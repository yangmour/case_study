package com.xiwen.service;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import java.util.ArrayList;

import static org.junit.Assert.*;

/**
 * Description:
 *
 * @author: yf
 * @Create: 2023/04/11 -10:08
 * @Version: 1.0
 */
@ContextConfiguration(locations = "classpath:jdbc.xml")
@RunWith(SpringJUnit4ClassRunner.class)
public class CashierTest {

    @Autowired
    private Cashier cashier;

    @Test
    public void checkout() {
        ArrayList<String> ids = new ArrayList<>();
        ids.add("1001");
        ids.add("1002");
        cashier.checkout(1, ids);
    }
}