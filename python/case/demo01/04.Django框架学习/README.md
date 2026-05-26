# Django框架学习 - 企业级Web开发

> 从零构建Django RESTful API，为微服务商城项目做准备

## 📚 学习目标

1. 掌握Django框架核心概念和最佳实践
2. 熟练使用Django REST Framework构建API
3. 理解Django ORM和数据库设计
4. 掌握微服务开发所需的Django技能

---

## 📖 学习内容

### 阶段一: Django基础 (7-10天)

#### 1. Django项目结构与配置
- 创建Django项目和应用
- 理解MTV(Model-Template-View)架构
- settings.py配置详解
- 多环境配置管理(开发/测试/生产)
- 静态文件和媒体文件处理

**实践项目**: `01-blog-basic/` - 简单博客系统

---

#### 2. Django Models & ORM
- Model定义和字段类型
- 数据库迁移(migrations)
- QuerySet API 和查询优化
- 关系字段(ForeignKey, ManyToMany, OneToOne)
- 自定义Manager和QuerySet
- 数据库事务和原子操作
- N+1查询问题及解决方案(select_related, prefetch_related)

**核心知识点**:
```python
# 模型定义
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'category']),
        ]

# 查询优化
products = Product.objects.select_related('category')\
    .prefetch_related('tags')\
    .filter(price__gte=100)
```

**实践项目**: `02-orm-practice/` - ORM综合练习

---

#### 3. Django Views & URLs
- 函数视图 vs 类视图
- 通用类视图(Generic Views)
- URL路由和正则匹配
- 中间件(Middleware)
- 请求和响应处理
- 会话(Session)和Cookie

**实践项目**: `03-view-demo/` - 视图和URL配置

---

#### 4. Django Forms & 数据验证
- Form和ModelForm
- 表单验证和清洗
- 自定义验证器
- 文件上传处理
- 跨站请求伪造(CSRF)防护

---

### 阶段二: Django REST Framework (10-14天)

#### 5. DRF核心概念
- 安装和配置DRF
- API视图(APIView, ViewSet)
- Serializers序列化器
- 路由(Routers)
- 认证和权限
- 分页、过滤、搜索
- API文档生成(drf-spectacular)

**核心代码**:
```python
# Serializer
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_name']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("价格必须大于0")
        return value

# ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
```

**实践项目**: `04-drf-basic/` - RESTful API开发

---

#### 6. 认证和权限系统
- Token认证
- JWT(JSON Web Token)认证
- OAuth2.0
- 自定义权限类
- 角色权限管理(RBAC)

**技术栈**:
- `djangorestframework-simplejwt` - JWT认证
- `django-guardian` - 对象级权限

**实践项目**: `05-auth-system/` - 完整认证授权系统

---

#### 7. API设计最佳实践
- RESTful API设计规范
- API版本控制
- 统一响应格式
- 错误处理和异常
- API限流(Rate Limiting)
- CORS跨域配置

