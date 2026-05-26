"""
异步编程 (async/await) - Django高并发开发必备

学习目标:
1. 理解异步编程的核心概念
2. 掌握 async/await 语法
3. 使用 asyncio 进行异步IO操作
4. 理解异步在Django中的应用场景
"""

import asyncio
import time
from typing import List
import aiohttp
import aiofiles


# ============================================
# 1. 同步 vs 异步对比
# ============================================

def sync_sleep(name: str, seconds: int) -> str:
    """同步睡眠 - 会阻塞整个线程"""
    print(f"[同步] {name} 开始睡眠 {seconds} 秒")
    time.sleep(seconds)
    print(f"[同步] {name} 睡眠结束")
    return f"{name} 完成"


async def async_sleep(name: str, seconds: int) -> str:
    """异步睡眠 - 不会阻塞,可以切换到其他任务"""
    print(f"[异步] {name} 开始睡眠 {seconds} 秒")
    await asyncio.sleep(seconds)  # 让出控制权
    print(f"[异步] {name} 睡眠结束")
    return f"{name} 完成"


def compare_sync_vs_async():
    """对比同步和异步的性能差异"""
    print("=" * 50)
    print("同步执行 - 串行执行,总耗时 = 各任务耗时之和")
    print("=" * 50)
    start = time.time()
    sync_sleep("任务1", 2)
    sync_sleep("任务2", 2)
    sync_sleep("任务3", 2)
    print(f"总耗时: {time.time() - start:.2f}秒\n")

    print("=" * 50)
    print("异步执行 - 并发执行,总耗时 ≈ 最长任务耗时")
    print("=" * 50)
    start = time.time()
    asyncio.run(async_main())
    print(f"总耗时: {time.time() - start:.2f}秒\n")


async def async_main():
    """异步主函数 - 并发执行多个任务"""
    tasks = [
        async_sleep("任务1", 2),
        async_sleep("任务2", 2),
        async_sleep("任务3", 2),
    ]
    results = await asyncio.gather(*tasks)
    return results


# ============================================
# 2. 异步HTTP请求 - 模拟商城API调用
# ============================================

async def fetch_product(session: aiohttp.ClientSession, product_id: int) -> dict:
    """
    异步获取商品信息
    在Django微服务中,这是调用其他服务API的典型场景
    """
    # 模拟API地址
    url = f"https://jsonplaceholder.typicode.com/posts/{product_id}"

    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ 获取商品 {product_id} 成功")
                return {"product_id": product_id, "data": data}
            else:
                print(f"✗ 获取商品 {product_id} 失败: {response.status}")
                return {"product_id": product_id, "error": response.status}
    except Exception as e:
        print(f"✗ 获取商品 {product_id} 异常: {e}")
        return {"product_id": product_id, "error": str(e)}


