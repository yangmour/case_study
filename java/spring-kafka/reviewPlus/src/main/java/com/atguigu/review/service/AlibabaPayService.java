package com.atguigu.review.service;

import com.atguigu.review.annotations.PayAnnotation;
import com.atguigu.review.annotations.PayAnnotation2;
import org.springframework.stereotype.Service;

/**
 * @auther zzyy
 * @create 2022-08-18 0:10
 */
@Service
@PayAnnotation(myCode = "alibaba", myMessage1 = "注解自定义支付宝付款01", myMessage2 = "注解自定义支付宝付款02")
public class AlibabaPayService implements IPay {
    @Override
    public void pay() {
        System.out.println("*****支付宝付款IPay接口实现");
    }
}


//@PayAnnotation(myCode="alibaba",myMessage1 = "注解自定义支付宝付款01",myMessage2 = "注解自定义支付宝付款02")
