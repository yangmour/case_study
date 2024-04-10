package com.xiwen.serverdemoapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@ComponentScan(basePackages = {"com.xiwen.**"})
@SpringBootApplication
public class ServerDemoApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(ServerDemoApiApplication.class, args);
    }

}
