#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multi_protocol_subscription_collector.py
抓取 VLESS/VMess/Shadowsocks/ShadowsocksR/Clash YAML 节点，分类输出，高速/低速可选。
Usage:
    python multi_protocol_subscription_collector.py \
        --add https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v2 \
        --speedtest

    # 只抓取特定协议
    python multi_protocol_subscription_collector.py \
        --add https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v2 \
        --protocols vless vmess clash
"""

import base64
import re
import socket
import time
import argparse
import json
import os
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Set, Optional

def is_base64(s: str) -> bool:
    """检查字符串是否可能是Base64编码的"""
    try:
        # Base64编码的字符串长度应该是4的倍数
        # 只包含Base64字符集：A-Z, a-z, 0-9, +, /, =(填充)
        import re
        if len(s) % 4 != 0:
            return False
        # 检查字符集
        if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', s):
            return False
        # 尝试解码
        base64.b64decode(s)
        return True
    except Exception:
        return False

def is_yaml_content(content: str) -> bool:
    """检查内容是否可能是Clash YAML配置"""
    # 检查是否包含Clash配置的关键字段
    keywords = [
        'mixed-port', 'port', 'socks-port', 'redir-port',
        'allow-lan', 'mode', 'log-level', 'external-controller',
        'proxies:', 'proxy-groups:', 'rules:'
    ]
    
    # 检查是否包含YAML特有的结构
    if 'proxies:' in content and 'rules:' in content:
        return True
    
    # 检查关键字出现的频率
    keyword_count = 0
    for keyword in keywords:
        if keyword in content:
            keyword_count += 1
            # 如果找到多个关键字，很可能是YAML配置
            if keyword_count >= 3:
                return True
    
    return False

# -------------------- 配置区 --------------------
SOURCE_URLS = [
    "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v2",
]

WORKERS_FETCH = 8          # 抓取页面线程
WORKERS_SPEED = 32         # 并行测速线程
CONNECT_TIMEOUT = 3.0
REQUEST_TIMEOUT = 12
HEADERS = {"User-Agent": "multi-protocol-collector/1.0 (+your-email@example.com)"}

FAST_THRESHOLD_MS = 200    # 默认高速阈值(毫秒)

# Clash配置模板
CLASH_TEMPLATE = {
    "mixed-port": 7890,
    "allow-lan": True,
    "mode": "Rule",
    "log-level": "info",
    "external-controller": "127.0.0.1:9090",
    "proxies": [],
    "proxy-groups": [
        {
            "name": "自动选择",
            "type": "url-test",
            "proxies": [],
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300
        },
        {
            "name": "手动选择",
            "type": "select",
            "proxies": ["自动选择"]
        }
    ],
    "rules": [
        "DOMAIN-SUFFIX,google.com,自动选择",
        "DOMAIN-SUFFIX,github.com,自动选择",
        "DOMAIN-SUFFIX,youtube.com,自动选择",
        "DOMAIN-SUFFIX,netflix.com,自动选择",
        "GEOIP,CN,DIRECT",
        "MATCH,自动选择"
    ]
}

# 文件命名配置
def get_output_files(protocol: str) -> Tuple[str, str, str, str]:
    """获取指定协议的输出文件名"""
    prefix = protocol
    return (
        f"{prefix}_fast_raw.txt",
        f"{prefix}_slow_raw.txt",
        f"{prefix}_fast_base64.txt",
        f"{prefix}_slow_base64.txt"
    )

# V2Ray配置模板
def create_v2ray_config(links: List[str]) -> Dict:
    """从链接列表创建V2Ray配置"""
    inbounds = [
        {
            "port": 10808,
            "protocol": "socks",
            "settings": {
                "auth": "noauth",
                "udp": True,
                "userLevel": 8
            }
        },
        {
            "port": 10809,
            "protocol": "http",
            "settings": {
                "userLevel": 8
            }
        }
    ]
    
    outbounds = []
    stream_settings = {}
    
    # 解析链接并创建outbounds
    for link in links:
        protocol = get_protocol_from_link(link)
        if not protocol:
            continue
            
        try:
            if protocol == 'vless':
                # vless://uuid@host:port?encryption=none&security=tls&sni=example.com#name
                parsed = urlparse(link)
                userinfo, _, hostport = parsed.netloc.rpartition('@')
                host, port = hostport.split(':', 1) if ':' in hostport else (hostport, '443')
                query = parse_qs(parsed.query)
                
                outbound = {
                    "protocol": "vless",
                    "tag": parsed.fragment or f"vless_{host}",
                    "settings": {
                        "vnext": [
                            {
                                "address": host,
                                "port": int(port),
                                "users": [
                                    {
                                        "id": userinfo,
                                        "encryption": query.get('encryption', ['none'])[0],
                                        "level": 8
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": "tcp"
                    }
                }
                
                if 'security' in query and query['security'][0] == 'tls':
                    outbound['streamSettings']['security'] = 'tls'
                    if 'sni' in query:
                        outbound['streamSettings']['tlsSettings'] = {
                            "serverName": query['sni'][0]
                        }
                
                outbounds.append(outbound)
                
            elif protocol == 'vmess':
                # vmess://base64_encoded_json
                vmess_data = link[8:]
                padding = len(vmess_data) % 4
                if padding > 0:
                    vmess_data += '=' * (4 - padding)
                decoded = base64.b64decode(vmess_data)
                vmess_config = json.loads(decoded.decode())
                
                outbound = {
                    "protocol": "vmess",
                    "tag": vmess_config.get('ps', f"vmess_{vmess_config.get('add')}"),
                    "settings": {
                        "vnext": [
                            {
                                "address": vmess_config.get('add'),
                                "port": vmess_config.get('port'),
                                "users": [
                                    {
                                        "id": vmess_config.get('id'),
                                        "alterId": vmess_config.get('aid', 0),
                                        "level": 8,
                                        "security": vmess_config.get('security', 'auto')
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": vmess_config.get('net', 'tcp'),
                        "security": vmess_config.get('tls', '')
                    }
                }
                
                # 添加传输协议相关配置
                if vmess_config.get('net') == 'ws' and 'path' in vmess_config:
                    outbound['streamSettings']['wsSettings'] = {
                        "path": vmess_config.get('path'),
                        "headers": {}
                    }
                    if 'host' in vmess_config:
                        outbound['streamSettings']['wsSettings']['headers']['Host'] = vmess_config.get('host')
                
                outbounds.append(outbound)
                
            elif protocol == 'ss':
                # ss://base64(加密方式:密码)@服务器地址:端口#备注
                try:
                    parsed = urlparse(link)
                    ss_data = link[5:]
                    # 处理可能的URI片段（备注）
                    ss_data_without_fragment = ss_data.split('#')[0]
                    
                    # 分割用户信息和服务器信息
                    user_info_part, _, server_info_part = ss_data_without_fragment.rpartition('@')
                    
                    # 解码用户信息部分
                    padding = len(user_info_part) % 4
                    if padding > 0:
                        user_info_part += '=' * (4 - padding)
                    user_info_decoded = base64.b64decode(user_info_part).decode('utf-8', errors='ignore')
                    
                    # 分割加密方式和密码
                    method, password = user_info_decoded.split(':', 1) if ':' in user_info_decoded else (user_info_decoded, '')
                    
                    # 分割服务器地址和端口
                    host, port = server_info_part.split(':', 1) if ':' in server_info_part else (server_info_part, '80')
                    
                    outbound = {
                        "protocol": "shadowsocks",
                        "tag": parsed.fragment or f"ss_{host}",
                        "settings": {
                            "servers": [
                                {
                                    "address": host,
                                    "port": int(port),
                                    "method": method,
                                    "password": password,
                                    "level": 8
                                }
                            ]
                        }
                    }
                    
                    outbounds.append(outbound)
                except Exception as e:
                    print(f"[WARN] 解析SS链接失败: {e}")
                    continue
        except Exception as e:
            print(f"[WARN] 解析 {protocol} 链接失败: {e}")
    
    # 添加直连出站
    outbounds.append({
        "protocol": "freedom",
        "tag": "direct",
        "settings": {}
    })
    
    # 添加阻止出站
    outbounds.append({
        "protocol": "blackhole",
        "tag": "block",
        "settings": {
            "response": {
                "type": "http"
            }
        }
    })
    
    # 路由配置
    routing = {
        "domainStrategy": "IPIfNonMatch",
        "rules": [
            {
                "type": "field",
                "ip": ["geoip:private"],
                "outboundTag": "direct"
            }
        ]
    }
    
    return {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": inbounds,
        "outbounds": outbounds,
        "routing": routing
    }

# 协议正则表达式
PROTOCOL_REGEX = {
    'vless': re.compile(r'(vless://[A-Za-z0-9@:\-._~!$&\'()*+,;=%/?#]+)'),
    'vmess': re.compile(r'(vmess://[A-Za-z0-9+/=]+)'),
    'ss': re.compile(r'(ss://[A-Za-z0-9+/=]+)'),
    'ssr': re.compile(r'(ssr://[A-Za-z0-9+/=]+)'),
    # Clash配置文件通常包含特定关键词
    'clash': re.compile(r'proxies|proxy-groups|rules', re.MULTILINE)
}

BASE64_RE = re.compile(r'^[A-Za-z0-9+/=\s]+$')

# -------------------- 网络请求 --------------------
def fetch_url_text(url: str) -> str:
    """获取URL内容"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(f"[WARN] 抓取失败 {url}: {e}")
        return ""

