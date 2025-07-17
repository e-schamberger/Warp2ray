def download_configs():
    # Read links from inputs/links.txt
    if not os.path.exists("inputs/links.txt"):
        print("Error: inputs/links.txt not found! Creating empty file.")
        Path("inputs").mkdir(exist_ok=True)
        with open("inputs/links.txt", "w") as f:
            f.write("# Add your config URLs here\n")
        return
    
    # Rest of the function remains the same
