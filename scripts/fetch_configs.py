import os
import requests
from pathlib import Path

# Create required folders
Path("inputs").mkdir(exist_ok=True)
Path("raw_configs").mkdir(exist_ok=True)

def download_configs():
    # Read links from inputs/links.txt
    with open("inputs/links.txt", "r") as f:
        links = [l.strip() for l in f.readlines() if l.strip()]
    
    for i, url in enumerate(links):
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Save raw content
            with open(f"raw_configs/config_{i}.txt", "w") as f:
                f.write(response.text)
                
            print(f"Downloaded: {url}")
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")

if __name__ == "__main__":
    download_configs()
