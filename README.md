# SvelteKit Project Minifier

This Python script minifies and chunks a SvelteKit project into multiple markdown files. It's designed to help developers work with large SvelteKit projects in AI-assisted development environments by breaking down the project into manageable pieces.

## Features

- Minifies Svelte, JavaScript, and TypeScript files
- Chunks large files into smaller markdown files
- Creates an index file for easy navigation
- Includes static asset information
- Generates a project structure overview
- Supports custom ignore patterns

## Requirements

- Python 3.6 or higher

## Usage

1. Place the `sveltekit_project_minifier.py` script in a convenient location.
2. Open a terminal and navigate to the directory containing the script.
3. Run the script with the following command:

```
python sveltekit_project_minifier.py /path/to/sveltekit/project /path/to/output/directory --chunk-size 8000
```

Replace `/path/to/sveltekit/project` with the path to your SvelteKit project, and `/path/to/output/directory` with the desired output location for the markdown files.

The `--chunk-size` parameter is optional and defaults to 8000 characters. Adjust this value based on the context window size of your AI model.

## Output

The script will generate:

1. An `index.md` file in the output directory, serving as a table of contents for all chunked files.
2. Multiple markdown files containing chunked content from your SvelteKit project.
3. A project structure overview in JSON format.

## Customizing Ignore Patterns

Create a `.sveltekitminifyignore` file in your SvelteKit project root to specify files or directories to ignore. The syntax is similar to `.gitignore`.

## Note

This script provides basic minification. For production use, consider implementing a more robust minification solution.

## Contributing

Feel free to submit issues or pull requests to improve this script.
