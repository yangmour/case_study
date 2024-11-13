package com.work.DynamicProxy.jdk.service.impl;

import com.work.DynamicProxy.jdk.service.UserService;
import org.springframework.stereotype.Service;


@Service
public class UserServiceImpl02 implements UserService {
    @Override
    public String demo01() {
        return "UserServiceImpl02执行了";
    }

    @Override
    public String demo02(String name, Integer age) {
        return "";
    }
}
