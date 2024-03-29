package com.atguigu.syt.hosp.dao.mongo;

import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Description:
 *
 * @author: yf
 * @Create: 2023/06/02 -19:01
 * @Version: 1.0
 */
@Repository
public interface UserRepository extends MongoRepository<User, ObjectId> {

    List<User> findByName(String name);

    List<User> findByNameLike(String name);

    List<User> findByNameAndAge(String name, Integer age);
}
