"""
并发编程 - 多线程/多进程/协程

学习目标:
1. 理解Python的GIL(全局解释器锁)
2. 掌握多线程、多进程、协程的使用场景
3. 学会使用线程池和进程池
4. 理解并发安全和锁机制
"""

import threading
import multiprocessing
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue
import os


# ============================================
# 1. GIL (全局解释器锁) 演示
# ============================================

def cpu_bound_task(n: int) -> int:
    """CPU密集型任务 - 计算质数"""
    count = 0
    for i in range(2, n):
        is_prime = True
        for j in range(2, int(i ** 0.5) + 1):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


def io_bound_task(url: str) -> str:
    """IO密集型任务 - 模拟网络请求"""
    time.sleep(1)  # 模拟IO等待
    return f"Downloaded {url}"


def demo_gil_impact():
    """演示GIL对多线程的影响"""
    print("\n" + "="*60)
    print("GIL影响演示 - CPU密集型任务")
    print("="*60)

    n = 100000

    # 单线程
    start = time.time()
    result = cpu_bound_task(n)
    single_time = time.time() - start
    print(f"单线程耗时: {single_time:.2f}秒, 质数个数: {result}")

    # 多线程 (受GIL影响,不会更快,可能更慢)
    start = time.time()
    threads = []
    for _ in range(2):
        t = threading.Thread(target=cpu_bound_task, args=(n//2,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    multi_thread_time = time.time() - start
    print(f"多线程耗时: {multi_thread_time:.2f}秒 (受GIL限制)")

    print(f"\n结论: CPU密集型任务使用多线程反而可能变慢(GIL的影响)")


# ============================================
# 2. 多线程 - 适合IO密集型任务
# ============================================

def threading_io_demo():
    """多线程处理IO密集型任务"""
    print("\n" + "="*60)
    print("多线程 - IO密集型任务")
    print("="*60)

    urls = [f"https://api.example.com/data/{i}" for i in range(5)]

    # 单线程
    start = time.time()
    for url in urls:
        io_bound_task(url)
    single_time = time.time() - start
    print(f"单线程耗时: {single_time:.2f}秒")

    # 多线程
    start = time.time()
    threads = []
    for url in urls:
        t = threading.Thread(target=io_bound_task, args=(url,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    multi_time = time.time() - start
    print(f"多线程耗时: {multi_time:.2f}秒")
    print(f"性能提升: {single_time / multi_time:.2f}倍")


# ============================================
# 3. 线程池 - ThreadPoolExecutor
# ============================================

def thread_pool_demo():
    """线程池示例"""
    print("\n" + "="*60)
    print("线程池 - ThreadPoolExecutor")
    print("="*60)

    urls = [f"https://api.example.com/product/{i}" for i in range(10)]

    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交任务
        futures = [executor.submit(io_bound_task, url) for url in urls]

        # 获取结果
        for future in as_completed(futures):
            result = future.result()
            print(f"  ✓ {result}")


# ============================================
# 4. 多进程 - 适合CPU密集型任务
# ============================================

def multiprocessing_demo():
    """多进程处理CPU密集型任务"""
    print("\n" + "="*60)
    print("多进程 - CPU密集型任务")
    print("="*60)

    n = 100000

    # 单进程
    start = time.time()
    result = cpu_bound_task(n)
    single_time = time.time() - start
    print(f"单进程耗时: {single_time:.2f}秒")

    # 多进程
    start = time.time()
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(cpu_bound_task, n//2) for _ in range(2)]
        results = [f.result() for f in futures]
    multi_time = time.time() - start
    print(f"多进程耗时: {multi_time:.2f}秒")
    print(f"性能提升: {single_time / multi_time:.2f}倍")


# ============================================
# 5. 线程安全 - 锁机制
# ============================================

class BankAccount:
    """银行账户 - 演示线程安全问题"""

    def __init__(self, balance: int):
        self.balance = balance
        self.lock = threading.Lock()  # 线程锁

    def deposit_unsafe(self, amount: int):
        """不安全的存款操作"""
        current_balance = self.balance
        time.sleep(0.001)  # 模拟处理延迟
        self.balance = current_balance + amount

    def deposit_safe(self, amount: int):
        """安全的存款操作(使用锁)"""
        with self.lock:
            current_balance = self.balance
            time.sleep(0.001)
            self.balance = current_balance + amount


def thread_safety_demo():
    """线程安全演示"""
    print("\n" + "="*60)
    print("线程安全 - 锁机制")
    print("="*60)

    # 不安全的操作
    account = BankAccount(0)
    threads = []
    for _ in range(100):
        t = threading.Thread(target=account.deposit_unsafe, args=(10,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(f"不安全操作: 预期余额1000, 实际余额{account.balance} (数据竞争)")

    # 安全的操作
    account = BankAccount(0)
    threads = []
    for _ in range(100):
        t = threading.Thread(target=account.deposit_safe, args=(10,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(f"安全操作: 预期余额1000, 实际余额{account.balance} ✓")


# ============================================
# 6. 生产者-消费者模式 (Queue)
# ============================================

def producer(queue: Queue, producer_id: int):
    """生产者"""
    for i in range(3):
        item = f"P{producer_id}-Item{i}"
        queue.put(item)
        print(f"  📦 生产者{producer_id} 生产: {item}")
        time.sleep(0.5)


def consumer(queue: Queue, consumer_id: int):
    """消费者"""
    while True:
        try:
            item = queue.get(timeout=2)
            print(f"  🔧 消费者{consumer_id} 消费: {item}")
            time.sleep(1)
            queue.task_done()
        except:
            break


def producer_consumer_demo():
    """生产者-消费者模式"""
    print("\n" + "="*60)
    print("生产者-消费者模式 (Queue)")
    print("="*60)

    queue = Queue(maxsize=10)

    # 启动生产者
    producers = []
    for i in range(2):
        t = threading.Thread(target=producer, args=(queue, i))
        t.start()
        producers.append(t)

    # 启动消费者
    consumers = []
    for i in range(3):
        t = threading.Thread(target=consumer, args=(queue, i))
        t.start()
        consumers.append(t)

    # 等待生产者完成
    for t in producers:
        t.join()

    # 等待队列处理完毕
    queue.join()

    # 等待消费者退出
    for t in consumers:
        t.join()


# ============================================
# 7. 协程 vs 线程对比
# ============================================

async def async_io_task(task_id: int):
    """异步IO任务"""
    print(f"  任务{task_id} 开始")
    await asyncio.sleep(1)
    print(f"  任务{task_id} 完成")
    return f"Task-{task_id}"


def coroutine_vs_thread_demo():
    """协程 vs 线程对比"""
    print("\n" + "="*60)
    print("协程 vs 线程性能对比")
    print("="*60)

    # 线程方式
    start = time.time()
    threads = []
    for i in range(100):
        t = threading.Thread(target=lambda: time.sleep(0.1))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    thread_time = time.time() - start
    print(f"100个线程耗时: {thread_time:.2f}秒")

    # 协程方式
    async def run_coroutines():
        tasks = [asyncio.sleep(0.1) for _ in range(100)]
        await asyncio.gather(*tasks)

    start = time.time()
    asyncio.run(run_coroutines())
    coroutine_time = time.time() - start
    print(f"100个协程耗时: {coroutine_time:.2f}秒")

    print(f"\n协程比线程快 {thread_time / coroutine_time:.2f}倍")
    print("原因: 协程开销极小,线程有创建和切换开销")


# ============================================
# 8. Django中的并发应用场景
# ============================================

def django_concurrency_scenarios():
    """Django中的并发应用场景"""
    print("\n" + "="*60)
    print("Django中的并发应用场景")
    print("="*60)

    scenarios = [
        ("Celery异步任务", "使用Celery+RabbitMQ处理耗时任务(发邮件、生成报表)"),
        ("异步视图", "Django 4.x的async def视图,处理并发API调用"),
        ("数据库连接池", "使用连接池管理数据库连接,提升并发性能"),
        ("缓存预热", "使用多线程批量预热Redis缓存"),
        ("批量导入", "使用多进程处理大文件导入"),
        ("消息队列", "RabbitMQ生产者-消费者模式处理订单"),
    ]

    for i, (title, desc) in enumerate(scenarios, 1):
        print(f"\n{i}. {title}")
        print(f"   {desc}")


# ============================================
# 主函数
# ============================================

def main():
    """运行所有并发编程示例"""

    demo_gil_impact()
    threading_io_demo()
    thread_pool_demo()
    multiprocessing_demo()
    thread_safety_demo()
    producer_consumer_demo()
    coroutine_vs_thread_demo()
    django_concurrency_scenarios()

    print("\n" + "="*60)
    print("✓ 所有并发编程示例执行完毕!")
    print("="*60)
    print("\n📚 关键要点总结:")
    print("  1. CPU密集型: 使用多进程 (绕过GIL)")
    print("  2. IO密集型: 使用多线程或协程")
    print("  3. 协程开销最小,适合高并发IO场景")
    print("  4. 使用锁保证线程安全")
    print("  5. 线程池/进程池复用资源,提升性能")
    print("  6. Django中主要使用Celery+异步视图+缓存")
    print("="*60)


if __name__ == "__main__":
    main()
