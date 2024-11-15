package com.atguigu;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.slf4j.LoggerFactory;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

public class SecKill_redisByScript {

	private static final org.slf4j.Logger logger = LoggerFactory.getLogger(SecKill_redisByScript.class);

	public static void main(String[] args) {


		Jedis jedis = new Jedis("192.168.232.201",6379,1000000000);
		jedis.auth("redis123");
		System.out.println(jedis.ping());

	}

	static String secKillScript = "local userid=KEYS[1];\r\n"
			+ "local prodid=KEYS[2];\r\n"
			+ "local qtkey='sk:'..prodid..\":stock\";\r\n"
			+ "local usersKey='sk:'..prodid..\":uids\";\r\n"
			+ "local userExists=redis.call(\"sismember\",usersKey,userid);\r\n"
			+ "if tonumber(userExists)==1 then \r\n"
			+ "   return 2;\r\n"
			+ "end\r\n"
			+ "local num= redis.call(\"get\" ,qtkey);\r\n"
			+ "if tonumber(num)<=0 then \r\n"
			+ "   return 0;\r\n"
			+ "else \r\n"
			+ "   redis.call(\"decr\",qtkey);\r\n"
			+ "   redis.call(\"sadd\",usersKey,userid);\r\n"
			+ "end\r\n"
			+ "return 1";

	static String secKillScript2 = "local userExists=redis.call(\"sismember\",\"{sk}:0101:usr\",userid);\r\n"
			+ " return 1";

	public static boolean doSecKill(String uid, String prodid) throws IOException {

		JedisPool jedispool = JedisPoolUtil.getJedisPoolInstance();

		Jedis jedis = jedispool.getResource();
		// String sha1= .secKillScript;
		String sha1 = jedis.scriptLoad(secKillScript);

		Object result = jedis.evalsha(sha1, 2, uid, prodid);

		String reString = String.valueOf(result);
		if ("0".equals(reString)) {
			System.err.println("已秒光！！");
		} else if ("1".equals(reString)) {
			System.out.println("秒杀成功！！！！");
		} else if ("2".equals(reString)) {
			System.err.println("该用户已抢过！！");
		} else {
			System.err.println("秒杀异常！！");
		}

		jedis.close();

		return true;

	}

}