# -------------------- 协议解析 --------------------
def extract_links_from_text(text: str, protocols: List[str]) -> Dict[str, Set[str]]:
    """从文本中提取所有支持的协议链接"""
    results = {protocol: set() for protocol in protocols}
    
    # 提取直接链接
    for protocol in protocols:
        if protocol != 'clash':  # Clash需要特殊处理
            for m in PROTOCOL_REGEX[protocol].findall(text):
                results[protocol].add(m.strip())
    
    # 尝试Base64解码
    stripped = "".join(text.split())
    if len(stripped) > 16 and BASE64_RE.match(stripped):
        try:
            decoded = base64.b64decode(stripped + "===", validate=False)
            s2 = decoded.decode(errors="ignore")
            for protocol in protocols:
                if protocol != 'clash':
                    for m in PROTOCOL_REGEX[protocol].findall(s2):
                        results[protocol].add(m.strip())
            # 检查是否包含Clash配置
            if 'clash' in protocols and PROTOCOL_REGEX['clash'].search(s2):
                results['clash'].add(s2)
        except Exception:
            pass
    
    # HTML解析
    soup = BeautifulSoup(text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        for protocol in protocols:
            if protocol != 'clash' and href.startswith(f"{protocol}://"):
                results[protocol].add(href)
    
    visible_text = soup.get_text(separator="\n")
    for protocol in protocols:
        if protocol != 'clash':
            for m in PROTOCOL_REGEX[protocol].findall(visible_text):
                results[protocol].add(m.strip())
    
    return results

def parse_clash_yaml(content: str) -> Dict[str, Set[str]]:
    """从Clash YAML配置中提取节点信息"""
    results = {'vmess': set(), 'ss': set(), 'ssr': set(), 'vless': set()}
    
    try:
        # 导入yaml库进行解析
        import yaml
        
        # 检查内容是否为YAML格式
        if not content.strip().startswith(('proxies:', 'proxy-groups:', 'rules:', '# Clash')):
            # 尝试从内容中提取可能的YAML部分
            for line in content.split('\n'):
                if line.strip().startswith('proxies:'):
                    yaml_start = content.find(line)
                    config = yaml.safe_load(content[yaml_start:])
                    break
            else:
                return results
        else:
            config = yaml.safe_load(content)
        
        if isinstance(config, dict) and 'proxies' in config:
            for proxy in config['proxies']:
                if isinstance(proxy, dict) and 'type' in proxy:
                    proxy_type = proxy['type']
                    if proxy_type in results:
                        # 尝试根据不同协议构建标准链接格式
                        try:
                            if proxy_type == 'vmess':
                                # 构建vmess链接
                                vmess_dict = {
                                    'v': '2',
                                    'ps': proxy.get('name', 'Clash-VMess'),
                                    'add': proxy.get('server', ''),
                                    'port': proxy.get('port', 0),
                                    'id': proxy.get('uuid', ''),
                                    'aid': proxy.get('alterId', 0),
                                    'net': proxy.get('network', 'tcp'),
                                    'type': proxy.get('type', 'none'),
                                    'host': proxy.get('host', ''),
                                    'path': proxy.get('path', ''),
                                    'tls': 'tls' if proxy.get('tls') else ''
                                }
                                vmess_json = json.dumps(vmess_dict)
                                vmess_link = f"vmess://{base64.b64encode(vmess_json.encode()).decode('utf-8')}"
                                results['vmess'].add(vmess_link)
                            elif proxy_type == 'ss':
                                # 构建shadowsocks链接
                                method = proxy.get('cipher', '')
                                password = proxy.get('password', '')
                                server = proxy.get('server', '')
                                port = proxy.get('port', 0)
                                name = proxy.get('name', 'Clash-SS')
                                
                                # ss://method:password@server:port#name
                                ss_part = f"{method}:{password}"
                                ss_part_encoded = base64.b64encode(ss_part.encode()).decode('utf-8')
                                ss_link = f"ss://{ss_part_encoded}@{server}:{port}#{name}"
                                results['ss'].add(ss_link)
                            elif proxy_type == 'ssr':
                                # SSR链接构建相对复杂，这里简化处理
                                ssr_info = str(proxy)
                                results['ssr'].add(ssr_info)
                            elif proxy_type == 'vless':
                                # 构建vless链接
                                uuid = proxy.get('uuid', '')
                                server = proxy.get('server', '')
                                port = proxy.get('port', 0)
                                name = proxy.get('name', 'Clash-VLESS')
                                
                                # vless://uuid@server:port?encryption=none&security=...#name
                                vless_link = f"vless://{uuid}@{server}:{port}?encryption=none#{name}"
                                results['vless'].add(vless_link)
                        except Exception as e:
                            print(f"[DEBUG] 构建{proxy_type}链接失败: {e}")
                            # 构建失败时，添加原始配置信息作为备选
                            results[proxy_type].add(str(proxy))
    except Exception as e:
        print(f"[WARN] Clash配置解析失败: {e}")
    
    return results

def is_valid_protocol_link(link: str, protocol: str) -> bool:
    """验证链接是否为有效的指定协议链接"""
    try:
        if protocol == 'vless':
            parsed = urlparse(link)
            if parsed.scheme != "vless":
                return False
            # vless://uuid@host:port?encryption=none&security=tls&sni=example.com#name
            hostport = parsed.netloc.split("@")[-1]
            if ":" not in hostport:
                return False
            host, port = hostport.split(":", 1)
            if not host or not port.isdigit() or not (0 < int(port) <= 65535):
                return False
            # 检查查询参数
            query = parse_qs(parsed.query)
            if 'encryption' not in query:
                return False
            return True
        elif protocol == 'vmess':
            # VMess链接通常是base64编码的JSON
            try:
                if not link.startswith("vmess://"):
                    return False
                vmess_data = link[8:]
                # 处理可能缺失的padding
                padding = len(vmess_data) % 4
                if padding > 0:
                    vmess_data += '=' * (4 - padding)
                decoded = base64.b64decode(vmess_data)
                vmess_config = json.loads(decoded.decode())
                # 验证必要字段
                required_fields = ['add', 'port', 'id']
                for field in required_fields:
                    if field not in vmess_config or not vmess_config[field]:
                        return False
                return True
            except:
                return False
        elif protocol == 'ss':
            # Shadowsocks链接格式: ss://base64(加密方式:密码)@服务器地址:端口#备注
            if not link.startswith("ss://"):
                return False
            # 简单验证，实际应用中可进行更复杂的解析
            parts = link[5:].split('@')
            if len(parts) < 2:
                return False
            server_part = parts[1].split(':')
            if len(server_part) < 2:
                return False
            try:
                # 尝试解码前半部分
                base64_part = parts[0]
                padding = len(base64_part) % 4
                if padding > 0:
                    base64_part += '=' * (4 - padding)
                base64.b64decode(base64_part)
                # 验证端口
                port = int(server_part[1].split('#')[0])
                return 0 < port <= 65535
            except:
                return False
        elif protocol == 'ssr':
            # ShadowsocksR链接更复杂，但基本格式为ssr://base64_encoded_string
            if not link.startswith("ssr://"):
                return False
            # 简单验证
            try:
                ssr_data = link[6:]
                padding = len(ssr_data) % 4
                if padding > 0:
                    ssr_data += '=' * (4 - padding)
                base64.b64decode(ssr_data)
                return True
            except:
                return False
        else:
            return True  # 其他协议简化验证
    except Exception:
        return False

# -------------------- 协议工具函数 --------------------
def get_protocol_from_link(link: str) -> Optional[str]:
    """从链接中提取协议类型"""
    if link.startswith('vless://'):
        return 'vless'
    elif link.startswith('vmess://'):
        return 'vmess'
    elif link.startswith('ss://'):
        return 'ss'
    elif link.startswith('ssr://'):
        return 'ssr'
    return None

def get_protocol_pattern(protocol: str) -> Optional[re.Pattern]:
    """获取指定协议的正则表达式模式"""
    return PROTOCOL_REGEX.get(protocol)

def save_list(raw_file: str, sub_file: str, links: List[str]) -> None:
    """保存链接列表到原始文件和Base64编码的订阅文件"""
    # 保存原始链接文件
    with open(raw_file, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f"{link}\n")
    
    # 创建Base64编码的订阅文件
    subscription_content = '\n'.join(links)
    encoded_content = base64.b64encode(subscription_content.encode('utf-8')).decode('utf-8')
    with open(sub_file, 'w', encoding='utf-8') as f:
        f.write(encoded_content)

def save_v2ray_config(file_path: str, config: Dict) -> None:
    """保存V2Ray配置到JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def create_clash_config(links: List[str]) -> Dict:
    """从链接列表创建Clash配置"""
    # 复制模板配置
    config = CLASH_TEMPLATE.copy()
    proxies = []
    
    for link in links:
        protocol = get_protocol_from_link(link)
        if not protocol:
            continue
        
        try:
            if protocol == 'vmess':
                # vmess://base64(json)
                vmess_data = link[8:]
                padding = len(vmess_data) % 4
                if padding > 0:
                    vmess_data += '=' * (4 - padding)
                vmess_json = json.loads(base64.b64decode(vmess_data).decode('utf-8'))
                
                proxy = {
                    "name": vmess_json.get('ps', f"vmess_{vmess_json.get('add', '')}"),
                    "type": "vmess",
                    "server": vmess_json.get('add', ''),
                    "port": vmess_json.get('port', 0),
                    "uuid": vmess_json.get('id', ''),
                    "alterId": vmess_json.get('aid', 0),
                    "cipher": vmess_json.get('scy', 'auto'),
                    "tls": vmess_json.get('tls', '') == 'tls',
                    "skip-cert-verify": True,
                    "network": vmess_json.get('net', ''),
                    "ws-path": vmess_json.get('path', '') if vmess_json.get('net') == 'ws' else '',
                    "ws-headers": vmess_json.get('header', {}).get('headers', {}) if vmess_json.get('net') == 'ws' else {}
                }
                proxies.append(proxy)
            elif protocol == 'ss':
                # ss://base64(加密方式:密码)@服务器地址:端口#备注
                parsed = urlparse(link)
                ss_data = link[5:]
                ss_data_without_fragment = ss_data.split('#')[0]
                
                user_info_part, _, server_info_part = ss_data_without_fragment.rpartition('@')
                
                padding = len(user_info_part) % 4
                if padding > 0:
                    user_info_part += '=' * (4 - padding)
                user_info_decoded = base64.b64decode(user_info_part).decode('utf-8', errors='ignore')
                
                method, password = user_info_decoded.split(':', 1) if ':' in user_info_decoded else (user_info_decoded, '')
                
                host, port = server_info_part.split(':', 1) if ':' in server_info_part else (server_info_part, '80')
                
                proxy = {
                    "name": parsed.fragment or f"ss_{host}",
                    "type": "ss",
                    "server": host,
                    "port": int(port),
                    "cipher": method,
                    "password": password
                }
                proxies.append(proxy)
            elif protocol == 'vless':
                # vless://uuid@host:port?encryption=none&security=tls&sni=example.com#name
                parsed = urlparse(link)
                userinfo, _, hostport = parsed.netloc.rpartition('@')
                host, port = hostport.split(':', 1) if ':' in hostport else (hostport, '443')
                query = parse_qs(parsed.query)
                
                proxy = {
                    "name": parsed.fragment or f"vless_{host}",
                    "type": "vless",
                    "server": host,
                    "port": int(port),
                    "uuid": userinfo,
                    "encryption": query.get('encryption', ['none'])[0],
                    "tls": 'security' in query and query['security'][0] == 'tls',
                    "servername": query.get('sni', [''])[0] if 'sni' in query else '',
                    "skip-cert-verify": True
                }
                proxies.append(proxy)
        except Exception as e:
            print(f"[WARN] 解析 {protocol} 链接失败: {e}")
            continue
    
    # 设置代理列表
    config["proxies"] = proxies
    
    # 更新代理组中的代理列表
    proxy_names = [proxy["name"] for proxy in proxies]
    for group in config["proxy-groups"]:
        if group["name"] == "自动选择" or group["name"] == "手动选择":
            group["proxies"] = proxy_names
    
    return config

def save_clash_config(file_path: str, config: Dict) -> None:
    """保存Clash配置到YAML文件"""
    import yaml
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)



# -------------------- 主功能 --------------------
def process_source(url: str, protocols: List[str]) -> Dict[str, Set[str]]:
    """处理订阅源，提取指定协议的链接"""
    print(f"[INFO] 正在处理订阅源: {url}")
    
    # 初始化结果字典
    result = {p: set() for p in protocols}
    
    try:
        # 获取订阅内容
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        
        # 检查是否为Base64编码的内容
        if is_base64(content):
            try:
                padding = len(content) % 4
                if padding > 0:
                    content += '=' * (4 - padding)
                decoded = base64.b64decode(content)
                content = decoded.decode('utf-8')
                print(f"[INFO] 成功解码Base64内容，长度: {len(content)} 字符")
            except Exception as e:
                print(f"[WARN] Base64解码失败: {e}")
                # 继续使用原始内容进行处理
        
        # 检查是否为Clash YAML配置
        if is_yaml_content(content):
            print(f"[INFO] 检测到Clash YAML配置格式")
            parsed_links = parse_clash_yaml(content)
            for link in parsed_links:
                protocol = get_protocol_from_link(link)
                if protocol and protocol in protocols:
                    result[protocol].add(link)
        else:
            # 尝试直接提取链接
            for protocol in protocols:
                pattern = get_protocol_pattern(protocol)
                if pattern:
                    matches = pattern.findall(content)
                    for match in matches:
                        full_link = match if isinstance(match, str) else match[0]
                        if is_valid_protocol_link(full_link, protocol):
                            result[protocol].add(full_link)
        
        # 统计结果
        for p in protocols:
            print(f"[INFO] 从订阅源 {url} 提取到 {len(result[p])} 条 {p.upper()} 链接")
            
    except Exception as e:
        print(f"[ERROR] 处理订阅源 {url} 时出错: {e}")
    
    return result

# 合并所有订阅源的结果
def merge_results(all_results: List[Dict[str, Set[str]]]) -> Dict[str, Set[str]]:
    """合并多个订阅源的结果"""
    merged = {}
    
    # 收集所有协议类型
    protocols = set()
    for result in all_results:
        protocols.update(result.keys())
    
    # 初始化合并后的结果
    for p in protocols:
        merged[p] = set()
    
    # 合并链接
    for result in all_results:
        for p in protocols:
            if p in result:
                merged[p].update(result[p])
    
    # 统计总结果
    for p in protocols:
        print(f"[INFO] 合并后总共有 {len(merged[p])} 条去重的 {p.upper()} 链接")
    
    return merged

# 主程序逻辑
def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='多协议订阅链接收集器')
    parser.add_argument('--sources', type=str, nargs='+', default=['https://1024day.com/link/7v1fZ0BcQn6Hd2zS?sub=1'], 
                        help='订阅源URL列表')
    parser.add_argument('--protocols', type=str, nargs='+', default=['vless', 'vmess', 'ss', 'ssr'], 
                        help='要提取的协议类型列表')
    parser.add_argument('--output-dir', type=str, default='output', 
                        help='输出目录')
    parser.add_argument('--speedtest', action='store_true', 
                        help='启用速度测试')
    parser.add_argument('--timeout', type=int, default=2, 
                        help='连接超时时间（秒）')
    parser.add_argument('--threads', type=int, default=10, 
                        help='测速线程数')
    parser.add_argument('--fast-threshold', type=float, default=100, 
                        help='快速节点阈值（毫秒）')
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 处理所有订阅源
    all_results = []
    for source in args.sources:
        result = process_source(source, args.protocols)
        all_results.append(result)
    
    # 合并结果
    merged = merge_results(all_results)
    
    # 对每个协议进行处理
    for protocol in merged:
        links = list(merged[protocol])
        if not links:
            print(f"[INFO] 没有找到 {protocol.upper()} 协议的链接")
            continue
        
        # 按照用户要求的格式保存结果
        # 原始链接文件
        raw_file = os.path.join(args.output_dir, f"{protocol}_raw.txt")
        # Base64编码的订阅文件
        sub_file = os.path.join(args.output_dir, f"{protocol}_base64.txt")
        
        if not args.speedtest:
            # 不进行测速，直接保存所有链接
            save_list(raw_file, sub_file, links)
            print(f"[INFO] 已保存所有 {protocol.upper()} 链接到 {raw_file} 和 {sub_file}")
        else:
            # 进行测速
            print(f"[INFO] 正在对 {len(links)} 条 {protocol.upper()} 链接进行并行测速...")
            
            # 准备测速任务
            tasks = []
            for link in links:
                tasks.append((link, protocol, args.timeout))
            
            # 并行测速
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                results = list(executor.map(lambda task: connect_check(*task), tasks))
            
            # 处理测速结果
            fast_links = []
            slow_links = []
            unreachable_links = []
            
            for link, (reachable, latency) in zip(links, results):
                if reachable:
                    if latency < args.fast_threshold:
                        fast_links.append(link)
                        print(f"[OK] 快速节点 ({latency:.1f}ms): {link[:100]}...")
                    else:
                        slow_links.append(link)
                        print(f"[OK] 低速节点 ({latency:.1f}ms): {link[:100]}...")
                else:
                    unreachable_links.append(link)
                    print(f"[FAIL] 不可达节点: {link[:100]}...")
            
            # 保存快速节点
            if fast_links:
                fast_raw_file = os.path.join(args.output_dir, f"{protocol}_fast_raw.txt")
                fast_sub_file = os.path.join(args.output_dir, f"{protocol}_fast_base64.txt")
                save_list(fast_raw_file, fast_sub_file, fast_links)
                print(f"[INFO] 已保存 {len(fast_links)} 条快速 {protocol.upper()} 链接到 {fast_raw_file} 和 {fast_sub_file}")
            
            # 保存低速节点
            if slow_links:
                slow_raw_file = os.path.join(args.output_dir, f"{protocol}_slow_raw.txt")
                slow_sub_file = os.path.join(args.output_dir, f"{protocol}_slow_base64.txt")
                save_list(slow_raw_file, slow_sub_file, slow_links)
                print(f"[INFO] 已保存 {len(slow_links)} 条低速 {protocol.upper()} 链接到 {slow_raw_file} 和 {slow_sub_file}")
            
            # 统计结果
            print(f"[INFO] {protocol.upper()} 协议测速结果: 快速={len(fast_links)}, 低速={len(slow_links)}, 不可达={len(unreachable_links)}")
        
        # 生成并保存多种工具可用的配置文件
        all_protocol_links = links
        if args.speedtest and fast_links:
            # 如果启用了测速，优先使用快速节点生成配置
            all_protocol_links = fast_links
        
        # 生成并保存Clash配置
        try:
            clash_config = create_clash_config(all_protocol_links)
            clash_file = os.path.join(args.output_dir, f"{protocol}_clash.yaml")
            save_clash_config(clash_file, clash_config)
            print(f"[INFO] 已生成 {protocol.upper()} Clash配置文件: {clash_file}")
        except Exception as e:
            print(f"[ERROR] 生成 {protocol.upper()} Clash配置失败: {e}")
        
        # 生成并保存V2Ray配置
        if protocol in ['vless', 'vmess', 'ss']:  # V2Ray主要支持这几种协议
            try:
                v2ray_config = create_v2ray_config(all_protocol_links)
                v2ray_file = os.path.join(args.output_dir, f"{protocol}_v2ray.json")
                save_v2ray_config(v2ray_file, v2ray_config)
                print(f"[INFO] 已生成 {protocol.upper()} V2Ray配置文件: {v2ray_file}")
            except Exception as e:
                print(f"[ERROR] 生成 {protocol.upper()} V2Ray配置失败: {e}")
        
    # 生成混合协议的Clash配置（包含所有快速节点）
    try:
        all_fast_links = []
        for protocol in merged:
            if args.speedtest:
                # 如果启用了测速，查找快速节点文件
                fast_raw_file = os.path.join(args.output_dir, f"{protocol}_fast_raw.txt")
                if os.path.exists(fast_raw_file):
                    with open(fast_raw_file, 'r', encoding='utf-8') as f:
                        all_fast_links.extend([line.strip() for line in f if line.strip()])
            else:
                # 否则使用所有节点
                raw_file = os.path.join(args.output_dir, f"{protocol}_raw.txt")
                if os.path.exists(raw_file):
                    with open(raw_file, 'r', encoding='utf-8') as f:
                        all_fast_links.extend([line.strip() for line in f if line.strip()])
        
        if all_fast_links:
            mixed_clash_config = create_clash_config(all_fast_links)
            mixed_clash_file = os.path.join(args.output_dir, "all_protocols_clash.yaml")
            save_clash_config(mixed_clash_file, mixed_clash_config)
            print(f"[INFO] 已生成混合协议Clash配置文件: {mixed_clash_file}")
    except Exception as e:
        print(f"[ERROR] 生成混合协议Clash配置失败: {e}")

if __name__ == '__main__':
    main()

# -------------------- 测速功能 --------------------
def connect_check(link: str, protocol: str, timeout: float = 2) -> Tuple[bool, float]:
    """并行测速用：返回 (是否可连, 耗时毫秒)"""
    try:
        # 尝试从链接中提取主机和端口
        host, port = None, None
        
        # 处理不同协议的链接格式
        if protocol == 'vless':
            parsed = urlparse(link)
            if '@' in parsed.netloc:
                _, _, hostport = parsed.netloc.rpartition('@')
                if ':' in hostport:
                    host, port = hostport.split(':', 1)
                    port = int(port)
        elif protocol == 'vmess':
            try:
                if not link.startswith("vmess://"):
                    return False, float("inf")
                vmess_data = link[8:]
                # 处理可能缺失的padding
                padding = len(vmess_data) % 4
                if padding > 0:
                    vmess_data += '=' * (4 - padding)
                decoded = base64.b64decode(vmess_data)
                vmess_config = json.loads(decoded.decode())
                host = vmess_config.get('add')
                port = vmess_config.get('port')
                # 确保端口是整数类型
                if port and isinstance(port, str) and port.isdigit():
                    port = int(port)
            except Exception as e:
                print(f"[DEBUG] 解析VMess链接失败: {e}")
        elif protocol == 'ss':
            try:
                if not link.startswith("ss://"):
                    return False, float("inf")
                # SS链接格式: ss://base64(加密方式:密码)@服务器地址:端口
                ss_data = link[5:]
                if '@' in ss_data:
                    _, _, server_part = ss_data.rpartition('@')
                    if ':' in server_part:
                        host_part, port_part = server_part.split(':', 1)
                        host = host_part.split('#')[0]  # 移除可能的备注部分
                        try:
                            port = int(port_part.split('#')[0])  # 移除可能的备注部分
                        except ValueError:
                            pass
            except Exception as e:
                print(f"[DEBUG] 解析SS链接失败: {e}")
        elif protocol == 'ssr':
            try:
                if not link.startswith("ssr://"):
                    return False, float("inf")
                # SSR链接格式: ssr://base64(host:port:protocol:method:obfs:password_base64/?params)
                ssr_data = link[6:]
                padding = len(ssr_data) % 4
                if padding > 0:
                    ssr_data += '=' * (4 - padding)
                decoded = base64.b64decode(ssr_data).decode('utf-8', errors='ignore')
                # SSR链接使用冒号分隔的字段，格式较为固定
                ssr_parts = decoded.split(':')
                if len(ssr_parts) >= 6:
                    host = ssr_parts[0]
                    try:
                        port = int(ssr_parts[1])
                    except ValueError:
                        pass
            except Exception as e:
                print(f"[DEBUG] 解析SSR链接失败: {e}")
        
        # 如果无法从链接中提取，尝试使用一些常见的默认解析方法
        if not host or not port:
            # 对于可能的直连格式（如Clash提取的非标准格式）
            # 尝试使用正则表达式提取主机和端口
            host_port_match = re.search(r'([a-zA-Z0-9\.-]+):(\d{1,5})', str(link))
            if host_port_match:
                host = host_port_match.group(1)
                try:
                    port = int(host_port_match.group(2))
                except ValueError:
                    pass
        
        # 验证端口范围
        if not host or not port or port <= 0 or port > 65535:
            return False, float("inf")
        
        # 执行TCP连接测试
        start = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        elapsed = (time.perf_counter() - start) * 1000  # 转换为毫秒
        return True, elapsed
    except Exception as e:
        print(f"[DEBUG] 测速失败: {e}")
        return False, float("inf")