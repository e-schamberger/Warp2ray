import os
import requests
from pathlib import Path

def download_configs():
    Path("inputs").mkdir(exist_ok=True)
    Path("raw_configs").mkdir(exist_ok=True)
    
    if not os.path.exists("inputs/links.txt"):
        print("Creating default links.txt")
        with open("inputs/links.txt", "w") as f:
            f.write("https://raw.githubusercontent.com/lagzian/new-configs-collector/main/countries/hr/mixed\n")
            f.write("https://raw.githubusercontent.com/SagerNet/sing-box-examples/main/Configurations/VMess.json\n")
        return False

    with open("inputs/links.txt", "r") as f:
        links = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    
    for i, url in enumerate(links):
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(f"raw_configs/config_{i}.txt", "w") as f:
                f.write(response.text)
            print(f"Saved config_{i}.txt")
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")

if __name__ == "__main__":
    download_configs()
