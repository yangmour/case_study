package com.xiwen.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaInitConfig {
//    @Bean
//    public NewTopic springTestTopic2(){
//        return TopicBuilder.name("spring_test_topic") //主题名称
//                .partitions(3) //分区数量
//                .replicas(1) //副本数量
//                .build();
//    }
//
//
//    @Bean
//    public NewTopic springTestPartitionTopic(){
//        return TopicBuilder.name("spring_test_partition_topic") //主题名称
//                .partitions(3) //分区数量
//                .replicas(1) //副本数量
//                .build();
//    }
//
//    @Bean
//    public NewTopic springTestAckTopic(){
//        return TopicBuilder.name("spring_test_ack_topic") //主题名称
//                .partitions(3) //分区数量
//                .replicas(1) //副本数量
//                .build();
//    }
//
//    @Bean
//    public NewTopic springTestAckTopicWithExp(){
//        return TopicBuilder.name("spring_test_ack_topic_withExp") //主题名称
//                .partitions(3) //分区数量
//                .replicas(1) //副本数量
//                .build();
//    }
//
//    @Bean
//    public NewTopic springTestAckTopicDto(){
//        return TopicBuilder.name("spring_test_ack_topic_dto") //主题名称
//                .partitions(3) //分区数量
//                .replicas(1) //副本数量
//                .build();
//    }


    @Bean
    public NewTopic springTestRetryTopic(){
        return TopicBuilder.name("spring_test_retry_topic") //主题名称
                .partitions(3) //分区数量
                .replicas(1) //副本数量
                .build();
    }

}