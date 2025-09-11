//package com.xiwen.business;
//
//public class KafkaDelayPlugin {
//    private final GenericHashedWheelTimer timer;
//    private final KafkaProducer<String, String> producer;
//
//    public KafkaDelayPlugin() {
//        // 初始化时间轮
//        this.timer = new GenericHashedWheelTimer();
//        this.timer.setTaskRemovalListener(this::handleTaskRemoval);
//        this.timer.start();
//
//        // 初始化Kafka生产者
//        this.producer = new KafkaProducer<>(createKafkaConfig());
//    }
//
//    // 添加延时消息
//    public void sendDelayMessage(String topic, String key, String value, long delayMs) {
//        // 创建延时任务，到期后发送消息到目标主题
//        timer.addTask(() -> {
//            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);
//            producer.send(record);
//        }, delayMs);
//    }
//
//    // 处理任务移除（如消息被取消时的清理逻辑）
//    private void handleTaskRemoval(GenericHashedWheelTimer.TimerTask task) {
//        // 可以在这里记录日志或更新消息状态
//        System.out.println("延时任务被取消: " + task);
//    }
//
//    private Properties createKafkaConfig() {
//        Properties props = new Properties();
//        // 配置Kafka连接信息
//        props.put("bootstrap.servers", "localhost:9092");
//        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
//        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
//        return props;
//    }
//}