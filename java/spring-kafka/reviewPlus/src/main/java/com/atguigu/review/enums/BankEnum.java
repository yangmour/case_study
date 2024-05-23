package com.atguigu.review.enums;

import lombok.Getter;

import java.util.Arrays;
import java.util.function.Predicate;

/**
 * @auther zzyy
 * @create 2023-06-16 19:49
 *
 * 1 举值定义
 * 2 枚举构造
 * 3 遍历查询
 *
 * 举值 → 构造 → 遍历
 */
public enum BankEnum
{
    //1 举值定义
    CCB("ccb","中国建设银行"),
    ABC("abc","中国农业银行");

    //2 枚举构造
    @Getter
    String code;
    @Getter
    String message;

    BankEnum(String code, String message)
    {
        this.code = code;
        this.message = message;
    }

    //3.1 遍历查询
    public static BankEnum getBankEnum(String code)
    {
        BankEnum[] bankEnums = BankEnum.values();

        for (BankEnum element : bankEnums) {
            if(element.getCode().equalsIgnoreCase(code))
            {
                return element;
            }
        }
        return null;
    }

    //3.2 遍历查询
    public static BankEnum getBankEnum2(String code)
    {
        //    CCB("ccb","中国建设银行"),
        return Arrays.stream(BankEnum.values()).filter(t -> t.getCode().equalsIgnoreCase(code)).findFirst().orElse(null);


    }



    public static void main(String[] args)
    {
        BankEnum ccb = getBankEnum2("abc");

        System.out.println(ccb.getCode());
        System.out.println(ccb.getMessage());
    }

}


/**
 * public enum HttPCodeEnum
 * {
 *     PageError1("404","page not found exception"),
 *     PageError2("403","page auth exception"),
 *
 *     NOT_FOUND("404","页面没有找到")
 *
 * }
 */
