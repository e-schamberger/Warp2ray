import os
import json
import base64
import re
from urllib.parse import urlparse, parse_qs
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

def convert_to_hiddify_format(config):
    """Convert standard config to Hiddify format"""
    hiddify_config = {
        "version": 1,
        "domains": [],
        "proxies": []
    }
    
    # Add your conversion logic here
    if config.get("protocol") == "vmess":
        hiddify_config["proxies"].append({
            "type": "vmess",
            "name": config.get("ps", "vmess-connection"),
            "server": config.get("add"),
            "port": config.get("port"),
            "uuid": config.get("id"),
            "alterId": config.get("aid", 0),
            "security": config.get("scy", "auto"),
            "network": config.get("net"),
            "tls": config.get("tls") == "tls"
        })
    
    # Add other protocol conversions (vless, trojan, etc.)
    
    return hiddify_config

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
        
        hiddify_configs = []
        for link in links:
            try:
                # First convert to standard format
                if link.startswith("vmess://"):
                    config = vmess_to_json(link)
                elif link.startswith("vless://"):
                    config = vless_to_json(link)
                # ... other protocols
                
                # Then convert to Hiddify format
                hiddify_config = convert_to_hiddify_format(config)
                hiddify_configs.append(hiddify_config)
                
            except Exception as e:
                print(f"Error processing {link}: {str(e)}")
        
        # Save as JSON
        output_path = os.path.join("outputs", f"hiddify_{filename.replace('.txt', '.json')}")
        with open(output_path, "w") as f:
            json.dump(hiddify_configs, f, indent=2)
            
        print(f"Generated Hiddify config: {output_path}")

if __name__ == "__main__":
    process_files()
