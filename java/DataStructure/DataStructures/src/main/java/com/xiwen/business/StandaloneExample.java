package com.xiwen.business;

public class StandaloneExample {
    public static void main(String[] args) {
        int i = (150 + 50) / 100;
        int i2 = (140 + 50) / 100;
        System.out.println(i);
        System.out.println(i2);
    }
    public static void main2(String[] args) {
        // 创建时间轮实例
        GenericHashedWheelTimer timer = new GenericHashedWheelTimer();
        timer.start();
        
        // 添加5秒后执行的任务
        GenericHashedWheelTimer.TimerTask task1 = timer.addTask(() -> {
            System.out.println("5秒后执行的任务");
        }, 5000);
        
        // 添加10秒后执行的任务
        GenericHashedWheelTimer.TimerTask task2 = timer.addTask(() -> {
            System.out.println("10秒后执行的任务");
        }, 10000);
        
        // 可以取消任务
        // task2.cancel();
        
        // 程序运行一段时间后停止时间轮
        Runtime.getRuntime().addShutdownHook(new Thread(timer::stop));

    }
}