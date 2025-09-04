package com.xiwen.business;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 通用时间轮定时器
 * 功能：管理大量延时任务，在指定延迟时间后执行
 * 特点：高效、通用、可扩展，不依赖任何消息队列
 */
public class GenericHashedWheelTimer {
    // 时间槽数组：可以想象成钟表上的刻度，每个刻度是一个槽
    private final WheelBucket[] buckets;

    // 时间槽数量：必须是2的幂（方便计算位置），类似钟表有12个刻度
    private final int bucketCount;

    // 每个时间槽的间隔（毫秒）：比如100ms，代表每个刻度之间的时间间隔
    private final long tickDuration;

    // 当前指针位置：类似钟表的指针，指向当前正在处理的刻度
    private final AtomicInteger currentIndex = new AtomicInteger(0);

    // 工作线程：负责推动指针前进并处理到期任务
    private final Thread workerThread;

    // 任务执行线程池：实际执行任务的地方，避免阻塞时间轮本身
    private final ExecutorService executor;

    // 定时器状态：标记时间轮是否正在运行
    private final AtomicBoolean started = new AtomicBoolean(false);

    // 启动信号量：确保工作线程准备好后才开始接收任务
    private final CountDownLatch startLatch = new CountDownLatch(1);

    // 任务移除监听器：当任务被取消时的回调（用于扩展场景）
    private TaskRemovalListener removalListener;

    /**
     * 构造函数：创建时间轮实例
     * @param bucketCount 时间槽数量（建议是2的幂，如1024）
     * @param tickDuration 每个时间槽的间隔（毫秒）
     * @param executor 执行任务的线程池
     */
    public GenericHashedWheelTimer(int bucketCount, long tickDuration, ExecutorService executor) {
        // 确保槽数量是2的幂（方便用位运算计算位置）
        this.bucketCount = bucketCount > 0 ? nextPowerOfTwo(bucketCount) : 1024;
        // 确保时间间隔为正数
        this.tickDuration = tickDuration > 0 ? tickDuration : 1;
        // 初始化所有时间槽
        this.buckets = new WheelBucket[this.bucketCount];
        for (int i = 0; i < this.bucketCount; i++) {
            this.buckets[i] = new WheelBucket();
        }
        // 初始化线程池（如果没提供则使用默认）
        this.executor = executor != null ? executor : Executors.newCachedThreadPool();
        // 创建工作线程
        this.workerThread = new Thread(new Worker(), "generic-time-wheel-worker");
    }

    /**
     * 简化构造函数：使用默认参数
     */
    public GenericHashedWheelTimer() {
        this(1024, 1, null);
    }

