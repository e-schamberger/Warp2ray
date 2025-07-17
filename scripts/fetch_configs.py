import os
import requests
from pathlib import Path

def download_configs():
    # Create directories
    Path("inputs").mkdir(exist_ok=True)
    Path("raw_configs").mkdir(exist_ok=True)
    
    # Verify links.txt exists
    if not os.path.exists("inputs/links.txt"):
        print("Error: inputs/links.txt not found!")
        return False
    
    # Read links
    with open("inputs/links.txt", "r") as f:
        links = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    
    if not links:
        print("Error: No valid URLs found in links.txt")
        return False
    
    # Download each config
    success = False
    for i, url in enumerate(links):
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(f"raw_configs/config_{i}.txt", "w") as f:
                f.write(response.text)
            print(f"Successfully saved config_{i}.txt")
            success = True
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
    
    return success

if __name__ == "__main__":
    download_configs()
