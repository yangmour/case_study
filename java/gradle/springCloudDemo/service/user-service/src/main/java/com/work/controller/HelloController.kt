package com.work.controller

import com.alibaba.fastjson2.JSON
import com.work.bean.GPerson
import com.work.bean.Person
import org.slf4j.LoggerFactory
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/kt")
class HelloController {
    private val log = LoggerFactory.getLogger(HelloController::class.java)
    @RequestMapping("hello")
    fun hello(): Any {
        val person: Person = Person()
        person.name = "王五"

        val gperson: GPerson = GPerson()
        gperson.name = "赵六"
        log.info("person={}", JSON.toJSONString(gperson))
        return JSON.toJSONString(gperson);
    }
}