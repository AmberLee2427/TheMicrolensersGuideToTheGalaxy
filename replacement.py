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

    # Look for the indeicative solution marker
    # Pattern: (######################\n# EXERCISE: (.*?)(?: PART: (\d+))?\n)(.*?)(\n######################)
    #      or: ((<!-- EXERCISE: (.*?)(?: PART: (\d+))? -->)(.*?)(<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->)
    #           begin_marker, solution_file_name, (optional) part_number, content, end_marker

    code_pattern = (
        r".*?(######################.*?"        # ".*?" in case of tabs and rogue
        r"EXERCISE: (.*?)(?: PART: ([^\n]+))?\n"  # spaces
        r".*?"                                  # <-- the actual solution content
        r"######################)"              # everything wrap in "(", ")" to 
    )                                           # catch the entire block

    markdown_pattern = (
        r"(<!-- EXERCISE: (.*?)(?: PART: ([^\n]+))? -->"  # shouldn't be indented
        r".*?"                                  # <-- the actual solution content
        r"<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->)"    # shouldn't be indented
    )

    # The "EXERCISE: * PART: *" must be unique for the replacement to work
    # If there are multiple matches, an exception will be raised
    # If there are no matches, an exception will be raised

    code_pattern = re.compile(code_pattern, re.DOTALL)    # re.DOTALL allows . to 
    md_pattern = re.compile(markdown_pattern, re.DOTALL)  # match newlines

    code_matches = code_pattern.findall(notebook)  # findall returns a list of tuples
    md_matches = md_pattern.findall(notebook)  # each tuple contains the match groups

    #------ Handle the code matches ------
    for match in code_matches:
        notebook = replace_with_corresponding_solution(match, notebook, code_pattern, reference_dir, "code")

    #------ Handle the markdown matches ------
    for match in md_matches:
        notebook = replace_with_corresponding_solution(match, notebook, md_pattern, reference_dir, "markdown")

    if len(code_matches) == 0 and len(md_matches) == 0:
        raise Exception("No exercises found")

    if new_notebook.endswith(".ipynb"):
        # replace txt extention with ipynb
        new_notebook = new_notebook.replace(".ipynb", ".txt") # = <new notebook>.txt

    # save the notebook (txt)
    with open(new_notebook, 'w') as f:
        f.write(notebook)
    
    # convert to ipynb properly
    nb4llm.convert_txt_to_ipynb(new_notebook, new_notebook.replace(".txt", ".ipynb"))
    # output saved as <new notebook>.ipynb

    # if destructive is true, delete the txt file
    if destructive:
        os.remove(new_notebook) # new_notebook = <new notebook>.txt
    os.remove("old_notebook.txt")

def replace_with_corresponding_solution(
        match : tuple, 
        notebook : str, 
        pattern : re.Pattern, 
        reference_dir : str, 
        block_type : str = "code"
    ) -> str:
        """Replace the content of the block with the corresponding solution block

        Args:
            match: The match object from the code_pattern or md_pattern
            notebook: The notebook to replace the content in
            code_pattern: The pattern to find the solution block in
            reference_dir: The directory containing the reference files
            block_type: The type of block to replace, either "code" or "markdown"

        Returns:
            The notebook with the content replaced

        Raises:
            Exception: If multiple solutions are found for the block
            Exception: If no solution is found for the block
            Exception: If the block type is not valid
            Exception: If the solution file does not exist
        """
        print(f"{block_type} match: {match}")
        block, filename, part_number = match

        if not os.path.exists(f"{reference_dir}{filename}"):
            raise Exception(f"Solution file {filename} does not exist")

        # read the solution file
        with open(f"{reference_dir}{filename}", 'r') as f:
            solution_file = f.read()

        # replace the whole block with the corresponding solution block
        found_patterns = pattern.findall(solution_file)

        replacements = []
        for replacement in found_patterns:
            solution_block, file, part = replacement
            print(f"solution_block: {solution_block}, file: {file}, part: {part}")
            if file == filename and part == part_number:
                replacements.append(replacement)

        if len(replacements) == 0:
            raise Exception(f"No solution found for {filename} part {part_number}")

        if len(replacements) > 1:
            raise Exception(f"Multiple solutions found for {filename}, part {part_number}")

        replacement = replacements[0]
        solution_block, _, part = replacement
        if part_number == part:
            print(f"Solution: {solution_block}")
            # replace the content with the solution
            notebook = notebook.replace(block, solution_block)

        if len(replacements) == 0:
            raise Exception(f"No solution found for {filename} part {part_number}")
        
        return notebook

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
