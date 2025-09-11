package com.xiwen.business.时间轮.utils;

import com.xiwen.business.时间轮.enums.TickCalculationStrategyEnum;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 通用时间轮定时器
 * 支持三种刻度计算策略（通过 TickCalculationStrategyEnum 枚举指定）
 */
public class GenericHashedWheelTimer {
    // 时间槽数组：钟表刻度对应的任务容器
    private final WheelBucket[] buckets;
    // 时间槽数量（2的幂，便于位运算计算位置）
    private final int bucketCount;
    // 每个刻度的时间间隔（毫秒）
    private final long tickDuration;
    // 当前指针位置（原子类确保线程安全）
    private final AtomicInteger currentIndex = new AtomicInteger(0);
    // 推动时间轮运转的工作线程
    private final Thread workerThread;
    // 执行任务的线程池（避免阻塞时间轮）
    private final ExecutorService executor;
    // 时间轮运行状态（原子类确保线程安全）
    private final AtomicBoolean started = new AtomicBoolean(false);
    // 启动信号量：确保工作线程就绪后再接收任务
    private final CountDownLatch startLatch = new CountDownLatch(1);
    // 任务移除监听器（扩展用）
    private TaskRemovalListener removalListener;

    // -------------------------- 关键修改：引用 TickCalculationStrategyEnum --------------------------
    // 默认计算策略：向上取整（符合多数关键业务“不提前”需求）
    private final TickCalculationStrategyEnum DEFAULT_STRATEGY = TickCalculationStrategyEnum.UPWARD_ROUNDING;
    // 当前使用的计算策略（支持外部指定）
    private TickCalculationStrategyEnum calculationStrategy;


    public static void loginfo(GenericHashedWheelTimer timer) {
        // 1. 查看所有任务
        List<GenericHashedWheelTimer.TimerTask> allTasks = timer.getAllTasks();
        System.out.println("=== 所有任务（共" + allTasks.size() + "个） ===");
        for (GenericHashedWheelTimer.TimerTask task : allTasks) {
            System.out.println(task.getTaskInfo());
        }

        // 2. 查看活跃任务（未取消）
        List<GenericHashedWheelTimer.TimerTask> activeTasks = timer.getActiveTasks();
        System.out.println("\n=== 活跃任务（共" + activeTasks.size() + "个） ===");
        for (GenericHashedWheelTimer.TimerTask task : activeTasks) {
            System.out.println(task.getTaskInfo());
        }

        // 3. 查看已取消任务
        List<GenericHashedWheelTimer.TimerTask> cancelledTasks = timer.getCancelledTasks();
        System.out.println("\n=== 已取消任务（共" + cancelledTasks.size() + "个） ===");
        for (GenericHashedWheelTimer.TimerTask task : cancelledTasks) {
            System.out.println(task.getTaskInfo());
        }
    }

    /**
     * 构造函数：全参数初始化（支持指定计算策略）
     * @param bucketCount 时间槽数量
     * @param tickDuration 刻度间隔（毫秒）
     * @param executor 任务线程池
     * @param strategy 刻度计算策略（传null则用默认）
     */
    public GenericHashedWheelTimer(int bucketCount, long tickDuration, ExecutorService executor, 
                                   TickCalculationStrategyEnum strategy) {
        // 确保槽数量为2的幂
        this.bucketCount = bucketCount > 0 ? nextPowerOfTwo(bucketCount) : 1024;
        // 确保刻度间隔为正数
        this.tickDuration = tickDuration > 0 ? tickDuration : 1;
        // 初始化时间槽
        this.buckets = new WheelBucket[this.bucketCount];
        for (int i = 0; i < this.bucketCount; i++) {
            this.buckets[i] = new WheelBucket();
        }
        // 初始化线程池（默认用CachedThreadPool）
        this.executor = executor != null ? executor : Executors.newCachedThreadPool();
        // 初始化工作线程
        this.workerThread = new Thread(new Worker(), "generic-time-wheel-worker");
        // 初始化计算策略（默认用向上取整）
        this.calculationStrategy = strategy != null ? strategy : DEFAULT_STRATEGY;
    }

