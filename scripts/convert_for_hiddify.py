import os
import json
from pathlib import Path

def process_files():
    """Process all raw config files"""
    # Create outputs directory if it doesn't exist
    Path("outputs").mkdir(exist_ok=True)
    
    # Check if raw_configs exists
    if not os.path.exists("raw_configs"):
        print("Error: raw_configs directory not found!")
        return
        
    if not os.listdir("raw_configs"):
        print("Warning: raw_configs directory is empty")
        return

    for filename in os.listdir("raw_configs"):
        if not filename.endswith(".txt"):
            continue
            
        filepath = os.path.join("raw_configs", filename)
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            # Your processing logic here
            # ...
            
            output_path = os.path.join("outputs", f"hiddify_{filename.replace('.txt', '.json')}")
            with open(output_path, "w") as f:
                json.dump(processed_content, f, indent=2)
                
            print(f"Generated: {output_path}")
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    process_files()
