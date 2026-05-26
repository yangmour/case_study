"""
数据处理与验证 - Django REST Framework必备技能

学习目标:
1. 掌握Pydantic数据验证
2. 理解Django REST Framework Serializer原理
3. 学习自定义验证器
4. 掌握数据序列化与反序列化
"""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import (
    BaseModel,
    Field,
    validator,
    root_validator,
    EmailStr,
    HttpUrl,
    constr,
    conint,
    ValidationError
)
from dataclasses import dataclass, field
import json


# ============================================
# 1. dataclasses - Python内置数据类
# ============================================

@dataclass
class Product:
    """
    商品数据类 - Python 3.7+
    类似Java的POJO, 自动生成__init__, __repr__, __eq__等方法
    """
    id: int
    name: str
    price: Decimal
    stock: int = 0  # 默认值
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)  # 工厂函数

    def __post_init__(self):
        """初始化后的验证"""
        if self.price < 0:
            raise ValueError("价格不能为负数")
        if self.stock < 0:
            raise ValueError("库存不能为负数")


def dataclass_demo():
    """dataclass基础示例"""
    print("\n" + "="*60)
    print("1. dataclass 基础示例")
    print("="*60)

    product = Product(
        id=1,
        name="iPhone 15 Pro",
        price=Decimal("7999.00"),
        stock=100
    )
    print(f"商品: {product}")
    print(f"名称: {product.name}, 价格: {product.price}")


# ============================================
# 2. Pydantic - 强大的数据验证库
# ============================================

