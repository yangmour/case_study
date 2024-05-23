package com.atguigu.review.annotations;

import lombok.Getter;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * @auther zzyy
 * @create 2023-06-11 23:08
 */
@Target({ElementType.TYPE}) //决定了该注解用在哪里，放在类上，方法上，还是字段上
@Retention(RetentionPolicy.RUNTIME) //作用范围，自定义注解，99%用在运行时，固定写死RetentionPolicy.RUNTIME
public @interface PayAnnotation
{
    String myCode()         default "";
    String myMessage1()     default "";
    String myMessage2()     default "";
}
