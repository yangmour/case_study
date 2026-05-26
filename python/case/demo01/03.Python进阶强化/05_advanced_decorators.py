"""
装饰器进阶 - Django项目中最常用的技术

学习目标:
1. 深入理解装饰器的工作原理
2. 掌握带参数的装饰器
3. 理解装饰器链的执行顺序
4. 学习Django内置装饰器的实现原理
5. 自定义Django风格的装饰器
"""

import functools
import time
from typing import Callable, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# 1. 基础装饰器回顾
# ============================================

def simple_decorator(func: Callable) -> Callable:
    """最简单的装饰器"""
    @functools.wraps(func)  # 保留原函数的元数据
    def wrapper(*args, **kwargs):
        print(f"[装饰器] 调用函数: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[装饰器] 函数返回: {result}")
        return result
    return wrapper


@simple_decorator
def greet(name: str) -> str:
    """测试函数"""
    return f"Hello, {name}!"


# ============================================
# 2. 计时装饰器 - 性能监控
# ============================================

def timer(func: Callable) -> Callable:
    """
    性能计时装饰器
    应用场景: 监控API接口响应时间、数据库查询耗时
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"⏱️  {func.__name__} 耗时: {end_time - start_time:.4f}秒")
        return result
    return wrapper


@timer
def slow_query():
    """模拟慢查询"""
    time.sleep(1)
    return "查询结果"


# ============================================
# 3. 带参数的装饰器 - 重试机制
# ============================================

def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    重试装饰器
    应用场景: 调用外部API、数据库连接、网络请求
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"🔄 第 {attempt} 次尝试调用 {func.__name__}")
                    result = func(*args, **kwargs)
                    logger.info(f"✓ {func.__name__} 调用成功")
                    return result
                except Exception as e:
                    logger.warning(f"✗ 第 {attempt} 次失败: {e}")
                    if attempt == max_attempts:
                        logger.error(f"❌ {func.__name__} 达到最大重试次数")
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


# 模拟不稳定的API调用
attempt_count = 0


@retry(max_attempts=3, delay=0.5)
def unstable_api_call():
    """模拟不稳定的API,前两次失败,第三次成功"""
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise ConnectionError("网络连接失败")
    return {"status": "success", "data": "API数据"}


# ============================================
# 4. 缓存装饰器 - Django风格
# ============================================

def cache_result(expire_seconds: int = 60):
    """
    简单的内存缓存装饰器
    Django中使用: @cache_page(60) 或 Redis缓存
    """
    cache = {}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # 检查缓存
            if cache_key in cache:
                cached_time, cached_value = cache[cache_key]
                if time.time() - cached_time < expire_seconds:
                    logger.info(f"💾 命中缓存: {cache_key}")
                    return cached_value
                else:
                    logger.info(f"⏰ 缓存过期: {cache_key}")

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache[cache_key] = (time.time(), result)
            logger.info(f"📝 写入缓存: {cache_key}")
            return result

        return wrapper
    return decorator


@cache_result(expire_seconds=10)
@timer
def expensive_query(product_id: int):
    """模拟昂贵的数据库查询"""
    time.sleep(2)  # 模拟查询延迟
    return {"product_id": product_id, "name": f"商品{product_id}", "price": 99.99}


# ============================================
# 5. 权限校验装饰器 - Django风格
# ============================================

class User:
    """模拟Django User模型"""
    def __init__(self, username: str, is_authenticated: bool, is_admin: bool = False):
        self.username = username
        self.is_authenticated = is_authenticated
        self.is_admin = is_admin


def login_required(func: Callable) -> Callable:
    """
    登录验证装饰器
    Django: from django.contrib.auth.decorators import login_required
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 模拟从request中获取user
        user = kwargs.get('user')
        if not user or not user.is_authenticated:
            raise PermissionError("用户未登录,请先登录!")
        return func(*args, **kwargs)
    return wrapper


