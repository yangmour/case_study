package com.xiwen.cloud;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@EnableEurekaServer
@SpringBootApplication
public class CloudEurekaServer7001Application {

    public static void main(String[] args) {
        SpringApplication.run(CloudEurekaServer7001Application.class, args);
    }

}