**响应格式规范**:
```python
{
    "code": 200,
    "message": "success",
    "data": {...},
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 阶段三: 企业级功能 (7-10天)

#### 8. 异步Django (ASGI)
- Django 4.x 异步视图
- 异步ORM操作
- Channels - WebSocket支持
- 后台任务(Celery)

**实践项目**: `06-async-django/` - 异步功能实现

---

#### 9. 缓存策略
- Django缓存框架
- Redis缓存
- 数据库查询缓存
- 模板缓存
- API响应缓存

**缓存配置**:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

#### 10. 数据库优化
- 数据库连接池
- 慢查询分析
- 索引优化
- 读写分离
- 分库分表策略

**实践项目**: `07-db-optimization/` - 数据库性能优化

---

#### 11. 测试驱动开发
- Django测试框架
- API测试
- 单元测试和集成测试
- 测试覆盖率
- Mock和Fixture

**测试示例**:
```python
class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'password')
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        url = reverse('product-list')
        data = {'name': 'iPhone', 'price': 6999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

---

#### 12. 日志和监控
- Django日志配置
- 结构化日志
- 错误追踪(Sentry)
- 性能监控(Django Debug Toolbar)
- APM工具集成

---

### 阶段四: 微服务准备 (5-7天)

#### 13. Docker容器化
- Dockerfile编写
- docker-compose配置
- 多容器编排
- 环境变量管理

**docker-compose.yml示例**:
```yaml
version: '3.8'
services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mall_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
  redis:
    image: redis:7-alpine
```

---

#### 14. API网关和服务通信
- 微服务间通信(REST, gRPC)
- API网关(Kong, Nginx)
- 服务注册与发现(Consul, Nacos)
- 负载均衡

---

#### 15. 消息队列
- Celery任务队列
- RabbitMQ/Redis消息队列
- 异步任务处理
- 定时任务

**Celery配置**:
```python
# tasks.py
from celery import shared_task

@shared_task
def send_order_email(order_id):
    order = Order.objects.get(id=order_id)
    send_mail(
        subject=f'订单确认 #{order_id}',
        message=f'您的订单已确认',
        from_email='noreply@mall.com',
        recipient_list=[order.user.email]
    )
```

---

## 🗂 目录结构

```
04.Django框架学习/
├── README.md                          # 本文档
├── 01-blog-basic/                     # 基础博客项目
├── 02-orm-practice/                   # ORM练习项目
├── 03-view-demo/                      # 视图和URL演示
├── 04-drf-basic/                      # DRF RESTful API
├── 05-auth-system/                    # 认证授权系统
├── 06-async-django/                   # 异步Django
├── 07-db-optimization/                # 数据库优化
├── 08-testing/                        # 测试示例
├── 09-docker-deploy/                  # Docker部署
├── requirements/                      # 依赖管理
│   ├── base.txt                       # 基础依赖
│   ├── dev.txt                        # 开发依赖
│   └── prod.txt                       # 生产依赖
├── docs/                              # 学习笔记
│   ├── django-cheatsheet.md           # Django速查表
│   ├── drf-cheatsheet.md              # DRF速查表
│   └── best-practices.md              # 最佳实践
└── scripts/                           # 工具脚本
    ├── create_project.sh              # 创建项目脚本
    └── run_tests.sh                   # 测试脚本
```

---

## 🛠 环境准备

### 安装Django和DRF

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装基础依赖
pip install -r requirements/base.txt
```

### requirements/base.txt
```
Django==5.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-filter==23.5
drf-spectacular==0.27.0
psycopg2-binary==2.9.9
redis==5.0.1
django-redis==5.4.0
celery==5.3.4
python-dotenv==1.0.0
gunicorn==21.2.0
```

---

## 🎯 学习路径建议

### 第1-2周: Django基础
- 完成blog-basic项目
- 掌握Models, Views, URLs
- 熟悉ORM查询

### 第3-4周: Django REST Framework
- 完成drf-basic项目
- 掌握Serializers和ViewSets
- 实现完整的CRUD API

### 第5周: 认证和权限
- 实现JWT认证
- 角色权限管理
- API安全加固

### 第6周: 企业级功能
- 缓存策略
- 异步任务
- 数据库优化

### 第7周: 测试和部署
- 编写单元测试和集成测试
- Docker容器化
- CI/CD配置

---

## 📊 学习检验标准

完成Django学习后,你应该能够:

✅ **基础能力**
- [ ] 独立创建Django项目和应用
- [ ] 设计合理的数据库模型
- [ ] 编写高效的ORM查询
- [ ] 处理表单和文件上传

✅ **API开发**
- [ ] 使用DRF构建RESTful API
- [ ] 实现JWT认证和权限控制
- [ ] API版本管理和文档生成
- [ ] 处理API限流和缓存

✅ **企业级能力**
- [ ] 异步任务处理(Celery)
- [ ] 缓存策略实现(Redis)
- [ ] 数据库查询优化
- [ ] 编写完整的测试用例

✅ **部署能力**
- [ ] Docker容器化部署
- [ ] 配置Nginx反向代理
- [ ] 多环境配置管理
- [ ] 日志和监控集成

---

## 🔗 下一步

完成Django学习后,继续进入:
- **05.微服务商城项目** - 企业级实战项目,综合运用所有技能

---

## 📖 学习资源

### 官方文档
- [Django官方文档(中文)](https://docs.djangoproject.com/zh-hans/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery文档](https://docs.celeryq.dev/)

### 推荐书籍
- 《Django企业开发实战》
- 《Two Scoops of Django》
- 《Django REST Framework实战》

### 在线资源
- [Django Girls教程](https://tutorial.djangogirls.org/)
- [Real Python Django Tutorials](https://realpython.com/tutorials/django/)
- [testdriven.io](https://testdriven.io/)

---

## 💡 学习建议

### ✅ 推荐做法
1. **动手实践**: 每学一个概念立即写代码验证
2. **阅读源码**: 查看Django和DRF的源码实现
3. **写技术博客**: 记录学习过程和踩坑经验
4. **参与开源**: 贡献Django/DRF相关项目
5. **对比学习**: 与Spring Boot等Java框架对比理解

### ❌ 避免误区
1. 不要只看教程不动手
2. 不要忽略测试和文档
3. 不要过早优化(先跑通,再优化)
4. 不要忽视数据库设计
5. 不要忽略安全性(SQL注入, XSS, CSRF)

---

## 🚀 快速开始

```bash
# 创建你的第一个Django项目
django-admin startproject myproject
cd myproject
python manage.py startapp myapp

# 运行开发服务器
python manage.py runserver

# 访问 http://127.0.0.1:8000
```

开始你的Django学习之旅吧! 🎉
