import os
import json
import base64
import re
import sys
import html
import urllib.parse
from urllib.parse import urlparse, parse_qs

def clean_tag(tag):
    """پاکسازی تگ و تبدیل کدهای Unicode به کاراکترهای خوانا"""
    # تبدیل کدهای HTML به کاراکتر (مثل &#x1F1E8;&#x1F1F3; به 🇨🇳)
    cleaned = html.unescape(tag)
    
    # حذف کاراکترهای غیر ضروری
    cleaned = re.sub(r'§\s*\d+', '', cleaned)  # حذف § و اعداد بعدی
    
    # جایگزینی کدهای یونیکد با کاراکترهای واقعی
    cleaned = bytes(cleaned, 'utf-8').decode('unicode_escape')
    
    # حذف کاراکترهای کنترل
    cleaned = ''.join(c for c in cleaned if ord(c) > 31)
    
    return cleaned.strip()

def vmess_to_singbox(url):
    try:
        b64_data = url.replace("vmess://", "")
        pad = len(b64_data) % 4
        if pad: b64_data += "=" * (4 - pad)
        json_str = base64.b64decode(b64_data).decode('utf-8')
        vmess_config = json.loads(json_str)
        
        # پاکسازی تگ
        tag = clean_tag(vmess_config.get("ps", "vmess-connection"))
        
        # ساختار اصلی
        config = {
            "type": "vmess",
            "tag": tag,
            "server": vmess_config["add"],
            "server_port": int(vmess_config["port"]),
            "uuid": vmess_config["id"],
            "security": vmess_config.get("scy", "auto"),
            "alter_id": vmess_config.get("aid", 0)
        }
        
        # افزودن TLS اگر نیاز باشد
        tls = vmess_config.get("tls", "")
        if tls == "tls":
            config["tls"] = {
                "enabled": True,
                "server_name": vmess_config.get("sni", "")
            }
        
        # افزودن بخش transport فقط اگر tcp نباشد
        net = vmess_config.get("net", "tcp")
        if net != "tcp":
            transport = {"type": net}
            
            if net == "ws":
                # تنظیمات WebSocket
                path = vmess_config.get("path", "")
                if path:
                    transport["path"] = path
                
                headers = vmess_config.get("headers", {})
                if headers:
                    transport["headers"] = headers
            
            config["transport"] = transport
        
        return config
    except Exception as e:
        print(f"VMess conversion error: {str(e)}")
        return None

