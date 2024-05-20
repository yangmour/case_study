package com.example.kafkaproducter.config;

import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.beans.factory.annotation.Configurable;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
@Slf4j
public class KafkaConfig {

    /**
     * 创建topic主题
     * @return
     */
    @Bean
    public NewTopic topic(){
        log.info("创建topic！==================================");
        return TopicBuilder.name("spring-test-topic")
                .partitions(3)  // 分区数
                .replicas(1) // 副本数
                .build();
    }
}
