package com.xiwen.juc.day02.locktest;

import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Description:
 *
 * @author: yf
 * @Create: 2023/07/01 -16:41
 * @Version: 1.0
 */
class ShareDataOne {
    private Integer number = 0;

    /**
     * 增1
     */
    public synchronized void increment() throws InterruptedException {

        // 等于1 开始堵塞
        while (number != 0) {
            this.wait();
        }
        // 开始生产
        number++;
        System.out.println(Thread.currentThread().getName() + "生产:" + number);

        // 通知其他线程
        this.notifyAll();
    }

    /**
     * 减1
     */
    public synchronized void decrement() throws InterruptedException {
        // 等于0 开始堵塞
        while (number != 1) {
            this.wait();
        }
        // 开始消费
        number--;
        System.out.println(Thread.currentThread().getName() + "消费:" + number);

        //通知其他线程
        this.notifyAll();
    }

}

class ShareDataOne2 {
    private Integer number = 0;
    // 锁
    private final Lock lock = new ReentrantLock();
    // 配一把钥匙
    private Condition condition = lock.newCondition();

    /**
     * 增1
     */
    public void increment() throws InterruptedException {
        lock.lock();
        // 等于1 开始堵塞
        while (number != 0) {
            condition.await();
        }
        // 开始生产
        number++;
        System.out.println(Thread.currentThread().getName() + "生产:" + number);

        // 通知其他线程
        condition.signalAll();
        lock.unlock();
    }

    /**
     * 减1
     */
    public void decrement() throws InterruptedException {
        lock.lock();
        // 等于0 开始堵塞
        while (number != 1) {
            condition.await();
        }
        // 开始消费
        number--;
        System.out.println(Thread.currentThread().getName() + "消费:" + number);

        //通知其他线程
        condition.signalAll();
        lock.unlock();

    }

}

public class NotifyWaitDemo {

    public static void main(String[] args) {
        //	两个线程操作一个初始值为0的变量，实现一个线程对变量增加1，一个线程对变量减少1，交替10轮。
//        ShareDataOne shareDataOne = new ShareDataOne();
        ShareDataOne2 shareDataOne = new ShareDataOne2();

        int size = 10;

        new Thread(() -> {
            for (int i = 0; i < size; i++) {

                try {
                    shareDataOne.increment();
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        }, "A").start();

        new Thread(() -> {
            for (int i = 0; i < size; i++) {

                try {
                    shareDataOne.decrement();
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        }, "B").start();

        new Thread(() -> {
            for (int i = 0; i < size; i++) {

                try {
                    shareDataOne.increment();
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        }, "C").start();

        new Thread(() -> {
            for (int i = 0; i < size; i++) {

                try {
                    shareDataOne.decrement();
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        }, "D").start();


    }
}
