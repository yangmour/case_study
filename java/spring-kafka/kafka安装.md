## 安装kafka文档

### docker安装kafka_2.13-2.8.1版本

第一步：拉取zookeeper、kafka镜像

> docker pull wurstmeister/zookeeper
>
> docker pull wurstmeister/kafka

第二步：启动zookeeper、kafka

> docker run -d --name zookeeper -p 2181:2181 -e TZ="Asia/Shanghai" --restart always wurstmeister/zookeeper 
>
> docker run -d --name kafka -p 9092:9092 -e KAFKA_BROKER_ID=0 -e KAFKA_ZOOKEEPER_CONNECT=111.229.165.176:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://111.229.165.176:9092 -e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092 -e TZ="Asia/Shanghai" wurstmeister/kafka 

参数介绍：
--name：容器名字
-p：端口号
KAFKA_BROKER_ID：该ID是集群的唯一标识
KAFKA_ADVERTISED_LISTENERS：kafka发布到zookeeper供客户端使用的服务地址。
KAFKA_ZOOKEEPER_CONNECT：zk的连接地址
KAFKA_LISTENERS：允许使用PLAINTEXT侦听器



第三步：进入kafka容器内部

```sh
docker exec -it kafka /bin/bash
cd /opt/kafka_2.13-2.8.1/bin
通过生产者想topic 发送消息
./kafka-console-producer.sh --broker-list 111.229.165.176:9092 --topic atguigu（topic名）
另外打开一个窗口 消费者消费消息
kafka-console-consumer.sh --bootstrap-server 111.229.165.176:9092 --topic atguigu
```

