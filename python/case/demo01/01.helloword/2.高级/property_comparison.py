# @property和@name.setter装饰器的作用对比

# 示例1：不使用@property装饰器（传统getter/setter方法）
class WithoutProperty:
    def __init__(self, value):
        self._value = value
    
    # 传统的getter方法
    def get_value(self):
        print("调用getter方法")
        return self._value
    
    # 传统的setter方法
    def set_value(self, value):
        print(f"调用setter方法，设置值为: {value}")
        # 可以添加验证逻辑
        if value < 0:
            raise ValueError("值不能为负数")
        self._value = value

# 示例2：使用@property装饰器
class WithProperty:
    def __init__(self, value):
        self._value = value
    
    # 使用@property定义getter
    @property
    def value(self):
        print("调用@property装饰的getter")
        return self._value
    
    # 使用@value.setter定义setter
    @value.setter
    def value(self, value):
        print(f"调用@value.setter装饰的setter，设置值为: {value}")
        # 可以添加验证逻辑
        if value < 0:
            raise ValueError("值不能为负数")
        self._value = value

# 示例3：只使用@property（只读属性）
class ReadOnlyProperty:
    def __init__(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value
    
    # 没有对应的setter方法，所以是只读属性

# 演示代码
if __name__ == "__main__":
    print("===== 装饰器作用对比示例 =====")
    
    # 示例1：不使用@property
    print("\n1. 不使用@property装饰器：")
    obj1 = WithoutProperty(10)
    obj1._value = 2
    # 必须显式调用方法
    print(f"获取值: {obj1._value}")
    obj1.set_value(20)
    print(f"修改后的值: {obj1.get_value()}")
    # 直接访问私有变量（不推荐但可行）
    print(f"直接访问私有变量: {obj1._value}")
    
    # 示例2：使用@property
    print("\n2. 使用@property装饰器：")
    obj2 = WithProperty(10)
    # 像访问普通属性一样使用
    print(f"获取值: {obj2.value}")
    obj2.value = 20  # 像赋值一样修改
    print(f"修改后的值: {obj2.value}")
    
    # 示例3：只读属性
    print("\n3. 只读属性（只有@property）：")
    obj3 = ReadOnlyProperty(10)
    print(f"获取只读属性值: {obj3.value}")
    try:
        obj3.value = 20  # 尝试修改只读属性
    except AttributeError as e:
        print(f"尝试修改只读属性错误: {e}")
    
    # 对比总结
    print("\n===== 装饰器作用总结 =====")
    print("1. @property不是可选的，而是提供了更优雅的属性访问方式")
    print("2. 使用@property的主要优势：")
    print("   - 代码更简洁优雅，符合Python风格")
    print("   - 可以像访问普通属性一样使用getter/setter方法")
    print("   - 保持了向后兼容性，隐藏了实现细节")
    print("   - 可以轻松将普通属性升级为带验证的属性")
    print("   - 可以创建只读属性")
    print("3. 不使用@property时：")
    print("   - 必须显式调用getter/setter方法")
    print("   - 代码不够直观，不符合Python的\"一致性\"原则")
    print("   - 无法防止直接访问私有变量")
    print("   - 无法轻松实现只读属性")
    print("\n结论：@property和@name.setter装饰器不是可有可无的，它们提供了更优雅、更安全的属性访问控制机制。")