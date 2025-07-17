import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup

def download_configs():
    # Create directories
    Path("inputs").mkdir(exist_ok=True)
    Path("raw_configs").mkdir(exist_ok=True)
    
    # Verify links file exists
    if not os.path.exists("inputs/links.txt"):
        print("Creating default links.txt")
        with open("inputs/links.txt", "w") as f:
            f.write("# Add one URL per line\n")
            f.write("https://raw.githubusercontent.com/lagzian/new-configs-collector/main/countries/hr/mixed\n")
        return False

    # Read links
    with open("inputs/links.txt", "r") as f:
        links = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    
    # Download each config
    for i, url in enumerate(links):
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # Clean HTML content if needed
            if 'text/html' in response.headers.get('Content-Type', ''):
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.get_text()
            else:
                content = response.text
            
            # Save cleaned content
            output_file = f"raw_configs/config_{i}.txt"
            with open(output_file, "w") as f:
                f.write(content)
            print(f"Saved {output_file}")
            
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
    
    return True

if __name__ == "__main__":
    download_configs()
