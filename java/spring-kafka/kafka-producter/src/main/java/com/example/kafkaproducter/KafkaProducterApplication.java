package com.example.kafkaproducter;

import com.example.kafkaproducter.interceptors.KafkaProducerInterceptor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.core.KafkaTemplate;

import javax.annotation.PostConstruct;
import javax.annotation.Resource;

@SpringBootApplication
@Slf4j
public class KafkaProducterApplication {

    @Resource
    KafkaTemplate<String,String> kafkaTemplate;
    @Resource
    KafkaProducerInterceptor kafkaProducerInterceptor;
    // 适用于3.*版本kafka，由于2.*版本拦截器有一些改变在yml中设置的
//    @PostConstruct
//    public void init() {
//        kafkaTemplate.setProducerInterceptor(kafkaProducerInterceptor);
//        log.info("----init success over,KafkaTemplate配置生产者拦截器kafkaProducerInterceptor");
//    }


    public static void main(String[] args) {
        SpringApplication.run(KafkaProducterApplication.class, args);
    }

}
