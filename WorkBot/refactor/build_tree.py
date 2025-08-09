#!/usr/bin/env python3
import os
from pathlib import Path

def build_tree(path: Path, max_depth: int, prefix: str = "", current_depth: int = 0) -> str:
    """Recursively build a file tree string up to max_depth levels."""
    tree_str = ""
    if current_depth >= max_depth:
        return tree_str

    entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        tree_str += f"{prefix}{connector}{entry.name}\n"

        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            tree_str += build_tree(entry, max_depth, prefix + extension, current_depth + 1)
    return tree_str

def main():
    start_dir = Path(".").resolve()
    max_depth = int(input("Enter max depth (n): ").strip())
    output_file = input("Enter output filename [tree_output.txt]: ").strip() or "tree_output.txt"

    tree = f"{start_dir.name}/\n" + build_tree(start_dir, max_depth)
    Path(output_file).write_text(tree, encoding="utf-8")

    print(f"Tree written to {output_file}")

if __name__ == "__main__":
    main()
