import os
import requests
from pathlib import Path

def download_configs():
    # Create directories
    Path("inputs").mkdir(exist_ok=True)
    Path("raw_configs").mkdir(exist_ok=True)
    
    # Verify links file exists
    links_file = "inputs/links.txt"
    if not os.path.exists(links_file):
        print(f"Error: {links_file} not found! Creating template.")
        with open(links_file, "w") as f:
            f.write("# Add one config URL per line\n")
            f.write("https://raw.githubusercontent.com/lagzian/new-configs-collector/main/countries/hr/mixed\n")
        return False

    # Read and validate links
    with open(links_file, "r") as f:
        links = [l.strip() for l in f.readlines() 
                if l.strip() and not l.startswith("#")]
    
    if not links:
        print("Error: No valid URLs found in links.txt")
        return False

    # Download each config
    success = False
    for i, url in enumerate(links):
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # Verify content is not empty
            if not response.text.strip():
                print(f"Warning: Empty content from {url}")
                continue
                
            # Save config
            output_file = f"raw_configs/config_{i}.txt"
            with open(output_file, "w") as f:
                f.write(response.text)
            print(f"Saved {output_file} ({len(response.text)} bytes)")
            success = True
            
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
    
    return success

if __name__ == "__main__":
    download_configs()
