import os
import json
import base64
import re
from pathlib import Path

def vmess_to_json(vmess_url):
    """Convert vmess URL to JSON"""
    try:
        b64_data = vmess_url.replace("vmess://", "")
        json_str = base64.b64decode(b64_data).decode('utf-8')
        return json.loads(json_str)
    except Exception as e:
        print(f"Error decoding vmess: {str(e)}")
        return None

def process_files():
    # Create output directory
    Path("outputs").mkdir(exist_ok=True)
    
    # Check raw_configs exists and not empty
    if not os.path.exists("raw_configs") or not os.listdir("raw_configs"):
        print("Error: No config files found in raw_configs")
        return
    
    # Process each file
    for filename in os.listdir("raw_configs"):
        if not filename.endswith(".txt"):
            continue
            
        input_path = os.path.join("raw_configs", filename)
        output_path = os.path.join("outputs", f"hiddify_{filename.replace('.txt', '.json')}")
        
        try:
            with open(input_path, "r") as f:
                content = f.read()
            
            # Extract all config links
            config_links = re.findall(
                r'(vmess://[^\s]+|vless://[^\s]+|trojan://[^\s]+|ss://[^\s]+)',
                content
            )
            
            if not config_links:
                print(f"No config links found in {filename}")
                continue
                
            # Convert each link
            converted_configs = []
            for link in config_links:
                if link.startswith("vmess://"):
                    config = vmess_to_json(link)
                    if config:
                        converted_configs.append({
                            "type": "vmess",
                            "config": config
                        })
                # Add other protocols here...
            
            # Save to output file
            if converted_configs:
                with open(output_path, "w") as f:
                    json.dump(converted_configs, f, indent=2)
                print(f"Generated {output_path} with {len(converted_configs)} configs")
            else:
                print(f"No valid configs found in {filename}")
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    process_files()
