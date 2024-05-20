package com.example.kafkaproducter.listener.kafka;

import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.springframework.kafka.support.ProducerListener;
import org.springframework.stereotype.Component;


@Component
@Slf4j
public class KafkaSendResultHandlerListener implements ProducerListener {

    /**
     * Kafka发送成功回调
     * @param producerRecord
     * @param recordMetadata
     */
    @Override
    public void onSuccess(ProducerRecord producerRecord, RecordMetadata recordMetadata) {
        String topic = producerRecord.topic();
        String value = producerRecord.value().toString();
        log.info("topic：{}，value：{}， 发送成功回调",topic,value);    }

    @Override
    public void onError(ProducerRecord producerRecord, RecordMetadata recordMetadata, Exception exception) {
        String topic = producerRecord.topic();
        String value = producerRecord.value().toString();
        log.info("topic：{}，value：{}， 发送失败，原因：{}",topic,value,exception.getMessage());
    }
}
