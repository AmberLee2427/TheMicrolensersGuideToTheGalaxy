import os
import re
import nb4llm

def create_solution_notebooks():
    """
    This script converts all notebooks in the 'Notebooks' directory to a text-based format,
    finds exercise blocks with explicit solution file markers, injects the solutions,
    and then converts them back to .ipynb files in a 'build' directory.
    This is used for automated testing of the notebooks.
    """
    if not os.path.exists('build'):
        os.makedirs('build')

    notebook_dir = 'Notebooks'
    exercise_dir = os.path.join(notebook_dir, 'Exercises')
    build_dir = 'build'

    # Regex to find the explicit exercise markers
    exercise_pattern = re.compile(r'######################\n# EXERCISE: (.*?)\n.*?######################', re.DOTALL)

    for notebook_file in os.listdir(notebook_dir):
        if notebook_file.endswith('.ipynb'):
            notebook_path = os.path.join(notebook_dir, notebook_file)
            txt_path = os.path.join(build_dir, f"{os.path.splitext(notebook_file)[0]}.txt")
            solution_ipynb_path = os.path.join(build_dir, notebook_file)

            # Convert notebook to text
            nb4llm.convert_ipynb_to_txt(notebook_path, txt_path)

            with open(txt_path, 'r') as f:
                content = f.read()

            # Find all exercise blocks
            matches = exercise_pattern.finditer(content)

            for match in matches:
                full_block = match.group(0)
                solution_filename = match.group(1).strip()
                solution_path = os.path.join(exercise_dir, solution_filename)

                solution_content = ""
                if os.path.exists(solution_path):
                    with open(solution_path, 'r') as sf:
                        solution_text = sf.read()
                        # Check for our explicit marker for prose answers
                        if solution_text.startswith("# TYPE: markdown"):
                            prose = solution_text.replace("# TYPE: markdown\n", "", 1)
                            solution_content = f"'''markdown\n{prose.strip()}\n'''"
                        else:
                            solution_content = solution_text.strip()
                else:
                    solution_content = f"# Solution file not found: {solution_filename}"

                # Replace the placeholder block with the solution
                content = content.replace(full_block, solution_content, 1)

            with open(txt_path, 'w') as f:
                f.write(content)

            # Convert text back to notebook
            nb4llm.convert_txt_to_ipynb(txt_path, solution_ipynb_path)
            os.remove(txt_path) # Clean up the intermediate text file

if __name__ == '__main__':
    create_solution_notebooks()
    print("Solution notebooks have been built in the 'build/' directory.") 