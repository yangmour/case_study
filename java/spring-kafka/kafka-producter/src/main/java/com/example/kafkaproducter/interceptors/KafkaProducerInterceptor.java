package com.example.kafkaproducter.interceptors;

import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerInterceptor;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * 生产者拦截器
 */
@Component
@Slf4j
public class KafkaProducerInterceptor implements ProducerInterceptor<String, String> {
    private volatile long success = 0;
    private volatile long failure = 0;

    //消息发送前执行：可以对消息内容进行处理
    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> producerRecord) {

        log.info("即将发送的消息内容:{}", producerRecord.value());
        //此处可以修改producerRecord的属性值然后return
        return producerRecord;
    }

    //Kafka服务端应答后，应答到达生产者确认回调前执行
    @Override
    public void onAcknowledgement(RecordMetadata recordMetadata, Exception e) {
        if (null == e) {//成功
            success++;
        } else {//失败
            failure++;
        }
    }

    //拦截器销毁前执行
    @Override
    public void close() {
        log.info("消息发送统计,成功数量：{}，失败数量：{}，成功比例：{}",
                success, failure, (success * 1.0 / (success + failure)) * 100 + "%");
    }

    @Override
    public void configure(Map<String, ?> map) {

    }
}
