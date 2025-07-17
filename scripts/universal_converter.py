import os
import json
import base64
import re
import sys
from urllib.parse import urlparse, parse_qs
import subprocess

PROTOCOL_HANDLERS = {
    'vmess': lambda url: handle_vmess(url),
    'vless': lambda url: handle_vless(url),
    'ss': lambda url: handle_ss(url),
    'trojan': lambda url: handle_trojan(url),
    'hysteria': lambda url: handle_hysteria(url),
    'hysteria2': lambda url: handle_hysteria2(url)
}

def handle_vmess(url):
    try:
        b64_data = url.replace("vmess://", "")
        pad = len(b64_data) % 4
        if pad: b64_data += "=" * (4 - pad)
        json_str = base64.b64decode(b64_data).decode('utf-8')
        return json.loads(json_str)
    except Exception as e:
        print(f"VMess decode error: {str(e)}")
        return None

def handle_vless(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        return {
            "protocol": "vless",
            "address": parsed.hostname,
            "port": parsed.port,
            "id": parsed.username,
            **{k: v[0] for k, v in query.items()}
        }
    except Exception as e:
        print(f"VLESS parse error: {str(e)}")
        return None

def handle_ss(url):
    try:
        # Basic ShadowSocks handler
        return {"protocol": "ss", "url": url}
    except Exception as e:
        print(f"SS parse error: {str(e)}")
        return None

def handle_trojan(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        return {
            "protocol": "trojan",
            "address": parsed.hostname,
            "port": parsed.port,
            "password": parsed.username,
            **{k: v[0] for k, v in query.items()}
        }
    except Exception as e:
        print(f"Trojan parse error: {str(e)}")
        return None

def handle_hysteria(url):
    try:
        # Hysteria v1 handler
        return {"protocol": "hysteria", "url": url}
    except Exception as e:
        print(f"Hysteria parse error: {str(e)}")
        return None

def handle_hysteria2(url):
    try:
        # Hysteria v2 handler
        return {"protocol": "hysteria2", "url": url}
    except Exception as e:
        print(f"Hysteria2 parse error: {str(e)}")
        return None

def convert_to_xray_format(config):
    """Convert config using Xray-core"""
    try:
        result = subprocess.run(
            ['xray', 'api', 'convert', '-json', json.dumps(config)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        print(f"Xray conversion failed: {result.stderr}")
        return None
    except Exception as e:
        print(f"Xray conversion error: {str(e)}")
        return None

def process_file(input_file):
    with open(input_file, 'r') as f:
        content = f.read()
    
    configs = []
    for proto in PROTOCOL_HANDLERS:
        pattern = rf'({proto}://[^\s]+)'
        for url in re.findall(pattern, content):
            try:
                handler = PROTOCOL_HANDLERS[proto]
                config = handler(url)
                if config:
                    xray_config = convert_to_xray_format(config)
                    if xray_config:
                        configs.append(xray_config)
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")
    
    if configs:
        output_file = os.path.join('outputs', os.path.basename(input_file).replace('.txt', '.json'))
        with open(output_file, 'w') as f:
            json.dump(configs, f, indent=2)
        print(f"Generated {output_file} with {len(configs)} configs")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("Usage: python universal_converter.py <input_file>")
