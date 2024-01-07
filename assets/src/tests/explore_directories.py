import os

def explore_directory(base_path):
    for root, dirs, files in os.walk(base_path):
        print(f"Current Directory: {root}")

        for dir_name in dirs:
            print(f"Directory: {os.path.join(root, dir_name)}")

        for file_name in files:
            print(f"File: {os.path.join(root, file_name)}")

# Example usage
base_path = "assets/old/sprites"
explore_directory(base_path)
