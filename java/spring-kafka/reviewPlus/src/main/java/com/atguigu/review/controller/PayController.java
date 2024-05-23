package com.atguigu.review.controller;

import com.atguigu.review.service.PayServiceV1;
import com.atguigu.review.service.PayServiceV2;
import com.atguigu.review.service.PayServiceV3;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * @auther zzyy
 * @create 2023-06-11 22:42
 */
@RestController
@Slf4j
public class PayController
{
    @Autowired private PayServiceV1 payServiceV1;//V1（if..else）
    @Autowired private PayServiceV2 payServiceV2;//V2
    @Autowired private PayServiceV3 payServiceV3;//V3

    @GetMapping(value = "/payv1/{code}")
    public void payV1(@PathVariable("code") String code)
    {
        payServiceV1.doPaymentV1(code);
    }

    @GetMapping(value = "/payv2/{code}")
    public void payV2(@PathVariable("code") String code)
    {
        payServiceV2.doPaymentV2(code);
    }

    @GetMapping(value = "/payv3/{code}")
    public void payV3(@PathVariable("code") String code)
    {
        payServiceV3.doPaymentV3(code);
    }

}