def vless_to_singbox(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        
        # پاکسازی تگ از fragment
        tag = clean_tag(parsed.fragment) if parsed.fragment else "vless-connection"
        
        # ساختار اصلی
        config = {
            "type": "vless",
            "tag": tag,
            "server": parsed.hostname,
            "server_port": int(parsed.port),
            "uuid": parsed.username,
            "flow": query.get("flow", [""])[0]
        }
        
        # افزودن TLS
        tls_enabled = query.get("security", ["tls"])[0] == "tls"
        if tls_enabled:
            config["tls"] = {
                "enabled": True,
                "server_name": query.get("sni", [""])[0]
            }
        
        # افزودن بخش transport
        transport_type = query.get("type", ["tcp"])[0]
        transport = {"type": transport_type}
        
        if transport_type == "ws":
            # تنظیمات WebSocket
            path = query.get("path", [""])[0]
            if path:
                transport["path"] = path
            
            headers_host = query.get("host", [""])[0]
            if headers_host:
                transport["headers"] = {
                    "Host": headers_host
                }
        
        config["transport"] = transport
        
        return config
    except Exception as e:
        print(f"VLESS conversion error: {str(e)}")
        return None

def ss_to_singbox(url):
    try:
        # فرمت: ss://method:password@host:port#tag
        parsed = urlparse(url)
        tag = clean_tag(parsed.fragment) if parsed.fragment else "ss-connection"
        
        # استخراج اطلاعات کاربری
        userinfo_b64 = parsed.netloc.split('@')[0]
        pad = len(userinfo_b64) % 4
        if pad: userinfo_b64 += "=" * (4 - pad)
        userinfo = base64.b64decode(userinfo_b64).decode('utf-8')
        method, password = userinfo.split(':', 1)
        
        return {
            "type": "shadowsocks",
            "tag": tag,
            "server": parsed.hostname,
            "server_port": int(parsed.port),
            "method": method,
            "password": password
        }
    except Exception as e:
        print(f"Shadowsocks conversion error: {str(e)}")
        return None

def trojan_to_singbox(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        
        # پاکسازی تگ
        tag = clean_tag(parsed.fragment) if parsed.fragment else "trojan-connection"
        
        # ساختار اصلی
        config = {
            "type": "trojan",
            "tag": tag,
            "server": parsed.hostname,
            "server_port": int(parsed.port),
            "password": parsed.username
        }
        
        # افزودن TLS
        tls_enabled = query.get("security", ["tls"])[0] == "tls"
        if tls_enabled:
            config["tls"] = {
                "enabled": True,
                "server_name": query.get("sni", [""])[0]
            }
        
        # افزودن بخش transport
        transport_type = query.get("type", ["tcp"])[0]
        transport = {"type": transport_type}
        
        if transport_type == "ws":
            # تنظیمات WebSocket
            path = query.get("path", [""])[0]
            if path:
                transport["path"] = path
            
            headers_host = query.get("host", [""])[0]
            if headers_host:
                transport["headers"] = {
                    "Host": headers_host
                }
        
        config["transport"] = transport
        
        return config
    except Exception as e:
        print(f"Trojan conversion error: {str(e)}")
        return None

def hysteria_to_singbox(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        
        # پاکسازی تگ
        tag = clean_tag(parsed.fragment) if parsed.fragment else "hysteria-connection"
        
        # ساختار اصلی
        config = {
            "type": "hysteria",
            "tag": tag,
            "server": parsed.hostname,
            "server_port": int(parsed.port),
            "up_mbps": 100,
            "down_mbps": 100,
            "obfs": query.get("obfs", [""])[0],
            "auth_str": query.get("auth", [""])[0]
        }
        
        # افزودن TLS
        insecure = query.get("insecure", ["0"])[0] == "1"
        config["tls"] = {
            "enabled": True,
            "insecure": insecure,
            "server_name": query.get("sni", [""])[0]
        }
        
        return config
    except Exception as e:
        print(f"Hysteria conversion error: {str(e)}")
        return None

def process_file(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    configs = []
    
    # پردازش VMess
    for url in re.findall(r'vmess://[A-Za-z0-9+/=]+', content):
        config = vmess_to_singbox(url)
        if config:
            configs.append(config)
    
    # پردازش VLESS
    for url in re.findall(r'vless://[^\s]+', content):
        config = vless_to_singbox(url)
        if config:
            configs.append(config)
    
    # پردازش Shadowsocks
    for url in re.findall(r'ss://[^\s]+', content):
        config = ss_to_singbox(url)
        if config:
            configs.append(config)
    
    # پردازش Trojan
    for url in re.findall(r'trojan://[^\s]+', content):
        config = trojan_to_singbox(url)
        if config:
            configs.append(config)
    
    # پردازش Hysteria
    for url in re.findall(r'hysteria://[^\s]+', content):
        config = hysteria_to_singbox(url)
        if config:
            configs.append(config)
    
    # پردازش Hysteria2
    for url in re.findall(r'hysteria2://[^\s]+', content):
        # Hysteria2 از همان فرمت Hysteria استفاده می‌کند
        config = hysteria_to_singbox(url.replace("hysteria2://", "hysteria://"))
        if config:
            configs.append(config)
    
    if configs:
        output_file = os.path.join('outputs', os.path.basename(input_file).replace('.txt', '.json'))
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "outbounds": configs
            }, f, indent=2, ensure_ascii=False)
        print(f"Generated {output_file} with {len(configs)} configs")
    else:
        print(f"No valid configs found in {input_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("Usage: python singbox_converter.py <input_file>")
        sys.exit(1)
