# 多协议节点订阅收集器

一个强大的代理节点收集工具，支持多种常见协议，包括VLESS、VMess、Shadowsocks、ShadowsocksR和Clash YAML配置。

## 功能特性

- 🔄 **多协议支持**：同时抓取VLESS、VMess、Shadowsocks、ShadowsocksR和Clash配置
- ⚡ **并行处理**：多线程抓取和测速，高效处理大量节点
- 🎯 **智能识别**：自动识别和解析各种格式的订阅源
- 📊 **速度测试**：可选择性对节点进行连通性测试和速度分类
- 📁 **分类保存**：根据协议类型和速度阈值分类保存节点
- 🧹 **自动去重**：自动去除重复节点

## 支持的协议

- ✅ **VLESS**：vless:// 链接格式
- ✅ **VMess**：vmess:// 链接格式（base64编码）
- ✅ **Shadowsocks**：ss:// 链接格式
- ✅ **ShadowsocksR**：ssr:// 链接格式
- ✅ **Clash**：YAML配置格式

## 安装步骤

### 1. 确保已安装Python 3.7+ 

```bash
python3 --version
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行脚本

```bash
python multi_protocol_subscription_collector.py
```

## 使用方法

### 基本用法

```bash
# 使用默认配置运行（抓取所有协议，不测速）
python multi_protocol_subscription_collector.py

# 添加额外的订阅源URL
python multi_protocol_subscription_collector.py --add https://example.com/subscription1 https://example.com/subscription2

# 启用测速功能
python multi_protocol_subscription_collector.py --speedtest

# 自定义高速阈值（单位：毫秒）
python multi_protocol_subscription_collector.py --speedtest --threshold 300

# 只抓取特定协议
python multi_protocol_subscription_collector.py --protocols vless vmess

# 组合使用
python multi_protocol_subscription_collector.py \
    --add https://example.com/subscription \
    --protocols vless vmess ss \
    --speedtest \
    --threshold 250
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--add`, `-a` | 添加额外的订阅源URL | 无 |
| `--speedtest` | 启用节点测速功能 | False |
| `--threshold` | 高速节点的时间阈值（毫秒） | 200 |
| `--protocols` | 指定要抓取的协议类型 | 所有支持的协议 |

## 输出文件

脚本会生成以下格式的文件：

- `{protocol}_fast_raw.txt`：指定协议的高速节点（原始链接）
- `{protocol}_slow_raw.txt`：指定协议的低速节点（原始链接）
- `{protocol}_fast_base64.txt`：指定协议的高速节点（Base64订阅格式）
- `{protocol}_slow_base64.txt`：指定协议的低速节点（Base64订阅格式）

其中 `{protocol}` 会被替换为具体的协议名称（如 `vless`、`vmess` 等）。

## 在客户端中使用

### V2RayN / V2RayU 等客户端

1. 打开客户端
2. 右键点击任务栏图标
3. 选择 "订阅设置" -> "添加订阅" 或 "从剪贴板导入" 或 "从文件导入"
4. 选择生成的 `.txt` 文件或复制 Base64 内容

### Clash 客户端

1. 打开 Clash 配置目录
2. 将生成的节点文件复制到配置目录
3. 在 Clash 配置文件中引用这些节点

## 注意事项

1. 使用脚本时请遵守相关法律法规
2. 脚本默认包含一些公共订阅源，您可以根据需要自行添加
3. 频繁请求可能会被网站限制，请合理设置抓取间隔
4. 脚本提供的测速功能仅为基本连通性测试，实际速度可能受多种因素影响

## 配置修改

您可以直接修改脚本中的以下配置参数：

- `WORKERS_FETCH`：抓取页面的线程数
- `WORKERS_SPEED`：测速的并发线程数
- `CONNECT_TIMEOUT`：连接超时时间（秒）
- `REQUEST_TIMEOUT`：请求超时时间（秒）
- `FAST_THRESHOLD_MS`：默认高速阈值（毫秒）

## 更新节点

定期运行脚本以更新节点列表：

```bash
python multi_protocol_subscription_collector.py --speedtest
```