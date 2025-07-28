"""
This script automates the process of creating solution files from a master
notebook that contains all the completed exercises.
"""

import os
import sys
import re
import nb4llm
from collections import defaultdict

# This pattern now includes the #---------------------- line for more specific matching.
CODE_PATTERN = re.compile(
    r"######################\n"
    r"# EXERCISE: (.*?)(?: PART: (\d+))?\n"
    r"#----------------------\n"
    r"(.*?)\n"
    r"######################",
    re.DOTALL
)

MD_PATTERN = re.compile(
    r"<!-- EXERCISE: (.*?)(?: PART: (\d+))? -->\n"
    r"(.*?)\n"
    r"<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->",
    re.DOTALL
)

def extract_solutions(notebook_text_content: str) -> dict:
    """
    Parses a notebook's text content and extracts all exercise solutions,
    grouping them by their target filename.
    """
    solutions = defaultdict(list)

    # Find all code exercise blocks
    for match in CODE_PATTERN.finditer(notebook_text_content):
        filename, part_number, content = match.groups()
        solutions[filename].append({
            "type": "code",
            "part": part_number,
            "content": content.strip()
        })

    # Find all markdown exercise blocks
    for match in MD_PATTERN.finditer(notebook_text_content):
        filename, part_number, content = match.groups()
        solutions[filename].append({
            "type": "markdown",
            "part": part_number,
            "content": content.strip()
        })

    return solutions

def build_solution_file_content(filename: str, parts: list) -> str:
    """
    Builds the complete content for a single solution file from its constituent parts.
    """
    # Sort parts by part number, treating None (single-part) as 0 for sorting.
    parts.sort(key=lambda x: int(x['part'] or '0'))
    is_multipart = len(parts) > 1 and any(p['part'] for p in parts)

    output = []
    for part in parts:
        part_content_lines = []
        # Add PART marker for multipart exercises
        if is_multipart and part['part']:
            part_content_lines.append(f"PART: {part['part']}")

        part_string = f" PART: {part['part']}" if part.get('part') else ""

        # Add the fenced block
        if part['type'] == 'code':
            fence_content = (
                "```python\n"
                "######################\n"
                f"# EXERCISE: {filename}{part_string}\n"
                "#----------------------\n"
                f"{part['content']}\n"
                "######################\n"
                "```"
            )
            part_content_lines.append(fence_content)
        else:  # markdown
            fence_content = (
                "```markdown\n"
                f"<!-- EXERCISE: {filename}{part_string} -->\n"
                f"{part['content']}\n"
                "<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->\n"
                "```"
            )
            part_content_lines.append(fence_content)
        output.append("\n".join(part_content_lines))

    return "\n\n".join(output)

def create_solution_files_from_notebook(notebook_text_path: str, output_dir: str):
    """
    Reads a notebook text file, extracts all solutions, and writes them to
    individual, complete solution files, overwriting any existing ones.
    """
    print(f"Reading master notebook from: {notebook_text_path}")
    with open(notebook_text_path, 'r', encoding='utf-8') as f:
        content = f.read()

    solutions = extract_solutions(content)
    print(f"Found {len(solutions)} solution files to generate.")

    if not solutions:
        print("Warning: No exercise blocks found in the notebook.")
        return

    for filename, parts in solutions.items():
        solution_content = build_solution_file_content(filename, parts)
        solution_path = os.path.join(output_dir, filename)
        with open(solution_path, 'w', encoding='utf-8') as f:
            print(f"  -> Writing solution to {solution_path}")
            f.write(solution_content)

    print("\nSolution file generation complete.")


if __name__ == "__main__":
    # usage: python solutions.py <notebook> <directory>
    if len(sys.argv) != 3:
        print("Usage: python solutions.py <path_to_notebook.ipynb> <output_directory>")
        sys.exit(1)

    notebook_path = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    if not os.path.isdir(output_directory):
        print(f"Error: The provided path '{output_directory}' is not a directory.")
        sys.exit(1)
    
    if not os.path.exists(notebook_path):
        print(f"Error: The provided notebook '{notebook_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isfile(notebook_path):
        print(f"Error: The provided notebook path '{notebook_path}' is not a file.")
        sys.exit(1)
        
    txt_notebook = ""
    clean_up = False
    if notebook_path.endswith(".ipynb"):
        # Use os.path.splitext to reliably get the name without the extension
        base_name = os.path.splitext(notebook_path)[0]
        txt_notebook = f"{base_name}_temp_solution_gen.txt"
        
        # Simple override without interactive prompts for automation
        print(f"Converting {notebook_path} to {txt_notebook}...")
        nb4llm.convert_ipynb_to_txt(notebook_path, txt_notebook)
        clean_up = True

    elif notebook_path.endswith(".txt"):
        txt_notebook = notebook_path
    else:
        print(f"Error: The provided file '{notebook_path}' is not a .ipynb or .txt file.")
        sys.exit(1)

    try:
        create_solution_files_from_notebook(txt_notebook, output_directory)
    finally:
        if clean_up and os.path.exists(txt_notebook):
            print(f"Cleaning up temporary file: {txt_notebook}")
            os.remove(txt_notebook)
