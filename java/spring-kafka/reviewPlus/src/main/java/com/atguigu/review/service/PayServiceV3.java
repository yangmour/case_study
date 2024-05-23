package com.atguigu.review.service;

import com.atguigu.review.annotations.PayAnnotation;
import com.atguigu.review.enums.PaymentEnum;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * @auther zzyy
 * @create 2023-06-11 23:13
 */
@Service
@Slf4j
public class PayServiceV3 implements ApplicationListener<ContextRefreshedEvent> {
    static Map<String, IPay> payMap = null;

    public void doPaymentV3(String code) {
        payMap.get(code).pay();
    }


    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        ApplicationContext applicationContext = event.getApplicationContext();
        Map<String, Object> beansWithAnnotation = applicationContext.getBeansWithAnnotation(PayAnnotation.class);


        /**
         * String(k) = alibabaPayService
         * Object(v) = com.atguigu.review.service.AlibabaPayService
         *                 alibabaPayService	com.atguigu.review.service.AlibabaPayService@6680f714
         */

        if (beansWithAnnotation != null) {
            payMap = new ConcurrentHashMap<>(beansWithAnnotation.size());

            beansWithAnnotation.forEach((k, v) -> {
                System.out.println(k + "\t" + v);

                String myCode = v.getClass().getDeclaredAnnotation(PayAnnotation.class).myCode();
                String message1 = v.getClass().getDeclaredAnnotation(PayAnnotation.class).myMessage1();
                String message2 = v.getClass().getDeclaredAnnotation(PayAnnotation.class).myMessage2();

                // mycode = alibaba
                // v = com.atguigu.review.service.AlibabaPayService

                payMap.put(myCode, (IPay) v);

            });
        }

    }


}