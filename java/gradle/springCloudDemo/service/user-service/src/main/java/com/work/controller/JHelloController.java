package com.work.controller;

import com.alibaba.fastjson2.JSON;
import com.work.bean.Person;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RequestMapping("java")
@RestController
public class JHelloController {
    @GetMapping("/hello")
    public Object hello() {
        Person person = new Person();
        person.setName("李四");

        return JSON.toJSONString(person);
    }
}
