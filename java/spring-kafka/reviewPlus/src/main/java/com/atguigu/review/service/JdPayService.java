package com.atguigu.review.service;

import com.atguigu.review.annotations.PayAnnotation;
import org.springframework.stereotype.Service;

/**
 * @auther zzyy
 * @create 2023-06-11 22:22
 * <p>
 * JdPayService = jdPayService   UserService -> userService
 */
@Service
@PayAnnotation(myCode = "jd", myMessage1 = "注解自定义京东付款01", myMessage2 = "注解自定义京东付款02")
public class JdPayService implements IPay {
    @Override
    public void pay() {
        System.out.println("*****京东付款IPay接口实现");
    }
}


//@PayAnnotation(myCode="jd",myMessage1 = "注解自定义京东付款01",myMessage2 = "注解自定义京东付款02")