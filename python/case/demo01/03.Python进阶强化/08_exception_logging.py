"""
异常处理与日志系统 - 企业级错误处理

学习目标:
1. 掌握Python异常处理最佳实践
2. 自定义异常类
3. 配置logging日志系统
4. Django日志配置
5. 分布式链路追踪
"""

import logging
import sys
import traceback
from typing import Optional
from functools import wraps
import json
from datetime import datetime
import uuid


# ============================================
# 1. 自定义异常类
# ============================================

class APIException(Exception):
    """API异常基类"""

    def __init__(self, message: str, code: int = 500, data: Optional[dict] = None):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


class ValidationError(APIException):
    """数据验证异常"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, code=400)
        if field:
            self.data["field"] = field


class AuthenticationError(APIException):
    """认证异常"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, code=401)


class PermissionError(APIException):
    """权限异常"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


class NotFoundError(APIException):
    """资源不存在异常"""

    def __init__(self, resource: str, resource_id: any):
        message = f"{resource} ID={resource_id} 不存在"
        super().__init__(message, code=404)
        self.data = {"resource": resource, "id": resource_id}


class BusinessError(APIException):
    """业务逻辑异常"""

    def __init__(self, message: str):
        super().__init__(message, code=422)


def custom_exception_demo():
    """自定义异常演示"""
    print("\n" + "="*60)
    print("1. 自定义异常类")
    print("="*60)

    # 验证异常
    try:
        raise ValidationError("价格必须大于0", field="price")
    except ValidationError as e:
        print(f"✗ 验证异常: {e.to_dict()}")

    # 认证异常
    try:
        raise AuthenticationError("JWT Token已过期")
    except AuthenticationError as e:
        print(f"✗ 认证异常: {e.to_dict()}")

    # 资源不存在
    try:
        raise NotFoundError("Product", 12345)
    except NotFoundError as e:
        print(f"✗ 资源不存在: {e.to_dict()}")


# ============================================
# 2. 异常处理最佳实践
# ============================================

def safe_divide(a: float, b: float) -> float:
    """安全除法 - 异常处理示例"""
    try:
        result = a / b
    except ZeroDivisionError:
        # 捕获特定异常
        print("错误: 除数不能为0")
        return 0.0
    except TypeError as e:
        # 捕获类型错误
        print(f"错误: 参数类型错误 - {e}")
        return 0.0
    else:
        # 没有异常时执行
        print(f"计算成功: {a} / {b} = {result}")
        return result
    finally:
        # 总是执行(清理资源)
        print("除法操作完成\n")


def read_config_file(filename: str) -> dict:
    """读取配置文件 - 异常链演示"""
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError as e:
        # 异常链 - 保留原始异常
        raise BusinessError(f"配置文件不存在: {filename}") from e
    except json.JSONDecodeError as e:
        raise BusinessError(f"配置文件格式错误: {filename}") from e


def exception_best_practices():
    """异常处理最佳实践"""
    print("\n" + "="*60)
    print("2. 异常处理最佳实践")
    print("="*60)

    # 1. 具体异常捕获
    safe_divide(10, 2)
    safe_divide(10, 0)
    safe_divide(10, "abc")

    # 2. 异常链
    try:
        read_config_file("nonexistent.json")
    except BusinessError as e:
        print(f"业务异常: {e.message}")
        print(f"原始异常: {e.__cause__}")


# ============================================
# 3. 日志系统配置
# ============================================

def setup_logging():
    """配置日志系统"""

    # 创建logger
    logger = logging.getLogger("mall_app")
    logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 文件处理器
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # 错误日志处理器
    error_handler = logging.FileHandler("error.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


# 创建全局logger
logger = setup_logging()


def logging_demo():
    """日志系统演示"""
    print("\n" + "="*60)
    print("3. 日志系统")
    print("="*60)

    logger.debug("调试信息: 用户查询参数 {user_id: 123}")
    logger.info("用户登录成功: username=john")
    logger.warning("库存不足: product_id=456, stock=0")
    logger.error("数据库连接失败: timeout after 30s")
    logger.critical("支付服务宕机!")


# ============================================
# 4. 结构化日志 (JSON格式)
# ============================================

class JSONFormatter(logging.Formatter):
    """JSON格式日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加额外字段
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id

        # 异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exc()
            }

        return json.dumps(log_data, ensure_ascii=False)


def setup_json_logging():
    """配置JSON日志"""
    json_logger = logging.getLogger("json_logger")
    json_logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler("app.json.log", encoding="utf-8")
    handler.setFormatter(JSONFormatter())

    json_logger.addHandler(handler)
    return json_logger


json_logger = setup_json_logging()


