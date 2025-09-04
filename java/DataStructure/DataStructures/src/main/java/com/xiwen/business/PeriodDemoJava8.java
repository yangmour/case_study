package com.xiwen.business;

import com.xiwen.business.enums.TickCalculationStrategyEnum;
import com.xiwen.business.utils.GenericHashedWheelTimer;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class PeriodDemoJava8 {
    public static void main(String[] args) throws InterruptedException {
        // 1. 替换var：ExecutorService（线程池类型）
        ExecutorService executor = Executors.newFixedThreadPool(5);

        // -------------------------- 1. 分钟级任务（15分钟后执行） --------------------------
        System.out.println("=== 分钟级任务（15分钟后执行） ===");
        // 替换var：GenericHashedWheelTimer（时间轮实例类型）
        GenericHashedWheelTimer minuteTimer = new GenericHashedWheelTimer(
                1024,
                1000,  // 刻度间隔1秒
                executor,
                TickCalculationStrategyEnum.UPWARD_ROUNDING
        );
        minuteTimer.start();

        long minuteDelay = TimeUnit.MINUTES.toMillis(15);
        // 替换var：GenericHashedWheelTimer.TimerTask（任务实例类型，可省略，直接addTask）
        minuteTimer.addTask(() -> {
            System.out.printf("[订单取消] 执行时间：%s | 任务说明：15分钟未支付自动取消%n",
                    LocalDateTime.now());
        }, minuteDelay);

        TimeUnit.SECONDS.sleep(1);


        // -------------------------- 2. 小时级任务（3小时后执行） --------------------------
        System.out.println("\n=== 小时级任务（3小时后执行） ===");
        // 替换var：GenericHashedWheelTimer
        GenericHashedWheelTimer hourTimer = new GenericHashedWheelTimer(
                4096,
                10000, // 刻度间隔10秒
                executor,
                TickCalculationStrategyEnum.ROUND_HALF_UP
        );
        hourTimer.start();

        long hourDelay = TimeUnit.HOURS.toMillis(3);
        hourTimer.addTask(() -> {
            System.out.printf("[挽留消息] 执行时间：%s | 任务说明：登录3小时后推送优惠%n",
                    LocalDateTime.now());
        }, hourDelay);

        TimeUnit.SECONDS.sleep(1);


        // -------------------------- 3. 隔天任务（明天0点执行） --------------------------
        System.out.println("\n=== 隔天任务（明天0点执行） ===");
        // 替换var：GenericHashedWheelTimer
        GenericHashedWheelTimer dayTimer = new GenericHashedWheelTimer(
                8192,
                60000,  // 刻度间隔1分钟
                executor,
                TickCalculationStrategyEnum.UPWARD_ROUNDING
        );
        dayTimer.start();

        // 计算明天0点延迟（Java 8时区处理）
        LocalDateTime tomorrow0点 = LocalDateTime.now()
                .plusDays(1)
                .withHour(0)
                .withMinute(0)
                .withSecond(0)
                .withNano(0);
        // 替换var：ZoneOffset（时区偏移量类型）
        ZoneOffset zoneOffset = ZoneId.systemDefault().getRules().getOffset(LocalDateTime.now());
        long dayDelay = tomorrow0点.toInstant(zoneOffset).toEpochMilli() - System.currentTimeMillis();
        dayTimer.addTask(() -> {
            System.out.printf("[日报生成] 执行时间：%s | 任务说明：生成前一天交易报表%n",
                    LocalDateTime.now());
        }, dayDelay);

        TimeUnit.SECONDS.sleep(1);


        // -------------------------- 4. 隔月任务（下个月1号9点执行） --------------------------
        System.out.println("\n=== 隔月任务（下个月1号9点执行） ===");
        // 替换var：GenericHashedWheelTimer
        GenericHashedWheelTimer monthTimer = new GenericHashedWheelTimer(
                16384,  // 多槽位容纳长延时
                60000,  // 刻度间隔1分钟
                executor,
                TickCalculationStrategyEnum.UPWARD_ROUNDING
        );
        monthTimer.start();

        // 计算下个月1号9点延迟
        LocalDateTime nextMonth1号9点 = LocalDateTime.now()
                .plusMonths(1)
                .withDayOfMonth(1)
                .withHour(9)
                .withMinute(0)
                .withSecond(0)
                .withNano(0);
        long monthDelay = nextMonth1号9点.toInstant(zoneOffset).toEpochMilli() - System.currentTimeMillis();
        monthTimer.addTask(() -> {
            System.out.printf("[会员扣费] 执行时间：%s | 任务说明：扣除月度会员费%n",
                    LocalDateTime.now());
        }, monthDelay);

        System.out.println("\n所有任务已提交，等待执行...");
    }
}