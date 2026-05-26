# 微服务商城项目 - 企业级实战

> Django + 微服务架构 + 高并发 + 分布式事务的完整电商解决方案

## 🎯 项目概述

这是一个企业级电商系统,采用微服务架构,包含完整的电商功能、高并发优化、分布式事务处理和消息队列等企业级特性。

### 项目亮点

- ✅ **微服务架构**: 7大核心服务,服务独立部署、独立扩展
- ✅ **高并发处理**: Redis缓存、消息队列、数据库优化
- ✅ **分布式事务**: Saga模式处理跨服务事务
- ✅ **API网关**: 统一入口、认证、限流、日志
- ✅ **服务治理**: 服务注册发现、负载均衡、熔断降级
- ✅ **监控告警**: Prometheus + Grafana + ELK日志系统
- ✅ **容器化部署**: Docker + Kubernetes

---

## 🏗 系统架构

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层                                │
│              Web前端(Vue3) + 移动端(Flutter)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      API网关层 (Kong/Nginx)                   │
│    统一鉴权 | 限流 | 日志 | 路由 | 负载均衡 | 熔断降级          │
└─────┬─────────┬─────────┬─────────┬─────────┬──────────────┘
      │         │         │         │         │
┌─────┴───┐ ┌──┴────┐ ┌──┴────┐ ┌──┴────┐ ┌─┴──────┐
│ 用户服务 │ │商品服务│ │订单服务│ │支付服务│ │搜索服务│ ...
│  User   │ │Product│ │ Order │ │Payment│ │Search │
└────┬────┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬────┘
     │          │         │         │         │
┌────┴──────────┴─────────┴─────────┴─────────┴──────────────┐
│                       中间件层                                │
│  Redis缓存 | RabbitMQ消息队列 | Elasticsearch搜索引擎          │
│  Consul服务发现 | Prometheus监控 | Zipkin链路追踪              │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────┴───────────────────────────────────┐
│                       数据层                                    │
│  PostgreSQL主库 | MySQL从库 | MongoDB日志库 | MinIO对象存储    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 服务划分

### 1. 用户服务 (user-service)
**职责**: 用户注册、登录、个人信息管理、地址管理

**技术栈**:
- Django 5.0 + DRF
- JWT认证
- Redis缓存用户会话
- PostgreSQL存储

**核心功能**:
- ✅ 用户注册(手机/邮箱/第三方登录)
- ✅ JWT认证和刷新
- ✅ 用户资料管理
- ✅ 收货地址管理
- ✅ 用户权限管理(RBAC)

**API示例**:
```
POST   /api/v1/users/register      # 用户注册
POST   /api/v1/users/login         # 用户登录
GET    /api/v1/users/profile       # 获取个人信息
PUT    /api/v1/users/profile       # 更新个人信息
GET    /api/v1/users/addresses     # 获取收货地址列表
POST   /api/v1/users/addresses     # 添加收货地址
```

---

### 2. 商品服务 (product-service)
**职责**: 商品管理、分类管理、品牌管理、SPU/SKU管理

**技术栈**:
- Django + DRF
- Redis缓存热门商品
- Elasticsearch全文搜索
- PostgreSQL + 读写分离

**核心功能**:
- ✅ 商品分类三级联动
- ✅ SPU/SKU管理
- ✅ 商品上下架
- ✅ 库存管理(实时扣减)
- ✅ 商品评价系统

**数据模型**:
```python
# SPU (Standard Product Unit) - 标准产品单元
class ProductSPU(models.Model):
    name = models.CharField(max_length=200)      # iPhone 15 Pro
    category = models.ForeignKey(Category)
    brand = models.ForeignKey(Brand)
    description = models.TextField()

# SKU (Stock Keeping Unit) - 库存单位
class ProductSKU(models.Model):
    spu = models.ForeignKey(ProductSPU)
    name = models.CharField(max_length=200)      # iPhone 15 Pro 256GB 深空黑
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    attributes = models.JSONField()              # {"颜色": "深空黑", "容量": "256GB"}
```

**API示例**:
```
GET    /api/v1/products             # 商品列表(分页、筛选、排序)
GET    /api/v1/products/{id}        # 商品详情
GET    /api/v1/categories           # 分类列表
GET    /api/v1/products/search      # 商品搜索
GET    /api/v1/products/hot         # 热门商品
```

---

### 3. 订单服务 (order-service)
**职责**: 订单创建、订单查询、订单状态流转、订单支付

**技术栈**:
- Django + DRF
- Redis缓存订单
- RabbitMQ处理订单队列
- PostgreSQL + 分库分表

**核心功能**:
- ✅ 订单创建(库存预扣)
- ✅ 订单支付
- ✅ 订单状态管理
- ✅ 订单超时自动取消
- ✅ 分布式事务处理(Saga模式)

**订单状态机**:
```
待支付 → 已支付 → 待发货 → 已发货 → 待收货 → 已完成
   ↓                                      ↓
 已取消  ←───────────────────────────── 退款中 → 已退款
```

