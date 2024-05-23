package com.atguigu.review.enums;

import lombok.Getter;

public enum CountryEnum
{
    ONE(1,"齐"),TWO(2,"楚"),THREE(3,"燕"),FOUR(4,"赵"),FIVE(5,"魏"),SIX(6,"韩");

    @Getter private Integer retCode;
    @Getter private String  retMessage;

    CountryEnum(Integer retCode, String retMessage)
    {
        this.retCode = retCode;
        this.retMessage = retMessage;
    }

    public static CountryEnum forEach_CountryEnum(int index)
    {
        CountryEnum[] myArray = CountryEnum.values();
        for (CountryEnum element : myArray)
        {
            if(index == element.getRetCode())
            {
                return element;
            }
        }
        return null;
    }

}

/*
mysql dbName = CountryEnum

table
one
ID userName age birth userEmail
1  齐       109

        ONE(1,"齐",v2,v3,v4,v5)*/
