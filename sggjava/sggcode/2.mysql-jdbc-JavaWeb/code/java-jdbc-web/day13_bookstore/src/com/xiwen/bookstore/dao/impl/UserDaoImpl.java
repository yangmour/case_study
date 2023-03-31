package com.xiwen.bookstore.dao.impl;

import com.xiwen.bookstore.bean.User;
import com.xiwen.bookstore.dao.UserDao;
import com.xiwen.bookstore.dao.BaseDao;

/**
 * Description:
 *
 * @author: yf
 * @Create: 2023/03/18 -21:44
 * @Version: 1.0
 */
public class UserDaoImpl extends BaseDao<User> implements UserDao {
    @Override
    public boolean saveUser(User user) {
        String sql = "insert into users(id,username,password,email) values(null,?,?,?)";
        return update(sql, user.getUsername(), user.getPassword(), user.getEmail());

    }

    /**
     * 这个做登陆和查询是否存在重复用户
     *
     * @param user
     * @return
     */
    public User getUser(User user) {
        String sql = "select id,username,password,email from users where username = ?";
        User bean = getBean(sql, user.getUsername());
        return bean;
    }

}