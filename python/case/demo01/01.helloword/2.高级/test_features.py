#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Python高级特性测试脚本 - 用于验证各个特性的功能"""

import sys
import os
import time

# 添加当前目录到Python路径，确保可以导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 测试标志
TEST_OOP = True
TEST_DECORATORS = True
TEST_GENERATORS = True
TEST_CONTEXT_MANAGERS = True
TEST_EXCEPTIONS = True
TEST_FUNCTIONAL = True
TEST_CONCURRENCY = False  # 可选测试，可能会影响输出
TEST_METAPROGRAMMING = True
TEST_MODULES = True

print("="*50)
print("Python高级特性测试脚本")
print("="*50)

# ======================== 测试面向对象编程 ========================#
if TEST_OOP:
    print("\n测试面向对象编程高级特性:")
    print("-"*30)
    
    class Animal:
        def __init__(self, name):
            self.name = name  # 实例变量，相当于Java的private成员变量
        
        def speak(self):
            raise NotImplementedError("子类必须实现此方法")
    
    class Pet:
        def __init__(self, owner):
            self.owner = owner
        
        def get_owner(self):
            return self.owner
    
    class Dog(Animal, Pet):
        def __init__(self, name, owner):
            Animal.__init__(self, name)
            Pet.__init__(self, owner)
        
        def speak(self):
            return f"{self.name} says Woof!"
        
        @staticmethod
        def get_type():
            return "Canine"
        
        @classmethod
        def from_birth_year(cls, name, owner, birth_year):
            age = 2023 - birth_year
            return cls(name, owner)
        
        @property
        def description(self):
            return f"Dog named {self.name}, owned by {self.owner}"
    
    # 创建实例并测试
    dog = Dog("Buddy", "Alice")
    print(f"1. 实例方法调用: {dog.speak()}")
    print(f"2. 属性装饰器: {dog.description}")
    print(f"3. 静态方法调用: {Dog.get_type()}")
    dog2 = Dog.from_birth_year("Max", "Bob", 2018)
    print(f"4. 类方法创建实例: {dog2.description}")

# ======================== 测试装饰器 ========================#
if TEST_DECORATORS:
    print("\n测试装饰器特性:")
    print("-"*30)
    
    def timing_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"  函数 {func.__name__} 执行耗时: {end_time - start_time:.4f} 秒")
            return result
        return wrapper
    
    @timing_decorator
    def slow_function(seconds):
        time.sleep(seconds)
        return f"等待了 {seconds} 秒"
    
    print("执行带装饰器的函数:")
    result = slow_function(0.5)  # 使用较短的等待时间便于测试
    print(f"  返回结果: {result}")

# ======================== 测试生成器 ========================#
if TEST_GENERATORS:
    print("\n测试生成器与迭代器特性:")
    print("-"*30)
    
    def fibonacci_generator(n):
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b
    
    print("1. 斐波那契数列生成器:")
    fib_list = list(fibonacci_generator(10))
    print(f"   前10个斐波那契数: {fib_list}")
    
    print("2. 生成器表达式:")
    squares = (x*x for x in range(5))
    print(f"   0-4的平方: {list(squares)}")

# ======================== 测试上下文管理器 ========================#
if TEST_CONTEXT_MANAGERS:
    print("\n测试上下文管理器特性:")
    print("-"*30)
    
    from contextlib import contextmanager
    
    @contextmanager
    def file_handler(filename, mode):
        print(f"  打开文件: {filename}")
        file = open(filename, mode)
        try:
            yield file
        finally:
            print(f"  关闭文件: {filename}")
            file.close()
    
    # 测试文件操作
    test_file = "test_context_manager.txt"
    print(f"使用上下文管理器操作文件 {test_file}:")
    with file_handler(test_file, "w") as f:
        f.write("Hello, Context Manager!")
        print("  文件写入完成")
    
    # 读取文件内容验证
    with file_handler(test_file, "r") as f:
        content = f.read()
        print(f"  文件内容: {content}")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"  清理测试文件: {test_file}")

