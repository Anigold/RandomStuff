import os

OUTPUT_FILE = "file_tree.txt"
IGNORED_DIRS = {"__pycache__"}

def write_file_tree(root_dir, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for current_path, dirnames, filenames in os.walk(root_dir):
            # Remove ignored directories in-place so os.walk doesn't visit them
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

            # Determine tree depth based on relative path
            rel_path = os.path.relpath(current_path, root_dir)
            depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1

            # Write directory name
            indent = "    " * depth
            dirname = os.path.basename(current_path) if depth > 0 else root_dir
            f.write(f"{indent}{dirname}/\n")

            # Write filenames
            for filename in filenames:
                f.write(f"{indent}    {filename}\n")

if __name__ == "__main__":
    cwd = os.getcwd()
    print(f"Generating file tree for: {cwd}")
    write_file_tree(cwd, OUTPUT_FILE)
    print(f"Saved tree to {OUTPUT_FILE}")
