package com.atguigu.review.enums;

import lombok.Getter;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.function.Predicate;
import java.util.stream.Stream;

/**
 * @auther zzyy
 * @create 2023-06-11 22:50
 *
 * 1 举值定义
 * 2 枚举构造
 * 3 遍历打通
 *
 * 举值 → 构造 → 遍历
 */
public enum PaymentEnum
{
    //1 举值定义
    ALIBABA("alibaba","支付宝枚举版支付"),
    WEIXIN("weixin","微信枚举版支付"),
    //DOUYING("dy","抖音枚举版支付"),
    JD("jd","京东枚举版支付");

    //2 枚举构造
    @Getter private String code;
    @Getter private String message;

    PaymentEnum(String code, String message)
    {
        this.code = code;
        this.message = message;
    }

    //3 遍历打通
    public static PaymentEnum getPaymentEnums(String code)
    {
        PaymentEnum[] myArray = PaymentEnum.values();

        for (PaymentEnum element : myArray) {
            if(element.getCode().equalsIgnoreCase(code))
            {
                return element;
            }
        }
        return null;
    }

    public static PaymentEnum getPaymentEnums2(String code)
    {
        return Arrays.stream(PaymentEnum.values()).filter(x -> x.getCode().equalsIgnoreCase(code)).findFirst().orElse(null);
    }


    public static void main(String[] args)
    {
        System.out.println(PaymentEnum.JD);
        System.out.println(PaymentEnum.JD.getMessage());
        System.out.println(PaymentEnum.JD.getCode());
    }

}


/*public enum HttpCode
{
    NOT_FOUND("404","页面没有找到")
}

枚举 =  mysql，可以模拟不用数据库，直接从枚举查询数据，直接避免
t_user

    //2 枚举构造
    @Getter private String code;
    @Getter private String message;
id userName age score major

    //2 枚举构造
    @Getter private String id;
    @Getter private String userName;
    @Getter private String age;
    @Getter private String score;

*/
