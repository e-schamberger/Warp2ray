import os
import json
import base64
import re
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Create output folder
Path("outputs").mkdir(exist_ok=True)

def vmess_to_json(vmess_url):
    """Convert vmess URL to JSON"""
    b64_data = vmess_url.replace("vmess://", "")
    # Add padding if needed
    pad = len(b64_data) % 4
    if pad:
        b64_data += "=" * (4 - pad)
    json_str = base64.b64decode(b64_data).decode('utf-8')
    return json.loads(json_str)

def vless_to_json(vless_url):
    """Convert vless URL to JSON"""
    parsed = urlparse(vless_url)
    query = parse_qs(parsed.query)
    
    return {
        "protocol": "vless",
        "address": parsed.hostname,
        "port": parsed.port,
        "id": parsed.username,
        "flow": query.get('flow', [''])[0],
        "encryption": query.get('encryption', ['none'])[0],
        "security": query.get('security', ['tls'])[0],
        "type": query.get('type', ['tcp'])[0],
        "sni": query.get('sni', [''])[0],
        "path": query.get('path', [''])[0],
        "host": query.get('host', [''])[0]
    }

def ss_to_json(ss_url):
    """Convert ss URL to JSON"""
    # Simple implementation - you might need to enhance this
    return {
        "protocol": "ss",
        "url": ss_url
    }

def trojan_to_json(trojan_url):
    """Convert trojan URL to JSON"""
    parsed = urlparse(trojan_url)
    query = parse_qs(parsed.query)
    
    return {
        "protocol": "trojan",
        "address": parsed.hostname,
        "port": parsed.port,
        "password": parsed.username,
        "security": query.get('security', ['tls'])[0],
        "sni": query.get('sni', [''])[0],
        "type": query.get('type', ['tcp'])[0],
        "host": query.get('host', [''])[0],
        "path": query.get('path', [''])[0]
    }

def detect_and_convert(link):
    """Detect protocol and convert to JSON"""
    if link.startswith("vmess://"):
        return vmess_to_json(link)
    elif link.startswith("vless://"):
        return vless_to_json(link)
    elif link.startswith("ss://"):
        return ss_to_json(link)
    elif link.startswith("trojan://"):
        return trojan_to_json(link)
    else:
        return {"error": "Unsupported protocol", "link": link}

def process_files():
    """Process all raw config files"""
    for filename in os.listdir("raw_configs"):
        if not filename.endswith(".txt"):
            continue
            
        with open(os.path.join("raw_configs", filename), "r") as f:
            content = f.read()
            
        # Extract config links
        pattern = r'(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)'
        links = re.findall(pattern, content)
        
        configs = []
        for link in links:
            try:
                config = detect_and_convert(link)
                configs.append(config)
            except Exception as e:
                print(f"Error processing {link}: {str(e)}")
                configs.append({
                    "error": str(e),
                    "raw_link": link
                })
        
        # Save as JSON
        output_path = os.path.join("outputs", f"{filename.replace('.txt', '.json')}")
        with open(output_path, "w") as f:
            json.dump(configs, f, indent=2)
            
        print(f"Generated: {output_path} with {len(configs)} configs")

if __name__ == "__main__":
    process_files()

def process_files():
    if not os.path.exists("raw_configs"):
        print("Error: raw_configs folder not found!")
        return
        
    # Rest of the function...
