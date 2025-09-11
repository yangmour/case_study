package com.xiwen.business.时间轮.main;

import com.xiwen.business.时间轮.enums.TickCalculationStrategyEnum;
import com.xiwen.business.时间轮.utils.GenericHashedWheelTimer;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class TimerTaskListDemo {
    public static void main(String[] args) throws InterruptedException {
        // 初始化时间轮
        ExecutorService executor = Executors.newFixedThreadPool(5);
        GenericHashedWheelTimer timer = new GenericHashedWheelTimer(
                1024,
                1000, // 1秒刻度间隔
                executor,
                TickCalculationStrategyEnum.UPWARD_ROUNDING
        );
        timer.start();

        // 添加测试任务
        timer.addTask(() -> System.out.println("任务1执行"), 1000); // 1秒后执行
        timer.addTask(() -> System.out.println("任务2执行"), 3000); // 3秒后执行
        GenericHashedWheelTimer.TimerTask task3 = timer.addTask(() -> System.out.println("任务3执行"), 5000);
        task3.cancel(); // 取消任务3

        // 等待任务提交完成
        TimeUnit.SECONDS.sleep(1);


//        timer.loginfo(timer);

        // 关闭资源
//        timer.stop();
//        executor.shutdown();

    }

}