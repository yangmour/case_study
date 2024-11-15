package com.xiwen.cloud;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
@MapperScan("com.xiwen.cloud.mapper")
public class CloudNacosProviderMovie6600Application {

    public static void main(String[] args) {
        SpringApplication.run(CloudNacosProviderMovie6600Application.class, args);
    }

}
