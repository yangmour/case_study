package com.atguigu.review.entities;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @auther zzyy
 * @create 2019-12-30 11:49
 */
@AllArgsConstructor
@NoArgsConstructor
@Data
public class Order
{
    private Long id;
    private String orderName;
    private Integer orderStatus; // 0 待支付 1 已支付 2 已超时
    private String orderToken;
    private String orderSerial;

    public Order(String orderName, Integer orderStatus, String orderToken, String orderSerial)
    {
        this.orderName = orderName;
        this.orderStatus = orderStatus;
        this.orderToken = orderToken;
        this.orderSerial = orderSerial;
    }
}
