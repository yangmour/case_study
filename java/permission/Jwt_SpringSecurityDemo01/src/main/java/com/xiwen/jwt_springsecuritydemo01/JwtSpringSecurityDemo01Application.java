package com.xiwen.jwt_springsecuritydemo01;

import com.alibaba.cloud.nacos.NacosConfigAutoConfiguration;
import com.alibaba.cloud.nacos.discovery.NacosDiscoveryAutoConfiguration;
import com.alibaba.cloud.nacos.discovery.NacosDiscoveryClientConfiguration;
import com.alibaba.cloud.nacos.registry.NacosServiceRegistryAutoConfiguration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication(
        exclude = {
                // 核心：排除 Nacos 服务发现的自动配置类
                NacosDiscoveryAutoConfiguration.class,
                NacosServiceRegistryAutoConfiguration.class,
                NacosDiscoveryClientConfiguration.class,
                // 若涉及配置中心，也一并排除
                NacosConfigAutoConfiguration.class
        }
)
public class JwtSpringSecurityDemo01Application {

    public static void main(String[] args) {
        SpringApplication.run(JwtSpringSecurityDemo01Application.class, args);
    }

}
