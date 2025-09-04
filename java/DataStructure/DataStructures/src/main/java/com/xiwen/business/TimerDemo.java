package com.xiwen.business;

import com.xiwen.business.enums.TickCalculationStrategyEnum;
import com.xiwen.business.utils.GenericHashedWheelTimer;

import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class TimerDemo {
    public static void main(String[] args) throws InterruptedException {
        // -------------------------- 场景1：测试“四舍五入”策略（通用场景） --------------------------
        System.out.println("==================== 场景1：四舍五入策略测试 ====================");
        // 初始化时间轮：1024个槽、100ms刻度间隔、5线程池、四舍五入策略
        GenericHashedWheelTimer roundTimer = new GenericHashedWheelTimer(
                1024,
                100, // 刻度间隔100ms，方便观察偏差
                Executors.newFixedThreadPool(5),
                TickCalculationStrategyEnum.ROUND_HALF_UP
        );
        roundTimer.start();
        System.out.println("当前策略：" + roundTimer.getCalculationStrategy());
        System.out.println("策略说明：" + roundTimer.getCalculationStrategy().getScenarioDesc());

        // 添加3个不同延迟的任务（覆盖提前/延后边界）
        addTestTask(roundTimer, 50, "50ms延迟任务（四舍五入）");  // 50ms=刻度一半，会进位到100ms执行
        addTestTask(roundTimer, 99, "99ms延迟任务（四舍五入）");  // 超过一半，进位到100ms执行
        addTestTask(roundTimer, 140, "140ms延迟任务（四舍五入）"); // 140ms+50ms=190ms，190/100=1.9→2个刻度（200ms执行）

        // 等待任务执行完成（200ms任务是最长的，等300ms足够）
        TimeUnit.MILLISECONDS.sleep(300);
        roundTimer.stop(); // 停止时间轮，释放线程池
        System.out.println("---------------------------------------------------------\n");


        // -------------------------- 场景2：测试“向上取整”策略（关键任务，不允许提前） --------------------------
        System.out.println("==================== 场景2：向上取整策略测试 ====================");
        GenericHashedWheelTimer upwardTimer = new GenericHashedWheelTimer(
                1024,
                100,
                Executors.newFixedThreadPool(5),
                TickCalculationStrategyEnum.UPWARD_ROUNDING
        );
        upwardTimer.start();
        System.out.println("当前策略：" + upwardTimer.getCalculationStrategy());
        System.out.println("策略说明：" + upwardTimer.getCalculationStrategy().getScenarioDesc());

        // 添加任务（验证“绝对不提前”）
        addTestTask(upwardTimer, 1, "1ms延迟任务（向上取整）");    // 1ms+99ms=100ms→1个刻度（100ms执行，不提前）
        addTestTask(upwardTimer, 100, "100ms延迟任务（向上取整）");// 100ms+99ms=199ms→199/100=1.9→1个刻度（100ms执行）
        addTestTask(upwardTimer, 101, "101ms延迟任务（向上取整）");// 101ms+99ms=200ms→2个刻度（200ms执行）

        // 等待任务执行（最长200ms，等300ms）
        TimeUnit.MILLISECONDS.sleep(300);
        upwardTimer.stop();
        System.out.println("---------------------------------------------------------\n");


        // -------------------------- 场景3：测试“原始方式”策略（非关键任务，允许提前） --------------------------
        System.out.println("==================== 场景3：原始方式策略测试 ====================");
        GenericHashedWheelTimer originalTimer = new GenericHashedWheelTimer(
                1024,
                100,
                Executors.newFixedThreadPool(5),
                TickCalculationStrategyEnum.ORIGINAL
        );
        originalTimer.start();
        System.out.println("当前策略：" + originalTimer.getCalculationStrategy());
        System.out.println("策略说明：" + originalTimer.getCalculationStrategy().getScenarioDesc());

        // 添加任务（验证“可能提前”）
        addTestTask(originalTimer, 50, "50ms延迟任务（原始方式）");  // 50/100=0→0个刻度（立即执行，提前50ms）
        addTestTask(originalTimer, 99, "99ms延迟任务（原始方式）");  // 99/100=0→0个刻度（立即执行，提前99ms）
        addTestTask(originalTimer, 140, "140ms延迟任务（原始方式）"); // 140/100=1→1个刻度（100ms执行，提前40ms）

        // 等待任务执行（最长100ms，等200ms）
        TimeUnit.MILLISECONDS.sleep(200);
        originalTimer.stop();
        System.out.println("---------------------------------------------------------\n");


        // -------------------------- 场景4：任务取消示例（验证取消功能） --------------------------
        System.out.println("==================== 场景4：任务取消功能测试 ====================");
        GenericHashedWheelTimer cancelTimer = new GenericHashedWheelTimer(
                1024,
                100,
                Executors.newFixedThreadPool(5),
                TickCalculationStrategyEnum.UPWARD_ROUNDING
        );
        cancelTimer.start();

        // 添加任务并立即取消
        GenericHashedWheelTimer.TimerTask cancelTask = addTestTask(cancelTimer, 200, "200ms延迟任务（待取消）");
        boolean cancelSuccess = cancelTask.cancel();
        System.out.println("任务取消结果：" + (cancelSuccess ? "成功（任务不会执行）" : "失败（任务已执行或不存在）"));

        // 等待200ms，验证任务是否执行（取消成功则无输出）
        TimeUnit.MILLISECONDS.sleep(200);
        cancelTimer.stop();
    }

    /**
     * 工具方法：添加测试任务，打印任务执行信息（包含实际执行时间与预期的偏差）
     * @param timer 时间轮实例
     * @param delayMs 预期延迟时间（毫秒）
     * @param taskName 任务名称（用于区分）
     * @return 封装后的TimerTask（用于取消任务）
     */
    private static GenericHashedWheelTimer.TimerTask addTestTask(
            GenericHashedWheelTimer timer,
            long delayMs,
            String taskName
    ) {
        long taskCreateTime = System.currentTimeMillis(); // 任务创建时间（用于计算实际延迟）
        return timer.addTask(() -> {
            long actualDelay = System.currentTimeMillis() - taskCreateTime; // 实际延迟时间
            long deviation = actualDelay - delayMs; // 偏差（正值=延后，负值=提前）
            System.out.printf("[%s] 执行完成 | 预期延迟：%dms | 实际延迟：%dms | 偏差：%dms%n",
                    taskName, delayMs, actualDelay, deviation);
        }, delayMs);
    }
}