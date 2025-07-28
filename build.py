import os
import subprocess
import shutil

def build_pipeline():
    """
    Orchestrates the full build process:
    1. Creates a clean 'build' directory.
    2. Runs the replacement script to generate solution notebooks.
    3. Copies the source notebooks into the docs directory for Sphinx.
    4. Runs sphinx-build to generate the HTML documentation.
    """
    build_dir = 'build'
    docs_dir = 'docs'
    source_notebooks_dir = 'Notebooks'
    dest_notebooks_dir = os.path.join(docs_dir, 'Notebooks')
    html_output_dir = os.path.join(docs_dir, '_build', 'html')

    # 1. Create a clean 'build' directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    print(f"Clean '{build_dir}' directory created.")

    # 2. Run the replacement script
    print("Running replacement script...")
    try:
        subprocess.run(
            ['python', 'replacement.py', 'Notebooks/BinarySource.ipynb', os.path.join(build_dir, 'BinarySource.ipynb')],
            check=True, text=True, capture_output=True
        )
        print("Replacement script completed successfully.")
    except subprocess.CalledProcessError as e:
        print("--- ERROR: replacement.py failed ---")
        print(e.stderr)
        return

    # 3. Copy source notebooks to docs directory
    if os.path.exists(dest_notebooks_dir):
        shutil.rmtree(dest_notebooks_dir)
    shutil.copytree(source_notebooks_dir, dest_notebooks_dir)
    print(f"Copied '{source_notebooks_dir}' to '{dest_notebooks_dir}'.")


    # 4. Run sphinx-build
    print("Running sphinx-build...")
    try:
        subprocess.run(
            ['sphinx-build', '-b', 'html', docs_dir, html_output_dir],
            check=True, text=True, capture_output=True
        )
        print(f"Sphinx build successful. HTML pages are in '{html_output_dir}'.")
    except subprocess.CalledProcessError as e:
        print("--- ERROR: sphinx-build failed ---")
        print(e.stderr)
        return

if __name__ == '__main__':
    build_pipeline() 