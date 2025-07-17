import os
import json
import base64
import re
import sys
from urllib.parse import urlparse, parse_qs
import yaml
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
    b64_data = url.replace("vmess://", "")
    pad = len(b64_data) % 4
    if pad: b64_data += "=" * (4 - pad)
    json_str = base64.b64decode(b64_data).decode('utf-8')
    return json.loads(json_str)

def handle_vless(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return {
        "protocol": "vless",
        "address": parsed.hostname,
        "port": parsed.port,
        "id": parsed.username,
        **{k: v[0] for k, v in query.items()}
    }

def handle_ss(url):
    # ShadowSocks handler
    return {"protocol": "ss", "url": url}

def handle_trojan(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return {
        "protocol": "trojan",
        "address": parsed.hostname,
        "port": parsed.port,
        "password": parsed.username,
        **{k: v[0] for k, v in query.items()}
    }

def handle_hysteria(url):
    # Hysteria v1 handler
    return {"protocol": "hysteria", "url": url}

def handle_hysteria2(url):
    # Hysteria v2 handler
    return {"protocol": "hysteria2", "url": url}

def convert_to_v2ray_format(config):
    """Convert any config to v2ray standard format using v2ray-core"""
    try:
        result = subprocess.run(
            ['v2ray', 'convert', json.dumps(config)],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Conversion error: {str(e)}")
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
                    v2ray_config = convert_to_v2ray_format(config)
                    if v2ray_config:
                        configs.append(v2ray_config)
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
