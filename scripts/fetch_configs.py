import os
import requests
from pathlib import Path

def download_configs():
    # Create directories
    Path("inputs").mkdir(exist_ok=True)
    Path("raw_configs").mkdir(exist_ok=True)
    
    # Create default links file if missing
    if not os.path.exists("inputs/links.txt"):
        print("Creating default links.txt")
        with open("inputs/links.txt", "w") as f:
            f.write("https://raw.githubusercontent.com/lagzian/new-configs-collector/main/countries/hr/mixed\n")
            f.write("https://raw.githubusercontent.com/hiddify/hiddify-config/main/sample_configs/vmess.txt\n")
        return True

    # Read links
    with open("inputs/links.txt", "r") as f:
        links = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    
    # Download each config
    for i, url in enumerate(links):
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # Save content
            output_file = f"raw_configs/config_{i}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Saved {output_file} ({len(response.text)} characters)")
            
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
    
    return True

if __name__ == "__main__":
    download_configs()
