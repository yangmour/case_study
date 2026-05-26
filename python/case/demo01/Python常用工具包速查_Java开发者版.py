#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python常用工具包速查手册 - 专为Java开发者准备
对比Java常用类库，快速掌握Python标准库和常用第三方库
"""

# ======================== 1. 字符串处理 ========================
# Java: String类、StringBuilder、StringUtils (Apache Commons)
# Python: str内置类型 + re模块

import re

print("=" * 60)
print("1. 字符串处理 - str & re")
print("=" * 60)

# 基本字符串操作
text = "  Hello, Python World!  "
print(f"原始字符串: '{text}'")
print(f"去除空格: '{text.strip()}'")  # Java: trim()
print(f"转小写: '{text.lower()}'")  # Java: toLowerCase()
print(f"转大写: '{text.upper()}'")  # Java: toUpperCase()
print(f"替换: '{text.replace('Python', 'Java')}'")  # Java: replace()
print(f"分割: {text.strip().split(',')}")  # Java: split()
print(f"连接: {'-'.join(['a', 'b', 'c'])}")  # Java: String.join()
print(f"判断开头: {text.strip().startswith('Hello')}")  # Java: startsWith()
print(f"判断结尾: {text.strip().endswith('!')}")  # Java: endsWith()
print(f"包含判断: {'Python' in text}")  # Java: contains()

# 字符串格式化（3种方式）
name, age = "张三", 25
print(f"\n格式化方式1 - f-string (推荐): {name}今年{age}岁")
print("格式化方式2 - format(): {}今年{}岁".format(name, age))
print("格式化方式3 - %格式化: %s今年%d岁" % (name, age))

# 正则表达式
pattern = r"\d+"  # 匹配数字
test_str = "订单号: 12345, 金额: 9999元"
print(f"\n正则匹配所有数字: {re.findall(pattern, test_str)}")  # Java: Pattern.compile()
print(f"正则替换: {re.sub(r'\d+', 'XXX', test_str)}")

# ======================== 2. 集合操作 ========================
# Java: List、Set、Map、Arrays、Collections
# Python: list、tuple、set、dict

print("\n" + "=" * 60)
print("2. 集合操作 - list, tuple, set, dict")
print("=" * 60)

# List（列表）- 类似Java的ArrayList
numbers = [1, 2, 3, 4, 5]
print(f"列表: {numbers}")
numbers.append(6)  # Java: list.add()
print(f"添加元素后: {numbers}")
numbers.remove(3)  # Java: list.remove()
print(f"删除元素3后: {numbers}")
print(f"列表长度: {len(numbers)}")  # Java: list.size()
print(f"排序: {sorted(numbers, reverse=True)}")  # Java: Collections.sort()
print(f"列表切片[1:3]: {numbers[1:3]}")  # Python特有

# 列表推导式（Python特色）- 类似Java Stream API
squares = [x**2 for x in range(1, 6)]
print(f"列表推导式: {squares}")

# Tuple（元组）- 不可变列表
coordinates = (10, 20)
print(f"\n元组（不可变）: {coordinates}")
# coordinates[0] = 15  # 会报错，元组不可修改

# Set（集合）- 类似Java的HashSet
unique_numbers = {1, 2, 3, 3, 4, 5, 5}
print(f"\n集合（自动去重）: {unique_numbers}")
set_a = {1, 2, 3}
set_b = {3, 4, 5}
print(f"交集: {set_a & set_b}")  # Java: set.retainAll()
print(f"并集: {set_a | set_b}")  # Java: set.addAll()
print(f"差集: {set_a - set_b}")  # Java: set.removeAll()

# Dict（字典）- 类似Java的HashMap
user = {"name": "张三", "age": 25, "city": "北京"}
print(f"\n字典: {user}")
print(f"获取值: {user['name']}")  # Java: map.get()
print(f"安全获取: {user.get('email', 'N/A')}")  # Java: map.getOrDefault()
user["email"] = "zhangsan@example.com"  # Java: map.put()
print(f"添加键值对后: {user}")
print(f"所有键: {list(user.keys())}")  # Java: map.keySet()
print(f"所有值: {list(user.values())}")  # Java: map.values()
print(f"所有项: {list(user.items())}")  # Java: map.entrySet()

# 字典推导式
squared_dict = {x: x**2 for x in range(1, 6)}
print(f"字典推导式: {squared_dict}")

# ======================== 3. 日期时间处理 ========================
# Java: java.util.Date、Calendar、LocalDateTime (Java 8+)
# Python: datetime、time

from datetime import datetime, timedelta
import time

print("\n" + "=" * 60)
print("3. 日期时间处理 - datetime & time")
print("=" * 60)

# 获取当前时间
now = datetime.now()
print(f"当前时间: {now}")
print(f"格式化输出: {now.strftime('%Y-%m-%d %H:%M:%S')}")  # Java: SimpleDateFormat

# 日期计算
tomorrow = now + timedelta(days=1)
print(f"明天: {tomorrow.strftime('%Y-%m-%d')}")
week_ago = now - timedelta(weeks=1)
print(f"一周前: {week_ago.strftime('%Y-%m-%d')}")

# 字符串解析为日期
date_str = "2024-01-15 14:30:00"
parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
print(f"解析日期: {parsed_date}")

# 时间戳
timestamp = time.time()
print(f"时间戳: {timestamp}")
print(f"从时间戳创建日期: {datetime.fromtimestamp(timestamp)}")

# ======================== 4. 文件IO操作 ========================
# Java: File、FileInputStream、BufferedReader、Files (Java 7+)
# Python: open()、pathlib

import os
from pathlib import Path

print("\n" + "=" * 60)
print("4. 文件IO操作 - open() & pathlib")
print("=" * 60)

# 写文件
filename = "test_output.txt"
with open(filename, 'w', encoding='utf-8') as f:  # Java: try-with-resources
    f.write("Hello, Python!\n")
    f.write("第二行内容\n")
print(f"已写入文件: {filename}")

# 读文件
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()
    print(f"文件内容:\n{content}")

# 按行读取
with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f"按行读取: {lines}")

# 使用pathlib（更现代的方式）
file_path = Path(filename)
print(f"\n文件是否存在: {file_path.exists()}")  # Java: Files.exists()
print(f"文件大小: {file_path.stat().st_size} 字节")  # Java: Files.size()

# 删除文件
if file_path.exists():
    file_path.unlink()
    print(f"已删除文件: {filename}")

# 目录操作
Path("temp_dir").mkdir(exist_ok=True)  # Java: Files.createDirectories()
print("已创建目录: temp_dir")
Path("temp_dir").rmdir()  # Java: Files.delete()
print("已删除目录: temp_dir")

# ======================== 5. JSON处理 ========================
# Java: Jackson、Gson、org.json
# Python: json (内置)

import json

print("\n" + "=" * 60)
print("5. JSON处理 - json")
print("=" * 60)

# Python对象转JSON
user_data = {
    "name": "张三",
    "age": 25,
    "skills": ["Python", "Java", "Django"],
    "active": True
}
json_str = json.dumps(user_data, ensure_ascii=False, indent=2)
print(f"对象转JSON:\n{json_str}")

# JSON转Python对象
parsed_data = json.loads(json_str)
print(f"JSON转对象: {parsed_data}")
print(f"访问属性: name={parsed_data['name']}, age={parsed_data['age']}")

# 读写JSON文件
json_file = "data.json"
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(user_data, f, ensure_ascii=False, indent=2)
print(f"\n已写入JSON文件: {json_file}")

with open(json_file, 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)
    print(f"从文件读取: {loaded_data}")

# 清理
Path(json_file).unlink()

# ======================== 6. HTTP请求 ========================
# Java: HttpURLConnection、Apache HttpClient、OkHttp
# Python: requests (第三方库，需要安装: pip install requests)

print("\n" + "=" * 60)
print("6. HTTP请求 - requests (需要安装: pip install requests)")
print("=" * 60)

try:
    import requests

    # GET请求
    response = requests.get('https://api.github.com')
    print(f"GET请求状态码: {response.status_code}")
    print(f"响应头: {dict(list(response.headers.items())[:3])}")  # 只显示前3个

    # POST请求
    data = {"key": "value"}
    # response = requests.post('https://httpbin.org/post', json=data)
    # print(f"POST请求结果: {response.json()}")

    print("\n常用方法:")
    print("- requests.get(url, params={}, headers={})")
    print("- requests.post(url, json={}, data={}, headers={})")
    print("- requests.put(url, json={})")
    print("- requests.delete(url)")
    print("- response.json()  # 解析JSON响应")
    print("- response.text    # 获取文本响应")
    print("- response.status_code  # 状态码")

except ImportError:
    print("requests库未安装，运行: pip install requests")

# ======================== 7. 数据库操作 ========================
# Java: JDBC、MyBatis、Hibernate、Spring Data JPA
# Python: sqlite3 (内置)、SQLAlchemy、Django ORM

import sqlite3

print("\n" + "=" * 60)
print("7. 数据库操作 - sqlite3 (内置)")
print("=" * 60)

# 连接数据库
conn = sqlite3.connect(':memory:')  # 内存数据库
cursor = conn.cursor()

# 创建表
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER
    )
''')
print("已创建表: users")

# 插入数据
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("张三", 25))
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("李四", 30))
conn.commit()
print("已插入2条数据")

# 查询数据
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print(f"查询结果: {rows}")

# 查询单条
cursor.execute("SELECT * FROM users WHERE name = ?", ("张三",))
user = cursor.fetchone()
print(f"单条查询: {user}")

# 关闭连接
conn.close()

# ======================== 8. 日志记录 ========================
# Java: Log4j、SLF4J、Logback
# Python: logging (内置)

import logging

print("\n" + "=" * 60)
print("8. 日志记录 - logging")
print("=" * 60)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# 不同级别的日志
logger.debug("这是DEBUG日志")  # Java: logger.debug()
logger.info("这是INFO日志")   # Java: logger.info()
logger.warning("这是WARNING日志")  # Java: logger.warn()
logger.error("这是ERROR日志")  # Java: logger.error()

# ======================== 9. 环境变量与配置 ========================
# Java: System.getenv()、Properties
# Python: os.environ

print("\n" + "=" * 60)
print("9. 环境变量 - os.environ")
print("=" * 60)

# 读取环境变量
home = os.environ.get('HOME', 'N/A')  # Java: System.getenv("HOME")
print(f"HOME环境变量: {home}")

# 设置环境变量（当前进程有效）
os.environ['MY_VAR'] = 'test_value'
print(f"自定义环境变量: {os.environ.get('MY_VAR')}")

# ======================== 10. 常用工具函数 ========================
# Java: Math、Random、Collections、Arrays
# Python: math、random、collections

import math
import random
from collections import Counter, defaultdict, OrderedDict

print("\n" + "=" * 60)
print("10. 常用工具 - math, random, collections")
print("=" * 60)

# 数学运算
print(f"圆周率: {math.pi}")
print(f"平方根: {math.sqrt(16)}")
print(f"幂运算: {math.pow(2, 3)}")
print(f"向上取整: {math.ceil(4.2)}")
print(f"向下取整: {math.floor(4.8)}")

# 随机数
print(f"\n随机整数[1,10]: {random.randint(1, 10)}")  # Java: Random.nextInt()
print(f"随机浮点数: {random.random()}")  # Java: Random.nextDouble()
print(f"随机选择: {random.choice(['a', 'b', 'c'])}")

# 集合工具
words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']
word_count = Counter(words)
print(f"\n计数器: {word_count}")
print(f"最常见的2个: {word_count.most_common(2)}")

# 默认字典
scores = defaultdict(int)  # 默认值为0
scores['math'] += 90
scores['english'] += 85
print(f"默认字典: {dict(scores)}")

print("\n" + "=" * 60)
print("学习建议")
print("=" * 60)
print("""
作为Java开发者学习Python工具包的建议:

1. 优先掌握内置库（无需安装）:
   - str, list, dict, set - 基础数据结构
   - datetime - 日期时间
   - json - JSON处理
   - os, pathlib - 文件系统
   - logging - 日志
   - re - 正则表达式

2. 必备第三方库（需pip安装）:
   - requests - HTTP请求（最常用）
   - pandas - 数据分析（类似Excel操作）
   - numpy - 数值计算
   - pytest - 单元测试

3. Django开发必备:
   - Django - Web框架
   - djangorestframework - REST API
   - celery - 异步任务
   - redis - 缓存

4. 学习方法:
   - 对比Java类库来理解Python库
   - 使用Python官方文档: https://docs.python.org/zh-cn/3/
   - 多动手实践，Python的交互式环境很适合测试代码

5. Python vs Java的核心差异:
   - Python动态类型，Java静态类型
   - Python简洁优雅，Java严谨冗长
   - Python适合快速开发，Java适合大型企业应用
   - Python标准库更丰富，"自带电池"
""")

print("\n运行此文件查看所有示例: python " + __file__)