    /**
     * 启动时间轮
     */
    public void start() {
        // 用CAS确保只启动一次
        if (started.compareAndSet(false, true)) {
            workerThread.start();
            try {
                // 等待工作线程准备就绪
                startLatch.await();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    /**
     * 停止时间轮
     */
    public void stop() {
        // 用CAS确保只停止一次
        if (started.compareAndSet(true, false)) {
            // 中断工作线程
            workerThread.interrupt();
            try {
                // 等待工作线程结束
                workerThread.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            // 关闭线程池
            executor.shutdown();
        }
    }

    /**
     * 添加延时任务
     * @param task 要执行的任务
     * @param delayMs 延迟毫秒数
     * @return 任务对象（可用于取消任务）
     */
    public TimerTask addTask(Runnable task, long delayMs) {
        if (delayMs < 0) {
            throw new IllegalArgumentException("延迟时间不能为负数");
        }
        if (!started.get()) {
            throw new IllegalStateException("时间轮尚未启动");
        }

        // 创建任务对象
        TimerTask timerTask = new TimerTask(task, delayMs);
        // 调度任务到合适的时间槽
        scheduleTask(timerTask);
        return timerTask;
    }

    /**
     * 核心逻辑：将任务放到正确的时间槽
     */
    private void scheduleTask(TimerTask task) {
        // 计算剩余延迟时间
        long delayMs = task.getDelay(TimeUnit.MILLISECONDS);
        // 计算需要多少个时间槽间隔（ ticks = 总延迟 / 每个槽的时间 ）
        long ticks = delayMs / tickDuration;

        // 计算任务应该放入的槽位置：当前指针位置 + 需要的槽数，再对总槽数取模
        // 相当于钟表：现在指向3点，过5个小时后指向8点（3+5=8）
        long finalIndex = (currentIndex.get() + ticks) & (bucketCount - 1);

        // 计算需要多少轮：如果任务延迟很长，需要多轮才能到达
        // 比如钟表12个刻度，要36小时后执行，需要36/12=3轮
        long rounds = (ticks - 1) / bucketCount;

        // 设置任务的轮次和槽位置
        task.setRounds(rounds);
        buckets[(int) finalIndex].addTask(task);
    }

    /**
     * 设置任务移除监听器（用于扩展）
     */
    public void setTaskRemovalListener(TaskRemovalListener listener) {
        this.removalListener = listener;
    }

    /**
     * 工作线程：推动时间轮运转的核心
     */
    private class Worker implements Runnable {
        @Override
        public void run() {
            // 通知start()方法：工作线程已准备好
            startLatch.countDown();

            // 只要时间轮在运行，就一直循环
            while (started.get()) {
                try {
                    // 等待一个时间槽间隔（比如100ms）
                    TimeUnit.MILLISECONDS.sleep(tickDuration);
                } catch (InterruptedException e) {
                    // 如果是正常停止，就退出循环
                    if (!started.get()) {
                        return;
                    }
                    continue;
                }

                // 处理当前槽位的任务
                processCurrentBucket();
            }
        }

        /**
         * 处理当前指针指向的时间槽中的任务
         */
        private void processCurrentBucket() {
            // 计算当前槽位置（指针向前移动一位）
            int index = currentIndex.getAndIncrement() & (bucketCount - 1);
            WheelBucket bucket = buckets[index];

            // 处理这个槽中所有到期的任务
            for (TimerTask task : bucket.expireTasks()) {
                // 如果任务没被取消，就交给线程池执行
                if (!task.isCancelled()) {
                    executor.execute(task.getTask());
                }
            }
        }
    }

    /**
     * 计算大于等于n的最小2的幂（用于确保bucketCount是2的幂）
     * 比如n=5，返回8；n=8，返回8
     */
    private static int nextPowerOfTwo(int n) {
        return n <= 0 ? 1 : (n & -n) == n ? n : Integer.highestOneBit(n) << 1;
    }

    /**
     * 时间槽容器：每个槽存放一组任务
     */
    private class WheelBucket {
        // 用并发队列存储任务，确保线程安全
        private final ConcurrentLinkedQueue<TimerTask> tasks = new ConcurrentLinkedQueue<>();

        /**
         * 添加任务到当前槽
         */
        public void addTask(TimerTask task) {
            tasks.add(task);
        }

        /**
         * 获取当前槽中所有到期的任务
         */
        public Iterable<TimerTask> expireTasks() {
            // 存储到期的任务
            ConcurrentLinkedQueue<TimerTask> expired = new ConcurrentLinkedQueue<>();
            TimerTask task;

            // 遍历所有任务
            while ((task = tasks.poll()) != null) {
                if (task.getRounds() <= 0) {
                    // 轮次为0，说明已经到期，加入到期列表
                    expired.add(task);
                } else {
                    // 轮次减1，重新放回队列（还要再等一轮）
                    task.setRounds(task.getRounds() - 1);
                    tasks.add(task);
                }
            }
            return expired;
        }

        /**
         * 从槽中移除任务（用于取消任务）
         */
        public boolean removeTask(TimerTask task) {
            boolean removed = tasks.remove(task);
            if (removed && removalListener != null) {
                removalListener.onTaskRemoved(task);
            }
            return removed;
        }
    }

    /**
     * 延时任务封装类：包装用户任务和相关信息
     */
    public class TimerTask {
        private final Runnable task; // 用户实际要执行的任务
        private final long createTime; // 任务创建时间
        private final long delayMs; // 延迟毫秒数
        private volatile long rounds; // 还需要多少轮才执行
        private volatile boolean cancelled; // 任务是否已取消

        public TimerTask(Runnable task, long delayMs) {
            this.task = task;
            this.delayMs = delayMs;
            this.createTime = System.currentTimeMillis();
            this.rounds = 0;
            this.cancelled = false;
        }

        /**
         * 获取剩余延迟时间
         */
        public long getDelay(TimeUnit unit) {
            long elapsed = System.currentTimeMillis() - createTime;
            long remaining = delayMs - elapsed;
            return unit.convert(remaining, TimeUnit.MILLISECONDS);
        }

        public void setRounds(long rounds) {
            this.rounds = rounds;
        }

        public long getRounds() {
            return rounds;
        }

        public Runnable getTask() {
            return task;
        }

        /**
         * 取消任务
         */
        public boolean cancel() {
            if (cancelled) {
                return false;
            }
            cancelled = true;

            // 从所有槽中找到并移除这个任务
            for (WheelBucket bucket : buckets) {
                if (bucket.removeTask(this)) {
                    return true;
                }
            }
            return false;
        }

        public boolean isCancelled() {
            return cancelled;
        }
    }

    /**
     * 任务移除监听器接口（用于扩展场景）
     */
    @FunctionalInterface
    public interface TaskRemovalListener {
        void onTaskRemoved(TimerTask task);
    }
}
    