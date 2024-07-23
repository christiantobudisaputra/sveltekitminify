import os
import argparse
from pathlib import Path
import fnmatch
import json
import hashlib

def read_ignore_file(ignore_file_path):
    if os.path.exists(ignore_file_path):
        with open(ignore_file_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    return []

def should_ignore(path, ignore_patterns):
    path_parts = path.split(os.sep)
    for pattern in ignore_patterns:
        if pattern.endswith('/'):
            # Directory pattern
            if any(fnmatch.fnmatch(part, pattern.rstrip('/')) for part in path_parts):
                return True
        else:
            # File pattern
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
    return False

def minify_svelte_code(code):
    # This is a basic minification. For production use, consider a more robust solution.
    lines = code.split('\n')
    minified = [line.strip() for line in lines if line.strip() and not line.strip().startswith('//')]
    return ' '.join(minified)

def process_file(file_path, ignore_patterns):
    if should_ignore(file_path, ignore_patterns):
        return None

    with open(file_path, 'r') as f:
        content = f.read()

    if file_path.endswith('.svelte'):
        return minify_svelte_code(content)
    elif file_path.endswith('.js') or file_path.endswith('.ts'):
        return content  # For JS/TS files, we're not minifying, just including
    else:
        return None

def find_static_assets(project_path, ignore_patterns):
    static_dir = os.path.join(project_path, 'static')
    assets = []
    if os.path.exists(static_dir):
        for root, _, files in os.walk(static_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path, ignore_patterns):
                    assets.append(file_path)
    return assets

def generate_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_chunk(content, chunk_size, file_path, output_dir):
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(output_dir, f"{os.path.basename(file_path)}_chunk_{i+1}.md")
        with open(chunk_file, 'w') as f:
            f.write(chunk)
        chunk_files.append(chunk_file)
    return chunk_files

def main(project_path, output_dir, chunk_size=8000):
    ignore_file = os.path.join(project_path, '.sveltekitminifyignore')
    ignore_patterns = read_ignore_file(ignore_file)
    print(f"Ignore patterns: {ignore_patterns}")  # Debug print

    os.makedirs(output_dir, exist_ok=True)

    index_content = "# SvelteKit Project Minified Code Index\n\n"
    file_hashes = {}

    for root, dirs, files in os.walk(project_path):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]

        for file in files:
            file_path = os.path.join(root, file)
            if should_ignore(file_path, ignore_patterns):
                print(f"Ignoring file: {file_path}")  # Debug print
                continue

            if file.endswith('.svelte') or file.endswith('.js') or file.endswith('.ts'):
                processed_content = process_file(file_path, ignore_patterns)
                if processed_content:
                    relative_path = os.path.relpath(file_path, project_path)
                    file_hash = generate_file_hash(file_path)
                    file_hashes[relative_path] = file_hash

                    content = f"## {relative_path}\n\n```{'svelte' if file.endswith('.svelte') else 'javascript'}\n{processed_content}\n```\n\n"
                    chunk_files = create_chunk(content, chunk_size, relative_path, output_dir)

                    index_content += f"- {relative_path}\n"
                    for i, chunk_file in enumerate(chunk_files):
                        index_content += f"  - [Chunk {i+1}]({os.path.relpath(chunk_file, output_dir)})\n"

    assets = find_static_assets(project_path, ignore_patterns)
    if assets:
        asset_content = "## Static Assets\n\n"
        for asset in assets:
            relative_path = os.path.relpath(asset, project_path)
            asset_content += f"- {relative_path}\n"

        asset_chunks = create_chunk(asset_content, chunk_size, "static_assets", output_dir)
        index_content += "\n## Static Assets\n"
        for i, chunk_file in enumerate(asset_chunks):
            index_content += f"- [Asset List Chunk {i+1}]({os.path.relpath(chunk_file, output_dir)})\n"

    project_structure = {
        "name": os.path.basename(project_path),
        "structure": {}
    }

    def build_structure(path, structure):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if should_ignore(item_path, ignore_patterns):
                continue
            if os.path.isdir(item_path):
                structure[item] = {}
                build_structure(item_path, structure[item])
            elif os.path.isfile(item_path):
                structure[item] = file_hashes.get(os.path.relpath(item_path, project_path), None)

    build_structure(project_path, project_structure["structure"])

    structure_content = "\n## Project Structure\n\n```json\n"
    structure_content += json.dumps(project_structure, indent=2)
    structure_content += "\n```\n"

    structure_chunks = create_chunk(structure_content, chunk_size, "project_structure", output_dir)
    index_content += "\n## Project Structure\n"
    for i, chunk_file in enumerate(structure_chunks):
        index_content += f"- [Structure Chunk {i+1}]({os.path.relpath(chunk_file, output_dir)})\n"

    with open(os.path.join(output_dir, "index.md"), 'w') as f:
        f.write(index_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minify SvelteKit project into multiple markdown files.")
    parser.add_argument("project_path", help="Path to the SvelteKit project")
    parser.add_argument("output_dir", help="Path to the output directory for markdown files")
    parser.add_argument("--chunk-size", type=int, default=8000, help="Maximum size of each chunk in characters")
    args = parser.parse_args()

    main(args.project_path, args.output_dir, args.chunk_size)
