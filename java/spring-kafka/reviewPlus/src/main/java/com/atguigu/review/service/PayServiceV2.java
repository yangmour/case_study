package com.atguigu.review.service;

import com.atguigu.review.enums.PaymentEnum;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * @auther zzyy
 * @create 2023-06-11 22:58
 */
@Service
@Slf4j
public class PayServiceV2
{
    public void doPaymentV2(String code)
    {
        PaymentEnum payEnumEntity = PaymentEnum.getPaymentEnums(code);

        if (payEnumEntity != null) {
            log.info("-----payv2枚举支付:{}",payEnumEntity.getCode()+"\t"+payEnumEntity.getMessage());
            System.out.println("----biz 01");
            System.out.println("----biz 02");
            System.out.println("----biz 03");
        }else{
            log.info("-----payv2枚举支付:{}",code+"\t"+"没有获得对应的支付方式");
        }

    }
}