async def fetch_multiple_products(product_ids: List[int]) -> List[dict]:
    """
    并发获取多个商品信息

    应用场景:
    - 商城首页需要展示多个商品
    - 订单详情需要查询多个商品信息
    - 推荐系统需要批量查询商品数据
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_product(session, pid) for pid in product_ids]
        results = await asyncio.gather(*tasks)
        return results


# ============================================
# 3. 异步文件IO - 日志写入场景
# ============================================

async def async_write_log(filename: str, content: str):
    """
    异步写入日志文件
    在高并发场景下,异步IO可以显著提升性能
    """
    async with aiofiles.open(filename, mode='a', encoding='utf-8') as f:
        await f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {content}\n")
        print(f"✓ 日志已写入: {content}")


async def batch_write_logs(logs: List[str]):
    """批量异步写入日志"""
    tasks = [async_write_log("app.log", log) for log in logs]
    await asyncio.gather(*tasks)


# ============================================
# 4. 异步数据库查询 (模拟)
# ============================================

async def async_query_user(user_id: int) -> dict:
    """
    模拟异步数据库查询
    实际项目中使用 databases 或 Django 4.1+ 的异步ORM
    """
    await asyncio.sleep(0.5)  # 模拟数据库查询延迟
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@example.com"
    }


async def async_query_order(order_id: int) -> dict:
    """模拟异步查询订单"""
    await asyncio.sleep(0.3)
    return {
        "order_id": order_id,
        "total_amount": 99.99,
        "status": "pending"
    }


async def get_user_order_details(user_id: int, order_id: int) -> dict:
    """
    并发查询用户和订单信息

    Django视图中的应用:
    async def order_detail_view(request, order_id):
        user_task = async_query_user(request.user.id)
        order_task = async_query_order(order_id)
        user, order = await asyncio.gather(user_task, order_task)
        return JsonResponse({"user": user, "order": order})
    """
    user_task = async_query_user(user_id)
    order_task = async_query_order(order_id)

    user, order = await asyncio.gather(user_task, order_task)

    return {
        "user": user,
        "order": order
    }


# ============================================
# 5. 异步上下文管理器
# ============================================

class AsyncDatabaseConnection:
    """
    异步数据库连接上下文管理器
    模拟Django中的数据库连接池
    """

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = None

    async def __aenter__(self):
        print(f"🔌 正在连接数据库: {self.db_name}")
        await asyncio.sleep(0.1)  # 模拟连接延迟
        self.connection = f"Connection<{self.db_name}>"
        print(f"✓ 数据库连接成功: {self.connection}")
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"🔌 正在关闭数据库连接: {self.connection}")
        await asyncio.sleep(0.1)  # 模拟关闭延迟
        self.connection = None
        print(f"✓ 数据库连接已关闭")


async def use_async_context_manager():
    """使用异步上下文管理器"""
    async with AsyncDatabaseConnection("mall_db") as conn:
        print(f"📊 使用连接进行查询: {conn}")
        await asyncio.sleep(0.2)


# ============================================
# 6. 异步生成器
# ============================================

async def async_product_generator(start: int, end: int):
    """
    异步生成器 - 用于流式处理大量数据

    应用场景:
    - 导出大量订单数据
    - 批量处理商品库存
    - 实时日志流处理
    """
    for product_id in range(start, end + 1):
        await asyncio.sleep(0.1)  # 模拟数据库查询
        yield {
            "product_id": product_id,
            "name": f"商品{product_id}",
            "price": 99.99 + product_id
        }


async def process_products_with_generator():
    """使用异步生成器处理商品"""
    print("\n使用异步生成器逐个处理商品:")
    async for product in async_product_generator(1, 5):
        print(f"  处理商品: {product}")


# ============================================
# 7. 异步队列 - 生产者消费者模式
# ============================================

async def producer(queue: asyncio.Queue, producer_id: int):
    """生产者 - 模拟订单生成"""
    for i in range(3):
        order = {"order_id": f"{producer_id}-{i}", "amount": 100 + i}
        await queue.put(order)
        print(f"📦 生产者{producer_id} 生成订单: {order['order_id']}")
        await asyncio.sleep(0.5)


async def consumer(queue: asyncio.Queue, consumer_id: int):
    """消费者 - 模拟订单处理"""
    while True:
        order = await queue.get()
        if order is None:  # 退出信号
            break
        print(f"🔧 消费者{consumer_id} 处理订单: {order['order_id']}")
        await asyncio.sleep(1)
        queue.task_done()


async def producer_consumer_demo():
    """
    生产者-消费者模式演示

    应用场景:
    - 订单处理系统
    - 消息队列处理
    - 任务调度系统
    """
    queue = asyncio.Queue(maxsize=10)

    # 启动2个生产者和3个消费者
    producers = [producer(queue, i) for i in range(2)]
    consumers = [consumer(queue, i) for i in range(3)]

    # 运行生产者
    await asyncio.gather(*producers)

    # 等待队列处理完毕
    await queue.join()

    # 发送退出信号
    for _ in consumers:
        await queue.put(None)

    # 等待消费者结束
    await asyncio.gather(*consumers)


# ============================================
# 8. 异步超时控制
# ============================================

async def slow_api_call():
    """模拟慢速API调用"""
    await asyncio.sleep(5)
    return "API响应数据"


async def timeout_demo():
    """
    异步超时控制

    应用场景:
    - 调用外部API时设置超时
    - 防止慢查询拖垮整个服务
    """
    try:
        result = await asyncio.wait_for(slow_api_call(), timeout=2.0)
        print(f"✓ API调用成功: {result}")
    except asyncio.TimeoutError:
        print("✗ API调用超时!")


# ============================================
# 9. Django中的异步视图 (示例代码)
# ============================================

"""
# Django 4.1+ 异步视图示例

from django.http import JsonResponse
import asyncio

# 异步视图函数
async def async_product_list(request):
    # 并发查询商品和分类
    products_task = Product.objects.all()  # Django 4.1+ 支持异步ORM
    categories_task = Category.objects.all()

    products, categories = await asyncio.gather(
        products_task,
        categories_task
    )

    return JsonResponse({
        "products": list(products),
        "categories": list(categories)
    })


# 异步类视图
from django.views import View

class AsyncOrderDetailView(View):
    async def get(self, request, order_id):
        # 并发查询订单和用户信息
        order = await Order.objects.filter(id=order_id).afirst()
        user = await User.objects.filter(id=order.user_id).afirst()

        return JsonResponse({
            "order": model_to_dict(order),
            "user": model_to_dict(user)
        })
"""


# ============================================
# 主函数 - 运行所有示例
# ============================================

async def main():
    """运行所有异步编程示例"""

    print("\n" + "="*60)
    print("1. 同步 vs 异步性能对比")
    print("="*60)
    compare_sync_vs_async()

    print("\n" + "="*60)
    print("2. 并发获取多个商品信息 (模拟微服务调用)")
    print("="*60)
    products = await fetch_multiple_products([1, 2, 3, 4, 5])
    print(f"成功获取 {len(products)} 个商品")

    print("\n" + "="*60)
    print("3. 并发查询用户和订单详情")
    print("="*60)
    details = await get_user_order_details(user_id=123, order_id=456)
    print(f"用户: {details['user']['username']}")
    print(f"订单: {details['order']['order_id']}")

    print("\n" + "="*60)
    print("4. 异步上下文管理器")
    print("="*60)
    await use_async_context_manager()

    print("\n" + "="*60)
    print("5. 异步生成器")
    print("="*60)
    await process_products_with_generator()

    print("\n" + "="*60)
    print("6. 异步超时控制")
    print("="*60)
    await timeout_demo()

    print("\n" + "="*60)
    print("7. 生产者-消费者模式 (订单处理)")
    print("="*60)
    await producer_consumer_demo()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())

    print("\n" + "="*60)
    print("✓ 所有异步编程示例执行完毕!")
    print("="*60)
    print("\n📚 关键要点总结:")
    print("  1. async/await 是Python异步编程的核心语法")
    print("  2. 异步适合IO密集型任务(网络请求、文件读写、数据库查询)")
    print("  3. 不适合CPU密集型任务(大量计算),应使用多进程")
    print("  4. Django 3.1+ 支持异步视图, 4.1+ 支持异步ORM")
    print("  5. 在微服务架构中,异步可以显著提升服务间调用性能")
    print("="*60)
