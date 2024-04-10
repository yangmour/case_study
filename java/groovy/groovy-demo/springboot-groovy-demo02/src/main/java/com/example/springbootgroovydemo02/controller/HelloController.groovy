package com.example.springbootgroovydemo02.controller

import groovy.transform.CompileStatic
import groovy.util.logging.Slf4j
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@CompileStatic
@Slf4j
class HelloController {
    @RequestMapping("/hello/groovy")
    def hello(String name) {
        def s = "Hello " + name
        log.warn(s)
        s
    }
}
