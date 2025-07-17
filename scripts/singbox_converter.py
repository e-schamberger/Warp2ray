import os
import json
import base64
import re
import sys
from urllib.parse import urlparse, parse_qs

def vmess_to_singbox(url):
    try:
        b64_data = url.replace("vmess://", "")
        pad = len(b64_data) % 4
        if pad: b64_data += "=" * (4 - pad)
        json_str = base64.b64decode(b64_data).decode('utf-8')
        vmess_config = json.loads(json_str)
        
        return {
            "type": "vmess",
            "tag": vmess_config.get("ps", "vmess-connection"),
            "server": vmess_config["add"],
            "server_port": int(vmess_config["port"]),
            "uuid": vmess_config["id"],
            "security": vmess_config.get("scy", "auto"),
            "transport": {
                "type": vmess_config.get("net", "tcp")
            }
        }
    except Exception as e:
        print(f"VMess conversion error: {str(e)}")
        return None

def vless_to_singbox(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        
        return {
            "type": "vless",
            "tag": "vless-connection",
            "server": parsed.hostname,
            "server_port": int(parsed.port),
            "uuid": parsed.username,
            "flow": query.get("flow", [""])[0],
            "tls": {
                "enabled": True,
                "server_name": query.get("sni", [""])[0]
            },
            "transport": {
                "type": query.get("type", ["tcp"])[0],
                "path": query.get("path", [""])[0],
                "host": query.get("host", [""])[0]
            }
        }
    except Exception as e:
        print(f"VLESS conversion error: {str(e)}")
        return None

def process_file(input_file):
    with open(input_file, 'r') as f:
        content = f.read()
    
    configs = []
    
    # Process VMess links
    for url in re.findall(r'vmess://[A-Za-z0-9+/=]+', content):
        config = vmess_to_singbox(url)
        if config:
            configs.append(config)
    
    # Process VLESS links
    for url in re.findall(r'vless://[^\s]+', content):
        config = vless_to_singbox(url)
        if config:
            configs.append(config)
    
    # Add other protocols here (SS, Trojan, Hysteria, etc.)
    
    if configs:
        output_file = os.path.join('outputs', os.path.basename(input_file).replace('.txt', '.json'))
        with open(output_file, 'w') as f:
            json.dump({
                "outbounds": configs
            }, f, indent=2)
        print(f"Generated {output_file} with {len(configs)} configs")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("Usage: python singbox_converter.py <input_file>")