def admin_required(func: Callable) -> Callable:
    """
    管理员权限装饰器
    Django: from django.contrib.admin.views.decorators import staff_member_required
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get('user')
        if not user or not user.is_admin:
            raise PermissionError("需要管理员权限!")
        return func(*args, **kwargs)
    return wrapper


@login_required
@admin_required
def delete_product(product_id: int, user: User = None):
    """删除商品 - 需要登录+管理员权限"""
    return f"商品 {product_id} 已被管理员 {user.username} 删除"


# ============================================
# 6. 参数验证装饰器
# ============================================

def validate_params(**validators):
    """
    参数验证装饰器
    应用场景: API接口参数校验
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 验证参数
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if not validator(value):
                        raise ValueError(f"参数 {param_name} 验证失败: {value}")

            return func(*args, **kwargs)
        return wrapper
    return decorator


@validate_params(
    price=lambda x: x > 0,  # 价格必须大于0
    stock=lambda x: x >= 0,  # 库存不能为负
)
def create_product(name: str, price: float, stock: int):
    """创建商品"""
    return {"name": name, "price": price, "stock": stock}


# ============================================
# 7. 日志装饰器 - 记录函数调用
# ============================================

def log_calls(log_args: bool = True, log_result: bool = True):
    """
    日志装饰器
    应用场景: 调试、审计、监控
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 记录函数调用
            log_msg = f"📞 调用函数: {func.__name__}"
            if log_args:
                log_msg += f" | 参数: args={args}, kwargs={kwargs}"
            logger.info(log_msg)

            # 执行函数
            try:
                result = func(*args, **kwargs)
                if log_result:
                    logger.info(f"✓ 返回结果: {result}")
                return result
            except Exception as e:
                logger.error(f"❌ 函数异常: {e}")
                raise

        return wrapper
    return decorator


@log_calls(log_args=True, log_result=True)
def process_order(order_id: int, amount: float):
    """处理订单"""
    return {"order_id": order_id, "status": "success", "amount": amount}


# ============================================
# 8. 异步装饰器
# ============================================

import asyncio


def async_timer(func: Callable) -> Callable:
    """异步函数的计时装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"⏱️  [异步] {func.__name__} 耗时: {end_time - start_time:.4f}秒")
        return result
    return wrapper


@async_timer
async def async_fetch_data(url: str):
    """异步获取数据"""
    await asyncio.sleep(1)  # 模拟网络请求
    return f"从 {url} 获取的数据"


# ============================================
# 9. 类装饰器
# ============================================

class CountCalls:
    """
    类装饰器 - 统计函数调用次数
    应用场景: API限流、调用统计
    """

    def __init__(self, func: Callable):
        self.func = func
        self.count = 0
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        self.count += 1
        logger.info(f"📊 {self.func.__name__} 被调用第 {self.count} 次")
        return self.func(*args, **kwargs)


@CountCalls
def api_endpoint():
    """模拟API接口"""
    return {"status": "ok"}


# ============================================
# 10. 装饰器链 - 执行顺序
# ============================================

def decorator_a(func: Callable) -> Callable:
    """装饰器A"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("→ 进入装饰器A")
        result = func(*args, **kwargs)
        print("← 离开装饰器A")
        return result
    return wrapper


def decorator_b(func: Callable) -> Callable:
    """装饰器B"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("  → 进入装饰器B")
        result = func(*args, **kwargs)
        print("  ← 离开装饰器B")
        return result
    return wrapper


@decorator_a  # 最后执行 (外层)
@decorator_b  # 最先执行 (内层)
def my_function():
    """测试装饰器链执行顺序"""
    print("    → 执行原函数")
    return "结果"


# ============================================
# 11. Django真实装饰器示例
# ============================================

"""
# Django内置装饰器使用示例

from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.db import transaction

# 1. 登录验证
@login_required(login_url='/login/')
def user_profile(request):
    return render(request, 'profile.html')


# 2. 权限验证
@permission_required('products.can_delete', raise_exception=True)
def delete_product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return HttpResponse("删除成功")


# 3. HTTP方法限制
@require_http_methods(["GET", "POST"])
def product_list(request):
    if request.method == "GET":
        return render(request, 'products.html')
    elif request.method == "POST":
        # 创建商品
        pass


# 4. 缓存页面 (60秒)
@cache_page(60)
def homepage(request):
    return render(request, 'home.html')


# 5. 数据库事务
@transaction.atomic
def create_order(request):
    # 创建订单
    order = Order.objects.create(user=request.user)
    # 扣减库存
    product.stock -= 1
    product.save()
    # 如果发生异常,所有操作自动回滚


# 6. 多个装饰器组合
@login_required
@permission_required('orders.can_view')
@require_http_methods(["GET"])
@cache_page(30)
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order.html', {'order': order})
"""


