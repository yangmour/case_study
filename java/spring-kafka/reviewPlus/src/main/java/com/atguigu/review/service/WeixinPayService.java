package com.atguigu.review.service;

import com.atguigu.review.annotations.PayAnnotation;
import org.springframework.stereotype.Service;

/**
 * @auther zzyy
 * @create 2022-08-18 0:11
 */
@Service
@PayAnnotation(myCode="weixin",myMessage1 = "注解自定义微信付款01",myMessage2 = "注解自定义微信付款02")
public class WeixinPayService implements IPay
{
    @Override
    public void pay()
    {
        System.out.println("*****微信付款IPay接口实现");
    }
}












