package com.example.springbootgroovydemo02.controller

import groovy.transform.CompileStatic
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.bind.annotation.RestController

@RestController
@CompileStatic
class HelloController {
    @RequestMapping("/hello/groovy")
    def hello(String name) {
        return "Hello " + name
    }
}
