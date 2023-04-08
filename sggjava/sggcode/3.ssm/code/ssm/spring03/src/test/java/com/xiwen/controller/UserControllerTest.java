package com.xiwen.controller;

import com.xiwen.service.UserService;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.support.ClassPathXmlApplicationContext;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

/**
 * Description:
 *
 * @author: yf
 * @Create: 2023/04/07 -16:30
 * @Version: 1.0
 */
//读取配文件一种读xml一种读配置类
@ContextConfiguration(locations = "classpath:applicationContext.xml")
//@ContextConfiguration(classes = SpringConfiguration.class)
@RunWith(SpringJUnit4ClassRunner.class)
public class UserControllerTest {
    @Autowired
    private UserController userController;

    @Test
    public void setUserService() {
//        xml文件读取
        ClassPathXmlApplicationContext ioc = new ClassPathXmlApplicationContext("applicationContext.xml");
//        配置类读取
//        AnnotationConfigApplicationContext ioc = new AnnotationConfigApplicationContext(SpringConfiguration.class);
        UserController userController = ioc.getBean("userController", UserController.class);
        System.out.println(userController);
        UserService service = ioc.getBean("userService", UserService.class);
        System.out.println(service);
//        userController.getName();
    }

    @Test
    public void text02() {
//        xml文件读取
        userController.getName();


    }
}