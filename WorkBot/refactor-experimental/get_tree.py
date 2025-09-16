# file: generate_tree.py
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')  

def tree(directory, prefix=""):
    files = sorted(os.listdir(directory))
    files = [f for f in files if f not in {"__pycache__", ".git", ".DS_Store"}]
    for i, name in enumerate(files):
        path = os.path.join(directory, name)
        connector = "├── " if i < len(files) - 1 else "└── "
        print(prefix + connector + name)
        if os.path.isdir(path):
            extension = "│   " if i < len(files) - 1 else "    "
            tree(path, prefix + extension)

tree(".")
