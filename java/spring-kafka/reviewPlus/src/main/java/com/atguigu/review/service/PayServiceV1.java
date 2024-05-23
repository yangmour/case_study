package com.atguigu.review.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * @auther zzyy
 * @create 2022-08-18 0:11
 */
@Service
@Slf4j
public class PayServiceV1
{
    @Autowired
    private AlibabaPayService alibabaPayService;
    @Autowired
    private WeixinPayService weixinPayService;
    @Autowired
    private JdPayService jdPayService;

    /**
     * 运行代码并指出你发现的优化方向？
     * 干掉大段大段的if。。。else
     * @param code
     */
    public void doPaymentV1(String code)
    {
        if ("alibaba".equals(code)) {
            alibabaPayService.pay();
        } else if ("weixin".equals(code)) {
            weixinPayService.pay();
        } else if ("jd".equals(code)) {
            jdPayService.pay();
        } else {
            System.out.println("找不到支付方式: "+ code +"\t该支付方式还没纳入支付渠道");
        }
    }
}

// K:V