    /**
     * 简化构造函数1：默认计算策略（向上取整）
     */
    public GenericHashedWheelTimer(int bucketCount, long tickDuration, ExecutorService executor) {
        this(bucketCount, tickDuration, executor, null);
    }

    /**
     * 简化构造函数2：全默认参数（1024槽、1ms间隔、默认线程池、向上取整）
     */
    public GenericHashedWheelTimer() {
        this(1024, 1, null, null);
    }

    /**
     * 简化构造函数3：仅指定计算策略（其他用默认）
     */
    public GenericHashedWheelTimer(TickCalculationStrategyEnum strategy) {
        this(1024, 1, null, strategy);
    }

    /**
     * 动态设置计算策略（需在时间轮启动前调用，避免并发问题）
     * @param strategy 新的计算策略
     */
    public void setCalculationStrategy(TickCalculationStrategyEnum strategy) {
        if (started.get()) {
            throw new IllegalStateException("时间轮已启动（started=true），无法修改计算策略（需在start()前设置）");
        }
        this.calculationStrategy = strategy != null ? strategy : DEFAULT_STRATEGY;
    }

    /**
     * 获取当前计算策略
     */
    public TickCalculationStrategyEnum getCalculationStrategy() {
        return calculationStrategy;
    }

    // -------------------------- 原有核心逻辑（仅修改刻度计算部分） --------------------------
    public void start() {
        if (started.compareAndSet(false, true)) {
            workerThread.start();
            try {
                startLatch.await(); // 等待工作线程就绪
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    public void stop() {
        if (started.compareAndSet(true, false)) {
            workerThread.interrupt();
            try {
                workerThread.join(); // 等待工作线程结束
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            executor.shutdown(); // 关闭线程池
        }
    }

    public TimerTask addTask(Runnable task, long delayMs) {
        if (delayMs < 0) {
            throw new IllegalArgumentException("延迟时间不能为负数（delayMs=" + delayMs + "）");
        }
        if (!started.get()) {
            throw new IllegalStateException("时间轮尚未启动，请先调用start()");
        }

        TimerTask timerTask = new TimerTask(task, delayMs);
        scheduleTask(timerTask); // 调度任务到对应时间槽
        return timerTask;
    }

    /**
     * 核心调度逻辑：使用 TickCalculationStrategyEnum 计算刻度
     */
    private void scheduleTask(TimerTask task) {
        // 1. 计算剩余延迟时间
        long delayMs = task.getDelay(TimeUnit.MILLISECONDS);
        // 2. 关键修改：通过枚举策略计算刻度数（替代原有的 delayMs / tickDuration）
        long ticks = calculationStrategy.calculateTicks(delayMs, tickDuration);

        // 3. 计算任务对应的时间槽位置（位运算取模，效率高于除法）
        long finalIndex = (currentIndex.get() + ticks) & (bucketCount - 1);
        // 4. 计算任务需要等待的轮次（长延时任务需多轮循环）
        long rounds = (ticks - 1) / bucketCount;

        // 5. 绑定任务的轮次和槽位，放入对应时间槽
        task.setRounds(rounds);
        buckets[(int) finalIndex].addTask(task);
    }

    // -------------------------- 原有内部类和工具方法（无修改） --------------------------
    public void setTaskRemovalListener(TaskRemovalListener listener) {
        this.removalListener = listener;
    }

    private class Worker implements Runnable {
        @Override
        public void run() {
            startLatch.countDown(); // 通知start()：工作线程已就绪
            while (started.get()) {
                try {
                    TimeUnit.MILLISECONDS.sleep(tickDuration); // 等待一个刻度间隔
                } catch (InterruptedException e) {
                    if (!started.get()) return; // 正常停止，退出循环
                    continue;
                } finally {
                    loginfo(GenericHashedWheelTimer.this);
                }
                processCurrentBucket(); // 处理当前刻度的任务
            }
        }

        private void processCurrentBucket() {
            int index = currentIndex.getAndIncrement() & (bucketCount - 1);
            WheelBucket bucket = buckets[index];
            for (TimerTask task : bucket.expireTasks()) {
                if (!task.isCancelled()) {
                    executor.execute(task.getTask()); // 执行到期任务
                }
            }
        }
    }

    private static int nextPowerOfTwo(int n) {
        return n <= 0 ? 1 : (n & -n) == n ? n : Integer.highestOneBit(n) << 1;
    }


    // -------------------------- 新增：任务查询相关方法 --------------------------
    /**
     * 获取所有任务（包括已取消和未取消的）
     * @return 所有任务列表
     */
    public List<TimerTask> getAllTasks() {
        List<TimerTask> allTasks = new ArrayList<>();
        // 遍历所有时间槽，收集所有任务
        for (WheelBucket bucket : buckets) {
            allTasks.addAll(bucket.getAllTasks());
        }
        return allTasks;
    }

    /**
     * 获取所有活跃任务（未被取消的）
     * @return 活跃任务列表
     */
    public List<TimerTask> getActiveTasks() {
        List<TimerTask> activeTasks = new ArrayList<>();
        for (WheelBucket bucket : buckets) {
            for (TimerTask task : bucket.getAllTasks()) {
                if (!task.isCancelled()) {
                    activeTasks.add(task);
                }
            }
        }
        return activeTasks;
    }

    /**
     * 获取所有已取消的任务
     * @return 已取消任务列表
     */
    public List<TimerTask> getCancelledTasks() {
        List<TimerTask> cancelledTasks = new ArrayList<>();
        for (WheelBucket bucket : buckets) {
            for (TimerTask task : bucket.getAllTasks()) {
                if (task.isCancelled()) {
                    cancelledTasks.add(task);
                }
            }
        }
        return cancelledTasks;
    }

    private class WheelBucket {
        private final ConcurrentLinkedQueue<TimerTask> tasks = new ConcurrentLinkedQueue<>();

        public void addTask(TimerTask task) {
            tasks.add(task);
        }

        public Iterable<TimerTask> expireTasks() {
            ConcurrentLinkedQueue<TimerTask> expired = new ConcurrentLinkedQueue<>();
            TimerTask task;
            while ((task = tasks.poll()) != null) {
                if (task.getRounds() <= 0) {
                    expired.add(task); // 轮次为0，任务到期
                } else {
                    task.setRounds(task.getRounds() - 1); // 轮次减1，放回队列
                    tasks.add(task);
                }
            }
            return expired;
        }

        public boolean removeTask(TimerTask task) {
            boolean removed = tasks.remove(task);
            if (removed && removalListener != null) {
                removalListener.onTaskRemoved(task);
            }
            return removed;
        }

        /**
         * 新增：获取当前槽中所有任务（用于外部查询）
         * @return 任务列表
         */
        public List<TimerTask> getAllTasks() {
            return new ArrayList<>(tasks); // 转换为ArrayList返回，避免并发修改异常
        }
    }

    public class TimerTask {
        private final Runnable task;
        private final long createTime;
        private final long delayMs;
        private volatile long rounds;
        private volatile boolean cancelled;

        public TimerTask(Runnable task, long delayMs) {
            this.task = task;
            this.delayMs = delayMs;
            this.createTime = System.currentTimeMillis();
            this.rounds = 0;
            this.cancelled = false;
        }

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

        public boolean cancel() {
            if (cancelled) return false;
            cancelled = true;
            for (WheelBucket bucket : buckets) {
                if (bucket.removeTask(this)) return true;
            }
            return false;
        }

        public boolean isCancelled() {
            return cancelled;
        }
        /**
         * 新增：获取任务详情（用于打印）
         */
        public String getTaskInfo() {
            return String.format(
                    "Task[创建时间=%d, 延迟=%dms, 剩余轮次=%d, 状态=%s]",
                    createTime,
                    delayMs,
                    rounds,
                    cancelled ? "已取消" : "活跃"
            );
        }
    }

    @FunctionalInterface
    public interface TaskRemovalListener {
        void onTaskRemoved(TimerTask task);
    }
}