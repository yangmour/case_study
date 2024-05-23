package com.xiwen.exception;

import com.alibaba.fastjson2.JSON;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.Consumer;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.listener.ConsumerAwareListenerErrorHandler;
import org.springframework.kafka.listener.ListenerExecutionFailedException;
import org.springframework.messaging.Message;

@Configuration
@Slf4j
public class CustomListenerErrorHandler{


    @Bean
    public ConsumerAwareListenerErrorHandler listenerErrorHandler(){
        return new ConsumerAwareListenerErrorHandler() {

            @Override
            public Object handleError(Message<?> message, ListenerExecutionFailedException exception, Consumer<?, ?> consumer) {
                System.out.println("--- 消费时发生异常 ---");
                log.info("message={}", JSON.toJSONString(message));
                log.warn("message.getPayload={}", message.getPayload());
                log.info("exception={}", JSON.toJSONString(exception.getMessage()));
                log.info("consumer={}", JSON.toJSONString(consumer));

                // 解析消息并转换为实体对象
                Object payload = message.getPayload();
                if (payload instanceof ConsumerRecord) {
                    ConsumerRecord<?, ?> consumerRecord = (ConsumerRecord<?, ?>) payload;
                    Object value = consumerRecord.value();
                    log.info("value={}", value);
                }



                return null;
            }
        };
    }

}