def json_logging_demo():
    """JSON日志演示"""
    print("\n" + "="*60)
    print("4. 结构化日志(JSON)")
    print("="*60)

    # 普通日志
    json_logger.info("订单创建成功")

    # 带额外字段的日志
    extra = {"user_id": 123, "trace_id": str(uuid.uuid4())}
    json_logger.info("用户下单", extra=extra)

    # 异常日志
    try:
        1 / 0
    except Exception as e:
        json_logger.error("计算异常", exc_info=True, extra=extra)

    print("✓ JSON日志已写入 app.json.log")


# ============================================
# 5. 装饰器 - 自动日志记录
# ============================================

def log_execution(logger: logging.Logger):
    """日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            extra = {"trace_id": trace_id}

            # 记录函数调用
            logger.info(
                f"[{trace_id}] 调用函数: {func.__name__}",
                extra=extra
            )

            try:
                result = func(*args, **kwargs)
                logger.info(
                    f"[{trace_id}] 函数成功: {func.__name__}",
                    extra=extra
                )
                return result
            except Exception as e:
                logger.error(
                    f"[{trace_id}] 函数异常: {func.__name__} - {e}",
                    exc_info=True,
                    extra=extra
                )
                raise

        return wrapper
    return decorator


@log_execution(logger)
def process_order(order_id: int):
    """处理订单"""
    logger.info(f"处理订单: {order_id}")
    # 模拟业务逻辑
    if order_id < 0:
        raise ValueError("订单ID必须为正数")
    return {"order_id": order_id, "status": "success"}


def decorator_logging_demo():
    """装饰器日志演示"""
    print("\n" + "="*60)
    print("5. 装饰器自动日志")
    print("="*60)

    try:
        process_order(12345)
        process_order(-1)  # 会抛出异常
    except ValueError:
        pass


# ============================================
# 6. Django日志配置
# ============================================

DJANGO_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/debug.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/error.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'myapp': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    }
}


def django_logging_config():
    """Django日志配置说明"""
    print("\n" + "="*60)
    print("6. Django日志配置")
    print("="*60)

    print("在Django settings.py中添加LOGGING配置:")
    print(json.dumps(DJANGO_LOGGING_CONFIG, indent=2, ensure_ascii=False))


# ============================================
# 7. 分布式追踪 (TraceID)
# ============================================

class TraceContext:
    """追踪上下文"""
    _trace_id = None

    @classmethod
    def set_trace_id(cls, trace_id: str):
        cls._trace_id = trace_id

    @classmethod
    def get_trace_id(cls) -> str:
        if cls._trace_id is None:
            cls._trace_id = str(uuid.uuid4())
        return cls._trace_id

    @classmethod
    def clear(cls):
        cls._trace_id = None


def service_a():
    """服务A"""
    trace_id = TraceContext.get_trace_id()
    logger.info(f"[{trace_id}] 服务A: 处理用户请求")
    service_b()


def service_b():
    """服务B"""
    trace_id = TraceContext.get_trace_id()
    logger.info(f"[{trace_id}] 服务B: 查询商品信息")
    service_c()


def service_c():
    """服务C"""
    trace_id = TraceContext.get_trace_id()
    logger.info(f"[{trace_id}] 服务C: 查询库存")


def trace_demo():
    """分布式追踪演示"""
    print("\n" + "="*60)
    print("7. 分布式追踪(TraceID)")
    print("="*60)

    # 请求1
    TraceContext.set_trace_id(str(uuid.uuid4()))
    print(f"\n请求1 TraceID: {TraceContext.get_trace_id()}")
    service_a()
    TraceContext.clear()

    # 请求2
    TraceContext.set_trace_id(str(uuid.uuid4()))
    print(f"\n请求2 TraceID: {TraceContext.get_trace_id()}")
    service_a()
    TraceContext.clear()


# ============================================
# 主函数
# ============================================

def main():
    """运行所有示例"""

    custom_exception_demo()
    exception_best_practices()
    logging_demo()
    json_logging_demo()
    decorator_logging_demo()
    django_logging_config()
    trace_demo()

    print("\n" + "="*60)
    print("✓ 所有异常处理和日志示例执行完毕!")
    print("="*60)
    print("\n📚 关键要点总结:")
    print("  1. 使用自定义异常类,提升代码可读性")
    print("  2. 捕获具体异常,不要用空except")
    print("  3. 使用异常链保留原始异常信息(raise ... from e)")
    print("  4. 配置完善的日志系统(多级别、多处理器)")
    print("  5. 使用JSON格式日志便于日志分析")
    print("  6. 使用TraceID进行分布式链路追踪")
    print("  7. Django项目务必配置LOGGING")
    print("="*60)


if __name__ == "__main__":
    main()
