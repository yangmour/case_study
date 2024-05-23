package com.xiwen.consumer;

import com.xiwen.dto.UserDTO;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.PartitionOffset;
import org.springframework.kafka.annotation.RetryableTopic;
import org.springframework.kafka.annotation.TopicPartition;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.retry.annotation.Backoff;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class KafkaListeners {


    /**
     * 简单消费：
     * topics：消费的主题列表
     * 接收消息的两种方式：
     * 1、记录对象
     * ConsumerRecord<String, String> record
     * 2、通过注解获取
     *
     * @Payload String data,
     * @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
     * @Header(KafkaHeaders.RECEIVED_PARTITION_ID) int partition,
     * @Header(KafkaHeaders.RECEIVED_MESSAGE_KEY) String key,
     * @Header(KafkaHeaders.RECEIVED_TIMESTAMP) long ts
     */
    @KafkaListener(topics = "spring_test_topic")
    public void simpleConsumer(ConsumerRecord<String, String> record) {
        this.logInfo(record);
    }



    @KafkaListener(
            topicPartitions = {
                    @TopicPartition(
                            topic = "spring_test_partition_topic",
                            //消费2分区所有消息
                            partitions = "2",
                            //指定消费的分区，并配置消费该分期的起始offset,注意partitions中配置的主题不能重复
                            partitionOffsets = {
                                    //分区0 offset从3开始消费
                                    @PartitionOffset(partition = "0", initialOffset = "6", relativeToCurrent = "true"),
                                    //分区3 offset从1开始消费
                                    @PartitionOffset(partition = "1", initialOffset = "0", relativeToCurrent = "true")
                            }
                    )
            },
            // 并发
            concurrency = "3"
    )
    public void consumeByPartitionOffsets(ConsumerRecord<String, String> record) {
        this.logInfo(record);
    }


    /**
     * 手动ack确认
     * @param record
     * @param ack
     */
    @KafkaListener(
            topics = "spring_test_ack_topic",
            //3个消费者
            concurrency = "3"
    )
    public void consumeByAck(ConsumerRecord<String, String> record, Acknowledgment ack) {
        logInfo(record);
        //手动ack
        ack.acknowledge();
    }

    @KafkaListener(
            topics = "spring_test_ack_topic_withExp",
            concurrency = "3",
            errorHandler = "listenerErrorHandler"
    )
    public void consumeByAckWithExp(ConsumerRecord<String, String> record, Acknowledgment ack) {
        logInfo(record);
        int i = 1/0;
        //手动ack
        ack.acknowledge();
    }


    /**
     * 消费实体
     * @param record
     * @param ack
     */
    @KafkaListener(
            topics = "spring_test_ack_topic_dto",
            concurrency = "3",
            errorHandler = "listenerErrorHandler"
    )
    public void consumeByAckDto(ConsumerRecord<String, UserDTO> record, Acknowledgment ack) {
        logInfo(record);
        //手动ack
        ack.acknowledge();
    }

    //attempts:重试的最大次数
//autoCreateTopics:指定是否自动创建重试主题和 DLT（死信主题）
//backoff: value 重试的时间间隔
    /**
     * 重试队列 "-retry";
     */
    /**
     * 私信队列 "-dlt";
     */
    @RetryableTopic(
            attempts = "3",
            backoff =@Backoff(delay = 2000L),
            autoCreateTopics ="true"
    )
    @KafkaListener(
            topics = {"spring_test_retry_topic", "spring_test_retry_topic"+"-retry-0"},
            //3个消费者
            concurrency = "3"
    )
    public void consumeByRetry(ConsumerRecord<String, UserDTO> record, Acknowledgment ack) {
        logInfo(record);
        int i = 1/0;
        //手动ack
        ack.acknowledge();
    }

    //死信队列默认名称在原队列后拼接'-dlt'
    @KafkaListener(
            topics = "spring_test_retry_topic-dlt",
            //1个消费者
            concurrency = "1"
    )
    public void consumeByDLT(ConsumerRecord<String, String> record, Acknowledgment ack) {
        logInfo(record);
        //手动ack
        ack.acknowledge();
    }

    /**
     * 日志信息
     *
     * @param record
     */
    private void logInfo(ConsumerRecord<String, ?> record) {
        log.info("分区 = {}, 偏移量 = {}, key = {}, 内容 = {}, 时间戳 = {}",
                record.partition(),
                record.offset(),
                record.key(),
                record.value(),
                record.timestamp()
        );
    }




}