class UserCreateRequest(BaseModel):
    """
    用户注册请求模型
    Pydantic会自动进行类型验证和数据转换
    """
    username: constr(min_length=3, max_length=20)  # 字符串长度限制
    email: EmailStr  # 邮箱格式验证
    password: constr(min_length=8)  # 密码最短8位
    age: conint(ge=18, le=120)  # 年龄: 18-120岁
    phone: Optional[str] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        """自定义验证: 用户名只能包含字母数字下划线"""
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @validator('password')
    def password_strength(cls, v):
        """密码强度验证"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "age": 25
            }
        }


class ProductModel(BaseModel):
    """
    商品模型 - 对应Django Model
    """
    id: Optional[int] = None  # 创建时不需要id
    name: str = Field(..., min_length=1, max_length=200, description="商品名称")
    price: Decimal = Field(..., gt=0, description="商品价格,必须大于0")
    stock: int = Field(default=0, ge=0, description="库存数量,不能为负")
    category: str = Field(..., description="商品分类")
    tags: List[str] = Field(default_factory=list, description="商品标签")
    on_sale: bool = Field(default=True, description="是否上架")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    @validator('price')
    def validate_price(cls, v):
        """价格验证: 保留两位小数"""
        return round(v, 2)

    @validator('tags')
    def validate_tags(cls, v):
        """标签验证: 去重并限制数量"""
        unique_tags = list(set(v))  # 去重
        if len(unique_tags) > 10:
            raise ValueError('标签数量不能超过10个')
        return unique_tags

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
            Decimal: lambda v: float(v)
        }


class OrderCreateRequest(BaseModel):
    """
    订单创建请求
    演示复杂对象验证和根验证器
    """
    user_id: int = Field(..., gt=0)
    items: List['OrderItemModel'] = Field(..., min_length=1)
    coupon_code: Optional[str] = None
    shipping_address: 'AddressModel'
    payment_method: str = Field(..., regex='^(alipay|wechat|card)$')  # 枚举验证

    @root_validator
    def validate_order(cls, values):
        """
        根验证器 - 验证多个字段之间的关系
        """
        items = values.get('items', [])
        total_amount = sum(item.price * item.quantity for item in items)

        # 订单金额限制
        if total_amount < Decimal('0.01'):
            raise ValueError('订单金额不能为0')
        if total_amount > Decimal('100000'):
            raise ValueError('单笔订单金额不能超过10万元')

        return values


class OrderItemModel(BaseModel):
    """订单商品项"""
    product_id: int = Field(..., gt=0)
    product_name: str
    price: Decimal = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=999)

    @property
    def subtotal(self) -> Decimal:
        """小计"""
        return self.price * self.quantity


class AddressModel(BaseModel):
    """收货地址"""
    province: str
    city: str
    district: str
    detail: str = Field(..., min_length=5)
    receiver: str
    phone: constr(regex=r'^1[3-9]\d{9}$')  # 手机号验证


# 更新前向引用
OrderCreateRequest.model_rebuild()


def pydantic_validation_demo():
    """Pydantic数据验证示例"""
    print("\n" + "="*60)
    print("2. Pydantic 数据验证")
    print("="*60)

    # 2.1 成功案例
    print("\n✓ 创建合法用户:")
    try:
        user = UserCreateRequest(
            username="john_doe",
            email="john@example.com",
            password="SecurePass123",
            age=25
        )
        print(f"  用户创建成功: {user.username}, {user.email}")
    except ValidationError as e:
        print(f"  验证失败: {e}")

    # 2.2 验证失败案例
    print("\n✗ 创建非法用户 (密码不符合要求):")
    try:
        user = UserCreateRequest(
            username="jane",
            email="jane@example.com",
            password="weak",  # 密码太弱
            age=20
        )
        print(f"  用户创建成功: {user.username}")
    except ValidationError as e:
        print(f"  验证失败:")
        for error in e.errors():
            print(f"    - {error['loc'][0]}: {error['msg']}")

    # 2.3 商品模型验证
    print("\n✓ 创建商品:")
    product = ProductModel(
        name="iPhone 15 Pro",
        price=Decimal("7999.99"),
        stock=100,
        category="电子产品",
        tags=["手机", "苹果", "5G", "手机", "苹果"]  # 有重复
    )
    print(f"  商品: {product.name}, 价格: {product.price}")
    print(f"  标签(已去重): {product.tags}")

    # 2.4 JSON序列化
    print("\n📦 JSON序列化:")
    product_json = product.model_dump_json(indent=2)
    print(product_json)

    # 2.5 JSON反序列化
    print("\n📦 JSON反序列化:")
    json_data = '{"name": "iPad Pro", "price": 6999, "stock": 50, "category": "平板电脑"}'
    product2 = ProductModel.model_validate_json(json_data)
    print(f"  商品: {product2.name}, 价格: {product2.price}")


# ============================================
# 3. 自定义验证器
# ============================================

class CustomValidator:
    """自定义验证器集合"""

    @static전method
    def validate_id_card(id_card: str) -> bool:
        """身份证号验证(简化版)"""
        if not id_card or len(id_card) != 18:
            return False
        return id_card[:17].isdigit() and (id_card[17].isdigit() or id_card[17].upper() == 'X')

    @staticmethod
    def validate_bank_card(card_number: str) -> bool:
        """银行卡号Luhn算法验证"""
        if not card_number or not card_number.isdigit():
            return False

        digits = [int(d) for d in card_number]
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0

    @staticmethod
    def validate_chinese_name(name: str) -> bool:
        """中文姓名验证"""
        if not name or len(name) < 2 or len(name) > 10:
            return False
        return all('\u4e00' <= char <= '\u9fff' for char in name)


class UserProfileModel(BaseModel):
    """用户资料 - 使用自定义验证器"""
    name: str
    id_card: str
    bank_card: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not CustomValidator.validate_chinese_name(v):
            raise ValueError('请输入有效的中文姓名(2-10个汉字)')
        return v

    @validator('id_card')
    def validate_id_card(cls, v):
        if not CustomValidator.validate_id_card(v):
            raise ValueError('请输入有效的18位身份证号')
        return v

    @validator('bank_card')
    def validate_bank_card(cls, v):
        if v and not CustomValidator.validate_bank_card(v):
            raise ValueError('请输入有效的银行卡号')
        return v


def custom_validator_demo():
    """自定义验证器示例"""
    print("\n" + "="*60)
    print("3. 自定义验证器")
    print("="*60)

    # 合法数据
    print("\n✓ 验证合法数据:")
    try:
        profile = UserProfileModel(
            name="张三",
            id_card="110101199001011234",  # 示例身份证号
            bank_card="6222600260001234567"  # 示例银行卡号
        )
        print(f"  资料创建成功: {profile.name}")
    except ValidationError as e:
        print(f"  验证失败: {e}")

    # 非法数据
    print("\n✗ 验证非法数据 (英文名):")
    try:
        profile = UserProfileModel(
            name="John",  # 非中文
            id_card="110101199001011234"
        )
    except ValidationError as e:
        for error in e.errors():
            print(f"  - {error['loc'][0]}: {error['msg']}")


# ============================================
# 4. Django REST Framework Serializer风格
# ============================================

class BaseSerializer:
    """
    模拟Django REST Framework的Serializer基类
    理解序列化器的工作原理
    """

    def __init__(self, data=None, instance=None):
        self.data = data
        self.instance = instance
        self._validated_data = None
        self._errors = None

    def is_valid(self, raise_exception=False):
        """验证数据"""
        try:
            self._validated_data = self.validate(self.data)
            self._errors = None
            return True
        except Exception as e:
            self._errors = {"error": str(e)}
            if raise_exception:
                raise
            return False

    def validate(self, data):
        """验证方法 - 子类需要实现"""
        return data

    @property
    def validated_data(self):
        """获取验证后的数据"""
        if self._validated_data is None:
            raise ValueError("请先调用 is_valid()")
        return self._validated_data

    @property
    def errors(self):
        """获取错误信息"""
        return self._errors or {}

    def save(self):
        """保存数据 - 子类需要实现"""
        raise NotImplementedError


class ProductSerializer(BaseSerializer):
    """
    商品序列化器 - Django风格
    """

    def validate(self, data):
        """数据验证"""
        # 必填字段检查
        required_fields = ['name', 'price', 'stock', 'category']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")

        # 类型和范围验证
        if not isinstance(data['price'], (int, float, Decimal)):
            raise ValueError("价格必须是数字")
        if data['price'] <= 0:
            raise ValueError("价格必须大于0")

        if not isinstance(data['stock'], int) or data['stock'] < 0:
            raise ValueError("库存必须是非负整数")

        return data

    def save(self):
        """保存商品 (模拟数据库操作)"""
        print(f"💾 保存商品: {self.validated_data['name']}")
        return {"id": 1, **self.validated_data}


def serializer_demo():
    """序列化器示例"""
    print("\n" + "="*60)
    print("4. Django风格序列化器")
    print("="*60)

    # 合法数据
    print("\n✓ 验证并保存商品:")
    serializer = ProductSerializer(data={
        "name": "MacBook Pro",
        "price": 12999.0,
        "stock": 50,
        "category": "电脑"
    })

    if serializer.is_valid():
        product = serializer.save()
        print(f"  商品已保存: {product}")
    else:
        print(f"  验证失败: {serializer.errors}")

    # 非法数据
    print("\n✗ 验证非法商品 (负价格):")
    serializer = ProductSerializer(data={
        "name": "测试商品",
        "price": -100,  # 负价格
        "stock": 10,
        "category": "测试"
    })

    if serializer.is_valid():
        product = serializer.save()
    else:
        print(f"  验证失败: {serializer.errors}")


# ============================================
# 5. 嵌套对象验证
# ============================================

class OrderValidator:
    """订单验证器 - 处理复杂嵌套结构"""

    @staticmethod
    def validate_order_data(order_data: dict) -> dict:
        """验证订单数据"""
        # 使用Pydantic模型验证
        try:
            order = OrderCreateRequest(**order_data)
            return order.model_dump()
        except ValidationError as e:
            raise ValueError(f"订单验证失败: {e}")


def nested_validation_demo():
    """嵌套对象验证示例"""
    print("\n" + "="*60)
    print("5. 嵌套对象验证")
    print("="*60)

    order_data = {
        "user_id": 123,
        "items": [
            {
                "product_id": 1,
                "product_name": "iPhone 15 Pro",
                "price": 7999.00,
                "quantity": 1
            },
            {
                "product_id": 2,
                "product_name": "AirPods Pro",
                "price": 1999.00,
                "quantity": 2
            }
        ],
        "shipping_address": {
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "detail": "科技园南区深南大道10000号",
            "receiver": "张三",
            "phone": "13800138000"
        },
        "payment_method": "alipay"
    }

    print("\n✓ 验证订单数据:")
    try:
        validated_order = OrderValidator.validate_order_data(order_data)
        print(f"  订单验证成功")
        print(f"  商品数量: {len(validated_order['items'])}")
        total = sum(item['price'] * item['quantity'] for item in validated_order['items'])
        print(f"  订单总额: ¥{total:.2f}")
    except ValueError as e:
        print(f"  验证失败: {e}")


# ============================================
# 主函数 - 运行所有示例
# ============================================

def main():
    """运行所有数据验证示例"""

    dataclass_demo()
    pydantic_validation_demo()
    custom_validator_demo()
    serializer_demo()
    nested_validation_demo()

    print("\n" + "="*60)
    print("✓ 所有数据验证示例执行完毕!")
    print("="*60)
    print("\n📚 关键要点总结:")
    print("  1. dataclass: Python内置数据类,简化数据对象定义")
    print("  2. Pydantic: 强大的数据验证库,Django REST Framework的最佳替代")
    print("  3. 自定义验证器: 使用@validator装饰器或自定义验证函数")
    print("  4. DRF Serializer: Django REST Framework的核心,用于数据序列化和验证")
    print("  5. 嵌套验证: 处理复杂对象关系,确保数据完整性")
    print("  6. 企业开发: 严格的数据验证是API安全的第一道防线")
    print("="*60)


if __name__ == "__main__":
    main()
