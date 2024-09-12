package com.work.springclouddemo.controller

import com.alibaba.fastjson2.JSON
import com.work.bean.GPerson
import groovy.util.logging.Slf4j
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("groovy")
@Slf4j
class GHelloController {

    @GetMapping("/hello")
    public Object hello(){
        GPerson person = new GPerson(name: "张三")
        log.info("person={}", JSON.toJSONString(person))
        return JSON.toJSONString(person);
    }
}