# ======================== 测试异常处理 ========================#
if TEST_EXCEPTIONS:
    print("\n测试异常处理高级用法:")
    print("-"*30)
    
    def divide_numbers(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            print("  捕获到: 除数不能为零")
            return float('inf')
        except TypeError as e:
            print(f"  捕获到: 类型错误: {e}")
            return None
        else:
            print(f"  计算成功，结果: {result}")
            return result
        finally:
            print("  除法操作完成")
    
    print("测试场景1: 正常除法")
    divide_numbers(10, 2)
    
    print("\n测试场景2: 除以零")
    divide_numbers(10, 0)
    
    print("\n测试场景3: 类型错误")
    divide_numbers(10, "not a number")

# ======================== 测试函数式编程 ========================#
if TEST_FUNCTIONAL:
    print("\n测试函数式编程特性:")
    print("-"*30)
    
    # Lambda函数
    add = lambda x, y: x + y
    multiply = lambda x, y: x * y
    print(f"1. Lambda函数:")
    print(f"   5 + 3 = {add(5, 3)}")
    print(f"   5 * 3 = {multiply(5, 3)}")
    
    # 高阶函数
    def apply_operation(func, x, y):
        return func(x, y)
    
    print(f"2. 高阶函数:")
    print(f"   apply_operation(add, 4, 5) = {apply_operation(add, 4, 5)}")
    print(f"   apply_operation(lambda x,y: x**y, 2, 3) = {apply_operation(lambda x,y: x**y, 2, 3)}")
    
    # 内置高阶函数
    numbers = [1, 2, 3, 4, 5]
    
    # map
    squared = list(map(lambda x: x**2, numbers))
    print(f"3. map函数 - 平方: {squared}")
    
    # filter
    even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"4. filter函数 - 偶数: {even_numbers}")
    
    # reduce
    from functools import reduce
    sum_result = reduce(lambda x, y: x + y, numbers)
    print(f"5. reduce函数 - 求和: {sum_result}")

# ======================== 测试多线程与多进程 ========================#
if TEST_CONCURRENCY:
    print("\n测试多线程特性:")
    print("-"*30)
    
    import threading
    
    def print_numbers():
        for i in range(1, 4):
            print(f"  数字: {i}")
            time.sleep(0.3)
    
    def print_letters():
        for letter in "ABC":
            print(f"  字母: {letter}")
            time.sleep(0.3)
    
    # 创建并启动线程
    thread1 = threading.Thread(target=print_numbers)
    thread2 = threading.Thread(target=print_letters)
    
    print("启动多线程...")
    thread1.start()
    thread2.start()
    
    # 等待线程完成
    thread1.join()
    thread2.join()
    print("多线程执行完成")

# ======================== 测试元编程 ========================#
if TEST_METAPROGRAMMING:
    print("\n测试元编程特性:")
    print("-"*30)
    
    def add_method_to_class(cls):
        def new_method(self):
            return f"这是为{cls.__name__}动态添加的方法"
        
        # 动态添加方法到类
        setattr(cls, "new_method", new_method)
    
    # 定义一个简单的类
    class MyClass:
        pass
    
    # 动态添加方法
    print("动态向类添加方法:")
    add_method_to_class(MyClass)
    
    # 创建实例并调用动态添加的方法
    obj = MyClass()
    result = obj.new_method()
    print(f"  调用动态添加的方法: {result}")

# ======================== 测试模块导入 ========================#
if TEST_MODULES:
    print("\n测试模块和包特性:")
    print("-"*30)
    
    # 测试不同的导入方式
    print("1. 导入整个模块:")
    import math
    print(f"   math.pi = {math.pi}")
    
    print("2. 导入特定函数:")
    from math import sqrt
    print(f"   sqrt(16) = {sqrt(16)}")
    
    print("3. 使用别名导入:")
    import math as m
    print(f"   m.cos(m.pi) = {m.cos(m.pi)}")

print("\n" + "="*50)
print("所有测试完成！")
print("="*50)
print("\n提示：")
print("1. 您可以通过修改脚本顶部的TEST_*变量来启用或禁用特定的测试")
print("2. 所有的示例代码都保持在现有的文件夹结构中")
print("3. 详细的概念解释请参考同目录下的README.md文件")