package com.atguigu.file.demo1;

import org.junit.jupiter.api.Test;
import org.springframework.util.DigestUtils;

import java.io.FileInputStream;
import java.util.stream.Stream;

/**
 * Author:huzhongkui
 * Date: 2024-04-27  11:09
 */
public class DigestUtilsTest {


    @Test
    public void test() {
        byte[] bytes = new String("123").getBytes();
        String sourceMd5 = DigestUtils.md5DigestAsHex(bytes);
        System.out.println(sourceMd5);
        if (DigestUtils.md5DigestAsHex(bytes).equals(sourceMd5)) {
            System.out.println("true");
        } else {
            System.out.println("false");
        }
    }


    @Test
    public void test1() {
//        double ceil = Math.ceil(1.55);
//        System.out.println(ceil);
        System.out.println(Math.floor(1.01));
    }


    @Test
    public void test2() {
        int i = 0;
        for (; i < 3; i++) {
            System.out.println("i---" + i);
        }
        System.out.println("total-->i->" + i);
    }


    @Test
    public void test3() {
        Stream.iterate(0,x->++x).map(i->i).limit(10).forEach(System.out::println);
    }
}
