package com.work.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;

@FeignClient(value = "name", url = "http://127.0.0.1:8080")
public interface DemoFeignClient {

    @GetMapping("java/hello")
    public String sayHello();
}
