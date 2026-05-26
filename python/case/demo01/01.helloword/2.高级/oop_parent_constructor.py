#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Python中调用父类构造函数的不同方法演示"""

print("="*50)
print("Python中调用父类构造函数的不同方法")
print("="*50)

# ======================== 1. 基本方式：显式调用每个父类的__init__ ========================#
print("\n1. 基本方式：显式调用每个父类的__init__方法")
print("-"*30)

class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Animal初始化: name = {name}")

class Pet:
    def __init__(self, owner):
        self.owner = owner
        print(f"Pet初始化: owner = {owner}")

class Dog1(Animal, Pet):
    def __init__(self, name, owner):
        # 当前代码中的写法：显式调用每个父类的构造函数
        Animal.__init__(self, name)  # 显式调用Animal的__init__
        Pet.__init__(self, owner)    # 显式调用Pet的__init__
        print(f"Dog1初始化完成")

# 测试基本方式
dog1 = Dog1("Buddy", "Alice")
print(f"Dog1实例属性: name={dog1.name}, owner={dog1.owner}")

# ======================== 2. 使用super()函数（Python 3推荐）========================#
print("\n2. 使用super()函数（单继承场景）")
print("-"*30)

class Animal2:
    def __init__(self, name):
        self.name = name
        print(f"Animal2初始化: name = {name}")

class Dog2(Animal2):
    def __init__(self, name, breed):
        # 使用super()调用父类构造函数（Python 3推荐写法）
        super().__init__(name)  # 等同于Animal2.__init__(self, name)
        self.breed = breed
        print(f"Dog2初始化: breed = {breed}")

# 测试super()函数（单继承）
dog2 = Dog2("Max", "Labrador")
print(f"Dog2实例属性: name={dog2.name}, breed={dog2.breed}")

# ======================== 3. super()在多继承中的应用 ========================#
print("\n3. super()在多继承中的应用")
print("-"*30)

class Animal3:
    def __init__(self, name):
        self.name = name
        print(f"Animal3初始化: name = {name}")

class Pet3:
    def __init__(self, owner):
        self.owner = owner
        print(f"Pet3初始化: owner = {owner}")

# 注意：这种方式在多继承中可能不会按预期工作
# super()会按照MRO（方法解析顺序）来调用父类方法
class Dog3(Animal3, Pet3):
    def __init__(self, name, owner):
        # 在多继承中，super()只会调用MRO中的下一个类的方法
        # 这里只会调用Animal3的__init__，不会调用Pet3的__init__
        super().__init__(name)
        # 需要显式调用Pet3的__init__
        Pet3.__init__(self, owner)
        print(f"Dog3初始化完成")

# 测试super()函数（多继承）
dog3 = Dog3("Charlie", "Bob")
print(f"Dog3实例属性: name={dog3.name}, owner={dog3.owner}")
print(f"Dog3的MRO（方法解析顺序）: {[cls.__name__ for cls in Dog3.__mro__]}")

# ======================== 4. 改进的多继承构造函数调用方式 ========================#
print("\n4. 改进的多继承构造函数调用方式")
print("-"*30)

# 更现代的多继承实现方式：所有父类的__init__都调用super()
class Base:
    def __init__(self):
        print("Base初始化")

class Animal4(Base):
    def __init__(self, name, **kwargs):
        self.name = name
        print(f"Animal4初始化: name = {name}")
        super().__init__(**kwargs)  # 调用下一个父类的__init__

class Pet4(Base):
    def __init__(self, owner, **kwargs):
        self.owner = owner
        print(f"Pet4初始化: owner = {owner}")
        super().__init__(**kwargs)  # 调用下一个父类的__init__

class Dog4(Animal4, Pet4):
    def __init__(self, name, owner):
        # 使用super()和关键字参数，让MRO机制处理所有父类的初始化
        # super().__init__(name=name, owner=owner)
        super().__init__(name=name, owner=owner)
        print(f"Dog4初始化完成")

# 测试改进的多继承方式
dog4 = Dog4("Rocky", "David")
print(f"Dog4实例属性: name={dog4.name}, owner={dog4.owner}")
print(f"Dog4的MRO（方法解析顺序）: {[cls.__name__ for cls in Dog4.__mro__]}")

# ======================== 5. Python 2.x兼容写法 ========================#
print("\n5. Python 2.x兼容写法（了解即可，现代Python不需要）")
print("-"*30)

# 这种写法在Python 2和Python 3中都能工作，但在Python 3中推荐使用更简洁的super()
class Dog5(Animal, Pet):
    def __init__(self, name, owner):
        # Python 2.x兼容写法
        super(Dog5, self).__init__(name)  # 指定当前类和self
        Pet.__init__(self, owner)
        print(f"Dog5初始化完成")

# 测试Python 2.x兼容写法
dog5 = Dog5("Rex", "Eve")
print(f"Dog5实例属性: name={dog5.name}, owner={dog5.owner}")

print("\n" + "="*50)
print("各种方法总结")
print("="*50)
print("1. 显式调用每个父类的__init__:")
print("   - 优点: 直观、明确，完全控制调用顺序")
print("   - 缺点: 代码冗长，当继承关系复杂时维护困难")
print("   - 适用场景: 多继承且需要严格控制父类初始化顺序")
print()
print("2. super()函数（单继承）:")
print("   - 优点: 代码简洁，符合Python 3推荐做法")
print("   - 缺点: 仅适用于单继承")
print("   - 适用场景: 单继承关系")
print()
print("3. super()函数结合显式调用（多继承）:")
print("   - 优点: 部分利用MRO机制，部分控制调用顺序")
print("   - 缺点: 仍需部分显式调用")
print("   - 适用场景: 简单的多继承关系")
print()
print("4. 改进的多继承构造函数调用方式:")
print("   - 优点: 完全利用MRO机制，代码简洁，可扩展性好")
print("   - 缺点: 需要所有父类配合使用super()和**kwargs")
print("   - 适用场景: 复杂的多继承关系")
print()
print("5. Python 2.x兼容写法:")
print("   - 优点: 兼容Python 2和3")
print("   - 缺点: 代码冗长")
print("   - 适用场景: 需要兼容Python 2的代码（现代Python开发不推荐）")
print()
print("提示: 对于Java开发者，Python的多继承机制与Java的接口实现有很大不同")
print("      在Python中，了解MRO（方法解析顺序）对正确使用super()非常重要")