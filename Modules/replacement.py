import nb4llm
import re
import os
import sys

def replace_solutions(
        old_notebook : str, 
        new_notebook : str, 
        reference_dir : str = "Notebooks/Exercises/",
        destructive : bool = True
    ) -> None:
    """Replace the solutions in the old notebook with the solutions from the 
    reference files and save in a new notebook
    
    Args:
        old_notebook: The path to the old notebook
        new_notebook: The path to the new notebook
        reference_dir: The directory containing the reference files
        destructive: If true, the new notebook txt file will be deleted

    Raises:
        Exception: If no exercises are found
        Exception: If no solution is found for a code exercise
        Exception: If no solution is found for a markdown exercise
        Exception: If the old notebook does not exist
        Exception: If the old notebook is not a notebook or a txt file
        Exception: If the reference directory does not exist
        Exception: If the reference directory is not a directory

    Returns:
        None
    """
    if not os.path.exists(old_notebook):
        raise Exception(f"Input notebook {old_notebook} does not exist")
    
    if reference_dir[-1] != "/":
        reference_dir += "/"
    
    if not os.path.exists(reference_dir):
        raise Exception(f"Reference directory {reference_dir} does not exist")
    
    if not os.path.isdir(reference_dir):
        raise Exception(f"Reference directory {reference_dir} is not a directory")

    # make a txt version of the old notebook using nb4llm if old_notebook is a notebook
    if old_notebook.endswith(".ipynb"):
        nb4llm.convert_ipynb_to_txt(old_notebook, "old_notebook.txt")
    elif old_notebook.endswith(".txt"):
        with open(old_notebook, 'r') as f:
            notebook = f.read()
    else:
        raise Exception(f"Input notebook {old_notebook} is not a notebook or a txt file")

    with open("old_notebook.txt", 'r') as f:
        notebook = f.read()

    # print the first 100 characters of the old notebook
    print(old_notebook[:100])

    # Look for the indeicative solution marker
    # Pattern: (######################\n# EXERCISE: (.*?)(?: PART: (\d+))?\n)(.*?)(\n######################)
    #      or: ((<!-- EXERCISE: (.*?)(?: PART: (\d+))? -->)(.*?)(<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->)
    #           begin_marker, solution_file_name, (optional) part_number, content, end_marker

    # Define the patterns for the markers
    begin_code_marker = r"######################"
    end_code_marker = r"######################"
    # pattern = begin_marker, *, ECERCISE, *, end_marker
    code_pattern = begin_code_marker + r".*?EXERCISE: (.*?)(?: PART: (\d+))?\n(.*?)" + end_code_marker
    begin_markdown_marker = r"<!-- EXERCISE: "
    end_markdown_marker = r"<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->"
    # pattern = begin_marker, *, end_marker
    markdown_pattern = begin_markdown_marker + r"(.*?)(?: PART: (\d+))? -->(.*?)" + end_markdown_marker

    code_pattern = re.compile(code_pattern, re.DOTALL)
    md_pattern = re.compile(markdown_pattern, re.DOTALL)

    code_matches = code_pattern.findall(notebook)
    md_matches = md_pattern.findall(notebook)
    

    #------ Handle the code matches ------
    for match in code_matches:
        print(f"Code match: {match}")
        filename, part_number, content = match

        # read the solution file
        with open(f"{reference_dir}{filename}", 'r') as f:
            solution_file = f.read()

        # replace the content with the solution
        code_replacements = code_pattern.findall(solution_file)
        for replacement in code_replacements:
            _, part, solution = replacement
            if part_number == part:
                print(f"Solution: {solution}")
                # replace the content with the solution
                notebook = notebook.replace(content, solution)

        if len(code_replacements) == 0:
            raise Exception(f"No solution found for {filename} part {part_number}")

    #------ Handle the markdown matches ------
    for match in md_matches:
        print(f"Markdown match: {match}")
        filename, part_number, content = match

        # read the solution file
        with open(f"{reference_dir}{filename}", 'r') as f:
            solution_file = f.read()

        # replace the content with the solution
        md_replacements = md_pattern.findall(solution_file)
        for replacement in md_replacements:
            _, part, solution = replacement
            if part_number == part:
                print(f"Solution: {solution}")
                notebook = notebook.replace(content, solution)

        if len(md_replacements) == 0:
            raise Exception(f"No solution found for {filename} part {part_number}")

    if len(code_matches) == 0 and len(md_matches) == 0:
        raise Exception("No exercises found")

    if new_notebook.endswith(".ipynb"):
        # replace txt extention with ipynb
        new_notebook = new_notebook.replace(".ipynb", ".txt")

    # save the notebook (txt)
    with open(new_notebook, 'w') as f:
        f.write(notebook)
    
    # convert to ipynb properly
    nb4llm.convert_txt_to_ipynb(new_notebook, new_notebook.replace(".txt", ".ipynb"))

    # if destructive is true, delete the txt file
    if destructive:
        os.remove(new_notebook)
    os.remove("old_notebook.txt")


if __name__ == "__main__":
    if not len(sys.argv) >= 3:
        print("Usage: python replacement.py <input_notebook> <output_notebook>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    reference_dir = "Notebooks/Exercises/"
    destructive = True

    try:
        arg = sys.argv[3]
        if arg == "--keep":
            destructive = False
        else:
            reference_dir = arg
        arg = sys.argv[4]
        if arg == "--keep":
            destructive = False
        else:
            reference_dir = arg
    except:
        pass

    replace_solutions(input_file, output_file, reference_dir, destructive)