package com.work.DynamicProxy.service;

import com.alibaba.fastjson2.JSON;
import com.work.DynamicProxy.service.impl.UserServiceImpl01;
import com.work.DynamicProxy.service.impl.UserServiceImpl02;
import com.work.DynamicProxy.util.ServiceProxyFactory;
import org.junit.jupiter.api.Test;

class UserServiceTest {

    @Test
    void demo01() {
        UserService proxy = ServiceProxyFactory.getProxy(UserService.class, UserServiceImpl01.class);
        System.out.println("proxy=" + JSON.toJSONString(proxy));
        System.out.println("demo02=" + proxy.demo02("张三", 10));
    }

    @Test
    void demo02() {
        UserService proxy = ServiceProxyFactory.getProxy(UserService.class, UserServiceImpl02.class);
        System.out.println("proxy=" + JSON.toJSONString(proxy));
        System.out.println("demo02=" + proxy.demo02("张三", 10));
    }
}