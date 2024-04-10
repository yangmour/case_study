package com.xiwen.serverdemoapi.demos.web

import com.xiwen.FileDTO
import com.xiwen.User2
import io.swagger.annotations.Api
import io.swagger.annotations.ApiOperation
import lombok.extern.slf4j.Slf4j
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@Slf4j
@Api(tags = "GroovyController")
@RequestMapping("demo")
@RestController
public class GroovyController {

    @ApiOperation("test1")
    @GetMapping("test1")
    public ResponseEntity<Object> test1(){
        ResponseEntity.ok(new FileDTO(fileName: "测试",fileUrl: "http://"))
    }

    @ApiOperation("test2")
    @GetMapping("test2")
    public ResponseEntity<Object> test2(){
        ResponseEntity.ok(new User2(name: "测试",age: 10))
    }

}
