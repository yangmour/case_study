#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Python高级特性示例 - 面向Java开发者"""

# ======================== 1. 面向对象编程的高级特性 ========================#
# 与Java不同的是，Python支持多重继承、方法重写、属性装饰器等

class Animal:
    def __init__(self, name):
        self._name = name  # 使用下划线开头的私有变量
    
    def speak(self):
        raise NotImplementedError("子类必须实现此方法")

# 多重继承 - Java不支持多重继承，但Python支持
class Pet:
    def __init__(self, owner):
        self._owner = owner  # 使用下划线开头的私有变量

# 继承两个类
class Dog(Animal, Pet):
    # 构造方法
    def __init__(self, name, owner):
        # 注意：在Python中，我们不直接调用父类的__init__来初始化私有变量
        # 而是应该在子类中直接初始化这些私有变量
        self._name = name
        self._owner = owner
    
    def speak(self):
        return f"{self._name} says Woof!"

    # 静态方法 - 不需要实例化即可调用
    @staticmethod
    def get_type():
        return "Canine"
    
    # 类方法 - 可以访问类变量，相当于Java的static方法但有cls参数
    @classmethod
    def from_birth_year(cls, name, owner, birth_year):
        # 假设当前是2023年
        age = 2023 - birth_year
        return cls(name, owner)  # 创建实例
    
    # 属性装饰器 - 将方法转换为只读属性
    @property
    def description(self):
        return f"Dog named {self._name}, owned by {self._owner}"
    # 正确实现name属性 - 使用私有变量
    # @property
    # def name(self):
    #     return self._name  # 使用下划线开头的私有变量
    # @name.setter
    # def name(self, value):
    #     self._name = value  # 设置下划线开头的私有变量
    
    # # 正确实现owner属性 - 使用私有变量
    # @property
    # def owner(self):
    #     return self._owner  # 使用下划线开头的私有变量
    # @owner.setter
    # def owner(self, value):
    #     self._owner = value  # 设置下划线开头的私有变量

# 演示使用
if __name__ == "__main__":
    dog = Dog("Buddy", "Alice")
    print(dog.speak())
    print(dog.description)  # 注意这里不需要括号，直接访问属性
    print(Dog.get_type())  # 静态方法调用
    print(dog._name)  # 调用父类方法
    # print(dog.owner)  # 调用父类方法
    
# ======================== 2. 装饰器 - 类似Java的注解但更强大 ========================#
import time

# 装饰器函数定义
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 执行耗时: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

# 使用装饰器
@timing_decorator  # 相当于执行: slow_function = timing_decorator(slow_function)
def slow_function(seconds):
    time.sleep(seconds)
    return f"等待了 {seconds} 秒"

# 演示使用
# print(slow_function(1))

# ======================== 3. 生成器与迭代器 ========================#
# 生成器函数 - 使用yield语句返回值，可以暂停执行并保留状态
# 相当于Java中的迭代器模式，但更简洁

def fibonacci_generator(n):
    a, b = 0, 1
    for _ in range(n):
        yield a  # 暂停执行并返回值
        a, b = b, a + b

# 使用生成器
# for num in fibonacci_generator(10):
#     print(num, end=" ")
# print()

# 生成器表达式 - 更简洁的生成器写法，类似Java的Stream API
# squares = (x*x for x in range(10))
# for square in squares:
#     print(square, end=" ")

# ======================== 4. 上下文管理器 (with语句) ========================#
# 类似Java的try-with-resources语句，但更灵活

# 方法1: 使用类实现
class FileHandler:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        # 返回True表示异常已处理

# 方法2: 使用contextlib装饰器
from contextlib import contextmanager

@contextmanager
def file_handler(filename, mode):
    file = open(filename, mode)
    try:
        yield file  # 暂停执行，返回资源
    finally:
        file.close()

# 演示使用
# with file_handler("example.txt", "w") as f:
#     f.write("Hello, World!")

# ======================== 5. 异常处理的高级用法 ========================#

def divide_numbers(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("除数不能为零")
        return float('inf')  # 返回无穷大
    except TypeError as e:
        print(f"类型错误: {e}")
        return None
    else:
        # 没有异常时执行
        print(f"计算成功，结果: {result}")
        return result
    finally:
        # 无论是否有异常都会执行
        print("除法操作完成")

# 演示使用
# divide_numbers(10, 2)
# divide_numbers(10, 0)

# ======================== 6. 函数式编程 ========================#
# Python支持函数式编程范式

# Lambda函数 - 类似Java的lambda表达式
add = lambda x, y: x + y
# print(add(5, 3))

# 高阶函数 - 接受函数作为参数或返回函数
def apply_operation(func, x, y):
    return func(x, y)

# print(apply_operation(add, 4, 5))
# print(apply_operation(lambda x, y: x * y, 4, 5))

# 内置高阶函数
# map - 类似Java的Stream.map()
numbers = [1, 2, 3, 4, 5]
# squared = list(map(lambda x: x**2, numbers))
# print(squared)

# filter - 类似Java的Stream.filter()
# even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
# print(even_numbers)

# reduce - 需要从functools导入
from functools import reduce
# sum_result = reduce(lambda x, y: x + y, numbers)
# print(sum_result)

# ======================== 7. 多线程与多进程 ========================#
# 注意：Python的多线程由于GIL（全局解释器锁）的存在，在CPU密集型任务上无法真正利用多核
# 对于CPU密集型任务，应使用多进程

import threading
import multiprocessing

# 多线程示例
def print_numbers():
    for i in range(1, 6):
        print(f"数字: {i}")
        time.sleep(1)

def print_letters():
    for letter in "ABCDE":
        print(f"字母: {letter}")
        time.sleep(1)

# 演示多线程
# thread1 = threading.Thread(target=print_numbers)
# thread2 = threading.Thread(target=print_letters)
# thread1.start()
# thread2.start()
# thread1.join()
# thread2.join()

# 多进程示例
def square_number(num):
    return num * num

# 演示多进程
# if __name__ == "__main__":  # 多进程必须在main块中执行
#     with multiprocessing.Pool(processes=4) as pool:
#         results = pool.map(square_number, [1, 2, 3, 4, 5])
#     print(results)

# ======================== 8. 元编程 ========================#
# 动态修改类的行为

def add_method_to_class(cls):
    def new_method(self):
        return f"这是为{cls.__name__}动态添加的方法"
    
    # 动态添加方法到类
    setattr(cls, "new_method", new_method)

# 演示元编程
# class MyClass:
#     pass
# 
# add_method_to_class(MyClass)
# obj = MyClass()
# print(obj.new_method())

# ======================== 9. 模块和包 ========================#
# Python的模块系统与Java的包系统类似但有区别

# 导入模块的不同方式
# import math  # 导入整个模块
# from math import sqrt  # 导入特定函数
# from math import *  # 导入所有函数（不推荐）
# import math as m  # 导入模块并使用别名