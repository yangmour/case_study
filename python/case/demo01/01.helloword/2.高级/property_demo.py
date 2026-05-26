# Python @property装饰器使用示例

class Person:
    def __init__(self, name, age):
        # 私有变量（按约定以下划线开头）
        self._name = name
        self._age = age
    
    # 定义name属性的getter方法
    # @property
    def name(self):
        """获取姓名属性"""
        print("获取姓名...")
        return self._name
    
    # 定义name属性的setter方法
    # @name.setter
    def name(self, value):
        """设置姓名属性，进行验证"""
        print(f"设置姓名为: {value}")
        if not isinstance(value, str):
            raise TypeError("姓名必须是字符串类型")
        if not value.strip():
            raise ValueError("姓名不能为空")
        self._name = value
    
    # 定义age属性的getter方法
    @property
    def age(self):
        """获取年龄属性"""
        print("获取年龄...")
        return self._age
    
    # 定义age属性的setter方法
    @age.setter
    def age(self, value):
        """设置年龄属性，进行验证"""
        print(f"设置年龄为: {value}")
        if not isinstance(value, int):
            raise TypeError("年龄必须是整数类型")
        if value < 0 or value > 150:
            raise ValueError("年龄必须在0到150之间")
        self._age = value
    
    # 只读属性，没有对应的setter方法
    @property
    def is_adult(self):
        """判断是否成年，只读属性"""
        return self._age >= 18
    
    # 使用属性组合
    @property
    def introduction(self):
        """组合属性，返回个人介绍"""
        return f"我叫{self.name}，今年{self.age}岁。"

# 演示代码
if __name__ == "__main__":
    print("===== @property装饰器使用示例 =====")
    
    # 创建实例
    person = Person("张三", 25)
    
    # 使用getter方法访问属性（像访问普通属性一样）
    print(f"\n1. 访问属性:")
    print(f"姓名: {person.name}")
    print(f"年龄: {person.age}")
    print(f"是否成年: {person.is_adult}")
    print(f"个人介绍: {person.introduction}")
    
    # 使用setter方法修改属性（像修改普通属性一样）
    print(f"\n2. 修改属性:")
    person.name = "李四"
    person.age = 30
    print(f"修改后的姓名: {person.name}")
    print(f"修改后的年龄: {person.age}")
    print(f"修改后的个人介绍: {person.introduction}")
    
    # 尝试设置无效值（将触发验证错误）
    print(f"\n3. 错误示例:")
    try:
        person.age = -5
    except ValueError as e:
        print(f"年龄验证错误: {e}")
    
    try:
        person.name = ""  # 空字符串
    except ValueError as e:
        print(f"姓名验证错误: {e}")
    
    # 尝试修改只读属性（将引发错误）
    try:
        person.is_adult = True
    except AttributeError as e:
        print(f"只读属性错误: 不能修改只读属性")
    
    print(f"\n===== @property装饰器总结 =====")
    print("1. @property可以将方法转换为只读属性")
    print("2. @属性名.setter可以定义对应的setter方法")
    print("3. 可以在getter/setter中添加验证逻辑")
    print("4. 属性可以组合使用其他属性")
    print("5. 私有变量约定使用下划线开头")