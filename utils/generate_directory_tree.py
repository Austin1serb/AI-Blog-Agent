import os

def load_gitignore(ignore_file=".gitignore"):
    """
    Reads the .gitignore file and returns a set of ignored patterns.
    """
    ignore_patterns = set()
    
    if os.path.exists(ignore_file):
        with open(ignore_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore comments and empty lines
                    ignore_patterns.add(line.rstrip("/"))  # Normalize directory paths
                    
    return ignore_patterns

def is_ignored(path, ignore_patterns):
    """
    Checks if a file or directory should be ignored based on .gitignore patterns.
    """
    for pattern in ignore_patterns:
        if path.endswith(pattern) or f"/{pattern}" in path:
            return True
    return False

def generate_directory_tree(start_path=".", prefix="", ignore_patterns=set()):
    """
    Recursively generates and prints a directory tree structure, respecting .gitignore.
    """
    try:
        entries = sorted(os.listdir(start_path))  # Get directory contents sorted
    except PermissionError:
        return  # Skip directories without permission

    files = [f for f in entries if os.path.isfile(os.path.join(start_path, f))]
    dirs = [d for d in entries if os.path.isdir(os.path.join(start_path, d))]

    # Apply .gitignore filtering
    files = [f for f in files if not is_ignored(f, ignore_patterns)]
    dirs = [d for d in dirs if not is_ignored(d, ignore_patterns)]

    for idx, directory in enumerate(dirs):
        is_last = idx == (len(dirs) - 1) and not files  # Last folder, no files after
        print(prefix + ("└── 📂 " if is_last else "│── 📂 ") + directory)
        new_prefix = prefix + ("    " if is_last else "│   ")
        generate_directory_tree(os.path.join(start_path, directory), new_prefix, ignore_patterns)

    for idx, file in enumerate(files):
        is_last = idx == (len(files) - 1)
        print(prefix + ("└── " if is_last else "│── ") + file)

if __name__ == "__main__":
    ignore_patterns = load_gitignore(".gitignore")
    print("📂 blog_agent/")
    generate_directory_tree(".", ignore_patterns=ignore_patterns)
