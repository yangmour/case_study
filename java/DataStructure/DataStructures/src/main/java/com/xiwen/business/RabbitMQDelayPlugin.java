//package com.xiwen.business;
//
//public class RabbitMQDelayPlugin {
//    private final GenericHashedWheelTimer timer;
//    private final RabbitTemplate rabbitTemplate;
//
//    public RabbitMQDelayPlugin(RabbitTemplate rabbitTemplate) {
//        this.timer = new GenericHashedWheelTimer();
//        this.timer.start();
//        this.rabbitTemplate = rabbitTemplate;
//    }
//
//    // 发送延时消息到RabbitMQ
//    public void sendDelayMessage(String exchange, String routingKey, Object message, long delayMs) {
//        timer.addTask(() -> {
//            rabbitTemplate.convertAndSend(exchange, routingKey, message);
//        }, delayMs);
//    }
//}