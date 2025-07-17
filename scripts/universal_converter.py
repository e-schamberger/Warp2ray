import os
import json
import base64
import re
import sys
from urllib.parse import urlparse, parse_qs
import subprocess

# Enhanced protocol patterns
PROTOCOL_PATTERNS = {
    'vmess': r'vmess://[A-Za-z0-9+/=]+',
    'vless': r'vless://[^\s]+',
    'ss': r'ss://[^\s]+',
    'trojan': r'trojan://[^\s]+', 
    'hysteria': r'hysteria://[^\s]+',
    'hysteria2': r'hysteria2://[^\s]+'
}

def decode_vmess(url):
    try:
        b64_data = url.replace("vmess://", "").strip()
        # Add padding if needed
        pad = len(b64_data) % 4
        if pad: b64_data += "=" * (4 - pad)
        json_str = base64.b64decode(b64_data).decode('utf-8')
        return json.loads(json_str)
    except Exception as e:
        print(f"VMess decode error: {str(e)}")
        return None

def parse_vless(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        return {
            "protocol": "vless",
            "address": parsed.hostname,
            "port": parsed.port or 443,
            "id": parsed.username,
            **{k: v[0] for k, v in query.items()}
        }
    except Exception as e:
        print(f"VLESS parse error: {str(e)}")
        return None

def convert_to_xray(config):
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
        return config  # Fallback to original config
    except Exception as e:
        print(f"Xray conversion error: {str(e)}")
        return config  # Fallback to original config

def process_file(input_file):
    print(f"\nProcessing {input_file}...")
    
    # Read file content
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        if not content.strip():
            print("Error: Empty input file")
            return
    except Exception as e:
        print(f"File read error: {str(e)}")
        return

    # Extract and process all configs
    configs = []
    for proto, pattern in PROTOCOL_PATTERNS.items():
        matches = re.findall(pattern, content)
        print(f"Found {len(matches)} {proto.upper()} configs")
        
        for url in matches:
            try:
                # Decode based on protocol
                if proto == 'vmess':
                    config = decode_vmess(url)
                elif proto == 'vless':
                    config = parse_vless(url)
                else:
                    config = {"protocol": proto, "url": url}
                
                if config:
                    # Convert to Xray format
                    xray_config = convert_to_xray(config)
                    if xray_config:
                        configs.append(xray_config)
            except Exception as e:
                print(f"Error processing {url[:50]}...: {str(e)}")
    
    # Save results
    if configs:
        output_file = os.path.join('outputs', 
                                 os.path.basename(input_file).replace('.txt', '.json'))
        with open(output_file, 'w') as f:
            json.dump(configs, f, indent=2)
        print(f"Success: Saved {len(configs)} configs to {output_file}")
    else:
        print("Warning: No valid configs found in this file")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("Error: Please provide an input file")
        print("Usage: python universal_converter.py <input_file>")
        sys.exit(1)