**分布式事务流程**:
```
1. 订单服务: 创建订单(待支付)
2. 库存服务: 预扣库存           → 失败则回滚订单
3. 优惠券服务: 锁定优惠券       → 失败则回滚库存+订单
4. 支付服务: 创建支付单         → 失败则回滚所有
5. 消息队列: 发送订单确认通知
```

**API示例**:
```
POST   /api/v1/orders               # 创建订单
GET    /api/v1/orders               # 订单列表
GET    /api/v1/orders/{id}          # 订单详情
PUT    /api/v1/orders/{id}/cancel   # 取消订单
PUT    /api/v1/orders/{id}/pay      # 支付订单
```

---

### 4. 支付服务 (payment-service)
**职责**: 支付订单、退款、支付回调、账单管理

**技术栈**:
- Django + DRF
- 支付宝/微信支付SDK
- Redis防重放攻击
- PostgreSQL记录支付流水

**核心功能**:
- ✅ 支付宝支付
- ✅ 微信支付
- ✅ 银行卡支付
- ✅ 余额支付
- ✅ 退款处理
- ✅ 支付回调验签
- ✅ 支付流水记录

**支付流程**:
```
1. 订单服务调用支付服务创建支付单
2. 支付服务返回支付URL/二维码
3. 用户完成支付
4. 支付平台回调支付服务
5. 支付服务验证签名并更新订单状态
6. 通过消息队列通知订单服务
```

---

### 5. 购物车服务 (cart-service)
**职责**: 购物车增删改查、购物车合并

**技术栈**:
- Django + DRF
- Redis存储购物车(Hash结构)
- 无需持久化数据库

**购物车存储**:
```redis
# Redis Hash结构
HSET cart:{user_id} {sku_id} {quantity}

# 示例
HSET cart:123 sku_1001 2    # 用户123购物车中, SKU_1001数量为2
HSET cart:123 sku_1002 1
```

---

### 6. 营销服务 (promotion-service)
**职责**: 优惠券、满减、限时折扣、秒杀、拼团

**技术栈**:
- Django + DRF
- Redis实现秒杀库存
- Lua脚本原子性扣减
- RabbitMQ异步处理

**核心功能**:
- ✅ 优惠券发放和使用
- ✅ 满减活动
- ✅ 限时折扣
- ✅ 秒杀活动(高并发)
- ✅ 拼团活动

**秒杀实现**:
```lua
-- Redis Lua脚本实现原子性库存扣减
local stock_key = KEYS[1]
local user_key = KEYS[2]
local quantity = tonumber(ARGV[1])

-- 检查库存
local stock = redis.call('GET', stock_key)
if not stock or tonumber(stock) < quantity then
    return 0  -- 库存不足
end

-- 检查用户是否已购买
if redis.call('SISMEMBER', user_key, ARGV[2]) == 1 then
    return -1  -- 已购买
end

-- 扣减库存并记录用户
redis.call('DECRBY', stock_key, quantity)
redis.call('SADD', user_key, ARGV[2])
return 1  -- 成功
```

---

### 7. 搜索服务 (search-service)
**职责**: 商品搜索、自动补全、搜索推荐

**技术栈**:
- Django + DRF
- Elasticsearch全文搜索
- Redis缓存热门搜索词

**核心功能**:
- ✅ 全文搜索
- ✅ 分词搜索(IK分词器)
- ✅ 搜索自动补全
- ✅ 搜索历史
- ✅ 热门搜索词
- ✅ 搜索结果排序(相关性、价格、销量)

---

## 🔧 技术栈清单

### 后端框架
- **Django 5.0** - Web框架
- **Django REST Framework** - RESTful API
- **Celery** - 异步任务队列

### 数据库
- **PostgreSQL 15** - 主数据库
- **MySQL 8.0** - 订单库(分库分表)
- **MongoDB** - 日志存储
- **Redis 7.0** - 缓存 + 分布式锁

### 消息队列
- **RabbitMQ** - 消息队列
- **Kafka** - 日志收集

### 搜索引擎
- **Elasticsearch 8.x** - 全文搜索
- **Kibana** - 日志可视化

### 服务治理
- **Consul** - 服务注册与发现
- **Kong** - API网关
- **Nginx** - 反向代理 + 负载均衡

### 监控告警
- **Prometheus** - 监控数据采集
- **Grafana** - 监控可视化
- **Alertmanager** - 告警管理
- **Zipkin** - 分布式链路追踪

### 存储
- **MinIO** - 对象存储(图片、视频)
- **FastDFS** - 分布式文件存储

### 容器化
- **Docker** - 容器化
- **Docker Compose** - 本地开发编排
- **Kubernetes** - 生产环境编排

### 认证和安全
- **JWT** - 无状态认证
- **OAuth2.0** - 第三方登录
- **HTTPS** - 加密传输

---

## 📂 项目结构