# ============================================
# 12. 高级: 可选参数装饰器
# ============================================

def smart_decorator(func: Callable = None, *, prefix: str = ""):
    """
    支持 @smart_decorator 和 @smart_decorator(prefix="...") 两种用法
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print(f"{prefix}调用 {f.__name__}")
            return f(*args, **kwargs)
        return wrapper

    if func is None:
        # @smart_decorator(prefix="...")
        return decorator
    else:
        # @smart_decorator
        return decorator(func)


@smart_decorator
def func1():
    return "测试1"


@smart_decorator(prefix="[DEBUG] ")
def func2():
    return "测试2"


# ============================================
# 主函数 - 运行所有示例
# ============================================

def main():
    """运行所有装饰器示例"""

    print("\n" + "="*60)
    print("1. 基础装饰器")
    print("="*60)
    result = greet("张三")
    print(f"结果: {result}\n")

    print("="*60)
    print("2. 计时装饰器 - 性能监控")
    print("="*60)
    slow_query()

    print("\n" + "="*60)
    print("3. 重试装饰器 - 错误恢复")
    print("="*60)
    global attempt_count
    attempt_count = 0  # 重置计数器
    try:
        result = unstable_api_call()
        print(f"API调用成功: {result}")
    except Exception as e:
        print(f"API调用失败: {e}")

    print("\n" + "="*60)
    print("4. 缓存装饰器 - 性能优化")
    print("="*60)
    print("首次查询 (慢):")
    expensive_query(101)
    print("\n第二次查询 (命中缓存):")
    expensive_query(101)

    print("\n" + "="*60)
    print("5. 权限装饰器 - 访问控制")
    print("="*60)
    admin_user = User("admin", is_authenticated=True, is_admin=True)
    normal_user = User("user1", is_authenticated=True, is_admin=False)

    try:
        print("管理员删除商品:")
        result = delete_product(123, user=admin_user)
        print(f"  ✓ {result}")
    except PermissionError as e:
        print(f"  ✗ {e}")

    try:
        print("普通用户删除商品:")
        result = delete_product(123, user=normal_user)
        print(f"  ✓ {result}")
    except PermissionError as e:
        print(f"  ✗ {e}")

    print("\n" + "="*60)
    print("6. 参数验证装饰器")
    print("="*60)
    try:
        print("创建合法商品:")
        product = create_product("iPhone", price=5999.0, stock=100)
        print(f"  ✓ {product}")
    except ValueError as e:
        print(f"  ✗ {e}")

    try:
        print("创建非法商品 (负价格):")
        product = create_product("iPhone", price=-100.0, stock=100)
        print(f"  ✓ {product}")
    except ValueError as e:
        print(f"  ✗ {e}")

    print("\n" + "="*60)
    print("7. 日志装饰器")
    print("="*60)
    process_order(order_id=1001, amount=299.99)

    print("\n" + "="*60)
    print("8. 类装饰器 - 调用计数")
    print("="*60)
    for i in range(3):
        api_endpoint()

    print("\n" + "="*60)
    print("9. 装饰器链执行顺序")
    print("="*60)
    my_function()

    print("\n" + "="*60)
    print("10. 可选参数装饰器")
    print("="*60)
    func1()
    func2()

    print("\n" + "="*60)
    print("11. 异步装饰器")
    print("="*60)
    asyncio.run(async_fetch_data("https://api.example.com"))


if __name__ == "__main__":
    main()

    print("\n" + "="*60)
    print("✓ 所有装饰器示例执行完毕!")
    print("="*60)
    print("\n📚 关键要点总结:")
    print("  1. 使用 @functools.wraps 保留原函数元数据")
    print("  2. 带参数的装饰器需要三层嵌套函数")
    print("  3. 装饰器链从下到上执行(最接近函数的最先执行)")
    print("  4. Django大量使用装饰器: 权限、缓存、事务、HTTP方法限制")
    print("  5. 装饰器常用场景: 日志、计时、重试、缓存、权限、参数验证")
    print("="*60)
