package com.xiwen.jwt_springsecuritydemo01.demos.nacosdiscoveryconsumer;

import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class RestTemplateConfig {

    // 微服务场景（通过服务名调用，如 http://nacos-service/echo）：必须加 @LoadBalanced
    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    // 非微服务场景（直接调用IP+端口）：可省略 @LoadBalanced
    // @Bean
    // public RestTemplate restTemplate() {
    //     return new RestTemplate();
    // }
}