```
05.微服务商城项目/
├── README.md                              # 本文档
├── docs/                                  # 项目文档
│   ├── 01-架构设计.md
│   ├── 02-数据库设计.md
│   ├── 03-API接口文档.md
│   ├── 04-部署文档.md
│   ├── 05-性能优化.md
│   └── 06-常见问题.md
├── services/                              # 微服务
│   ├── user-service/                      # 用户服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── manage.py
│   │   ├── config/                        # 配置
│   │   ├── apps/                          # 应用
│   │   │   ├── users/                     # 用户模块
│   │   │   └── addresses/                 # 地址模块
│   │   └── tests/                         # 测试
│   ├── product-service/                   # 商品服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── manage.py
│   │   └── apps/
│   │       ├── products/                  # 商品模块
│   │       ├── categories/                # 分类模块
│   │       └── reviews/                   # 评价模块
│   ├── order-service/                     # 订单服务
│   ├── payment-service/                   # 支付服务
│   ├── cart-service/                      # 购物车服务
│   ├── promotion-service/                 # 营销服务
│   └── search-service/                    # 搜索服务
├── gateway/                               # API网关
│   ├── kong/                              # Kong配置
│   └── nginx/                             # Nginx配置
├── infrastructure/                        # 基础设施
│   ├── docker-compose.yml                 # 本地开发环境
│   ├── k8s/                               # Kubernetes配置
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── configmaps/
│   │   └── ingress/
│   ├── monitoring/                        # 监控配置
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   └── alertmanager/
│   └── logging/                           # 日志配置
│       ├── elasticsearch/
│       ├── logstash/
│       └── kibana/
├── scripts/                               # 脚本
│   ├── init_db.sh                         # 初始化数据库
│   ├── start_services.sh                  # 启动所有服务
│   └── deploy.sh                          # 部署脚本
├── common/                                # 公共库
│   ├── utils/                             # 工具类
│   ├── middleware/                        # 中间件
│   └── exceptions/                        # 异常定义
└── tests/                                 # 集成测试
    ├── api_tests/
    └── performance_tests/
```

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7.0
- RabbitMQ 3.12

### 2. 本地开发环境启动

```bash
# 1. 克隆代码
cd 05.微服务商城项目

# 2. 启动基础设施(数据库、缓存、消息队列)
docker-compose -f infrastructure/docker-compose.yml up -d

# 3. 创建Python虚拟环境
python -m venv venv
source venv/bin/activate

# 4. 安装依赖(以用户服务为例)
cd services/user-service
pip install -r requirements.txt

# 5. 数据库迁移
python manage.py migrate

# 6. 启动服务
python manage.py runserver 8001

# 7. 其他服务类似操作,端口依次递增
# product-service: 8002
# order-service: 8003
# payment-service: 8004
# ...
```

### 3. Docker Compose一键启动

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f user-service
```

---

## 📊 开发进度

### Phase 1: 基础服务搭建 (2-3周)
- [ ] 用户服务基础功能
- [ ] 商品服务基础功能
- [ ] 订单服务基础功能
- [ ] 购物车服务
- [ ] API网关配置

### Phase 2: 核心功能完善 (3-4周)
- [ ] JWT认证体系
- [ ] 支付服务集成
- [ ] 营销服务(优惠券、满减)
- [ ] 搜索服务(Elasticsearch)
- [ ] 消息队列集成

### Phase 3: 高级特性 (2-3周)
- [ ] 分布式事务(Saga)
- [ ] 高并发优化(缓存、限流)
- [ ] 秒杀功能
- [ ] 服务注册发现(Consul)
- [ ] 链路追踪(Zipkin)

### Phase 4: 监控和部署 (1-2周)
- [ ] Prometheus + Grafana监控
- [ ] ELK日志系统
- [ ] Kubernetes部署
- [ ] CI/CD配置
- [ ] 压力测试

---

## 🎯 学习目标检验

完成本项目后,你应该掌握:

✅ **微服务架构**
- [ ] 服务拆分原则和实践
- [ ] 服务间通信(REST, RPC)
- [ ] API网关设计
- [ ] 服务注册与发现

✅ **高并发处理**
- [ ] Redis缓存策略
- [ ] 消息队列异步处理
- [ ] 数据库读写分离
- [ ] 秒杀系统设计

✅ **分布式系统**
- [ ] 分布式事务(Saga模式)
- [ ] 分布式锁
- [ ] 分库分表
- [ ] 分布式ID生成

✅ **DevOps能力**
- [ ] Docker容器化
- [ ] Kubernetes编排
- [ ] CI/CD流程
- [ ] 监控和告警

---

## 📖 学习资源

- 《微服务架构设计模式》
- 《高并发系统设计40问》
- 《分布式系统原理与实践》
- 《Kubernetes权威指南》

---

## 💡 项目建议

1. **循序渐进**: 先完成单体,再拆分微服务
2. **测试先行**: 编写完整的单元测试和集成测试
3. **文档完善**: 及时更新API文档和架构文档
4. **性能优化**: 使用性能分析工具找瓶颈
5. **安全第一**: 注意SQL注入、XSS、CSRF等安全问题

---

开始构建你的企业级微服务商城吧! 🚀
