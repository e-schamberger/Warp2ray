import os
import json
import base64
import re
import sys
import html
import urllib.parse
from urllib.parse import urlparse, parse_qs, unquote

def clean_tag(tag):
    """پاکسازی و تبدیل تگ به فرمت صحیح"""
    if not tag:
        return ""
    
    # تبدیل کدهای URL-encoded به کاراکترهای خوانا
    decoded = unquote(tag)
    
    # تبدیل کدهای HTML به کاراکتر (مثل &#x1F1E8;&#x1F1F3; به 🇨🇳)
    cleaned = html.unescape(decoded)
    
    # حذف کاراکترهای کنترل و نمادهای غیر ضروری
    cleaned = ''.join(c for c in cleaned if ord(c) > 31 and c not in ['§', '|'])
    
    # حذف اعداد انتهایی
    cleaned = re.sub(r'\s*\d+$', '', cleaned)
    
    return cleaned.strip()

def extract_params(url):
    """استخراج پارامترها از URL با مدیریت کاراکترهای خاص"""
    parsed = urlparse(url)
    query = {}
    
    # پارامترهای اصلی
    for key, values in parse_qs(parsed.query).items():
        # دیکد کردن مقادیر با مدیریت کاراکترهای خاص
        decoded_values = [unquote(v) for v in values]
        query[key] = decoded_values[0] if len(decoded_values) == 1 else decoded_values
    
    # fragment (تگ)
    tag = clean_tag(parsed.fragment) if parsed.fragment else ""
    
    return {
        "hostname": parsed.hostname,
        "port": parsed.port,
        "username": parsed.username,
        "path": unquote(parsed.path) if parsed.path else "",
        "query": query,
        "tag": tag
    }

def vmess_to_singbox(url):
    try:
        b64_data = url.replace("vmess://", "")
        pad = len(b64_data) % 4
        if pad: b64_data += "=" * (4 - pad)
        json_str = base64.b64decode(b64_data).decode('utf-8')
        vmess = json.loads(json_str)
        
        # پاکسازی تگ
        tag = clean_tag(vmess.get("ps", "vmess-connection"))
        
        # ساختار اصلی
        config = {
            "type": "vmess",
            "tag": tag,
            "server": vmess["add"],
            "server_port": int(vmess["port"]),
            "uuid": vmess["id"],
            "security": vmess.get("scy", "auto"),
            "alter_id": vmess.get("aid", 0),
            "authenticated_length": True,
            "packet_encoding": "xudp"
        }
        
        # افزودن TLS اگر نیاز باشد
        tls = vmess.get("tls", "")
        if tls == "tls":
            config["tls"] = {
                "enabled": True,
                "server_name": vmess.get("sni", "")
            }
        
        # افزودن بخش transport فقط برای انواع غیر tcp
        net = vmess.get("net", "tcp")
        if net != "tcp":
            transport = {"type": net}
            
            if net == "ws":
                # تنظیمات WebSocket
                path = vmess.get("path", "")
                if path:
                    transport["path"] = unquote(path)
                
                headers = vmess.get("headers", {})
                if headers:
                    transport["headers"] = headers
            
            config["transport"] = transport
        
        return config
    except Exception as e:
        print(f"VMess conversion error: {str(e)}")
        return None

def vless_to_singbox(url):
    try:
        params = extract_params(url)
        
        # ساختار اصلی
        config = {
            "type": "vless",
            "tag": params["tag"],
            "server": params["hostname"],
            "server_port": int(params["port"]),
            "uuid": params["username"],
            "packet_encoding": "xudp"
        }
        
        # افزودن flow اگر وجود داشته باشد
        if params["query"].get("flow"):
            config["flow"] = params["query"]["flow"]
        
        # افزودن TLS
        tls_enabled = params["query"].get("security", ["tls"])[0] == "tls"
        if tls_enabled:
            config["tls"] = {
                "enabled": True,
                "server_name": params["query"].get("sni", [""])[0]
            }
        
        # افزودن بخش transport
        transport_type = params["query"].get("type", ["tcp"])[0]
        transport = {"type": transport_type}
        
        if transport_type == "ws":
            # تنظیمات WebSocket
            path = params["query"].get("path", [""])[0]
            if path:
                transport["path"] = unquote(path)
            
            headers_host = params["query"].get("host", [""])[0]
            if headers_host:
                transport["headers"] = {
                    "Host": unquote(headers_host)
                }
            
            # افزودن early_data_header_name اگر وجود داشته باشد
            if params["query"].get("early_data_header_name"):
                transport["early_data_header_name"] = params["query"]["early_data_header_name"]
        
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
        
        # شناسایی روش رمزنگاری و پسورد
        if ':' in userinfo:
            method, password = userinfo.split(':', 1)
        else:
            method = userinfo
            password = ""
        
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
        params = extract_params(url)
        
        # ساختار اصلی
        config = {
            "type": "trojan",
            "tag": params["tag"],
            "server": params["hostname"],
            "server_port": int(params["port"]),
            "password": params["username"]
        }
        
        # افزودن TLS
        tls_enabled = params["query"].get("security", ["tls"])[0] == "tls"
        if tls_enabled:
            tls_config = {
                "enabled": True,
                "server_name": params["query"].get("sni", [""])[0]
            }
            
            # افزودن تنظیمات uTLS اگر وجود داشته باشد
            if params["query"].get("fp") or params["query"].get("fingerprint"):
                fingerprint = params["query"].get("fp", params["query"].get("fingerprint", [""]))[0]
                tls_config["utls"] = {
                    "enabled": True,
                    "fingerprint": fingerprint
                }
            
            config["tls"] = tls_config
        
        # افزودن بخش transport
        transport_type = params["query"].get("type", ["tcp"])[0]
        transport = {"type": transport_type}
        
        if transport_type == "ws":
            # تنظیمات WebSocket
            path = params["query"].get("path", [""])[0]
            if path:
                transport["path"] = unquote(path)
            
            headers_host = params["query"].get("host", [""])[0]
            if headers_host:
                transport["headers"] = {
                    "Host": unquote(headers_host)
                }
            
            # افزودن early_data_header_name اگر وجود داشته باشد
            if params["query"].get("early_data_header_name"):
                transport["early_data_header_name"] = params["query"]["early_data_header_name"]
        
        config["transport"] = transport
        
        return config
    except Exception as e:
        print(f"Trojan conversion error: {str(e)}")
        return None

def hysteria_to_singbox(url, is_v2=False):
    try:
        params = extract_params(url)
        protocol = "hysteria2" if is_v2 else "hysteria"
        
        # ساختار اصلی
        config = {
            "type": protocol,
            "tag": params["tag"],
            "server": params["hostname"],
            "server_port": int(params["port"]),
            "up_mbps": 100,
            "down_mbps": 100
        }
        
        # افزودن obfs اگر وجود داشته باشد
        obfs_password = params["query"].get("obfs-password", params["query"].get("obfsPassword", [""]))[0]
        if obfs_password:
            config["obfs"] = {
                "type": params["query"].get("obfs", ["salamander"])[0],
                "password": unquote(obfs_password)
            }
        
        # افزودن پسورد اصلی
        if params["username"]:
            config["password"] = unquote(params["username"])
        
        # افزودن TLS
        insecure = params["query"].get("insecure", ["0"])[0] == "1"
        config["tls"] = {
            "enabled": True,
            "insecure": insecure,
            "server_name": params["query"].get("sni", [""])[0]
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
        config = hysteria_to_singbox(url, is_v2=True)
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
