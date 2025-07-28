""" 
This script automates the process of creating solutions for the exercises in the 
notebook.
"""

import os
import sys
import re
import nb4llm

def get_solution_content(text_file : str) -> str:
    """
    Get the content of the solution for the notebook.
    """
    # make a txt version of the old notebook using nb4llm if old_notebook is a notebook

    code_pattern = r"######################.*?EXERCISE: (.*?)(?: PART: (\d+))?\n(.*?)######################"
    md_pattern = r"<!-- EXERCISE: (.*?)(?: PART: (\d+))? -->(.*?)<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->"

    code_matches = re.findall(code_pattern, text_file, re.DOTALL)
    md_matches = re.findall(md_pattern, text_file, re.DOTALL)

    return code_matches, md_matches

def format_code_content(content : str, filename : str, part_number : str) -> tuple[str, str]:
    """
    Format the code content for the solution files.

    Args:
        content: The content of the code exercise
        filename: The filename of the exercise
        part_number: The part number of the exercise
    
    Returns:
        file_content: The formatted content for the solution file
        comment_open: The regex key to check for existing solutions
    """
    fence_open = "```python\n"
    fence_close = "```\n"

    # determine the tab level of the code by counting the number of spaces at the beginning of the first line
    tab_level = content.split("\n")[0].count(" ")
    indent_string = " " * tab_level

    part_string = f" PART: {part_number}" if part_number else ""

    comment_open = f"{indent_string}######################\n{indent_string}# EXERCISE: {filename}{part_string}\n"
    comment_close = "######################\n"

    content_payload = f"{comment_open}{content}{comment_close}"

    file_content = f"{fence_open}{content_payload}{fence_close}"

    return file_content, comment_open

def format_md_content(content : str, filename : str, part_number : str) -> tuple[str, str]:
    """
    Format the markdown content for the solution files.

    Args:
        content: The content of the markdown exercise
        filename: The filename of the exercise
        part_number: The part number of the exercise

    Returns:
        file_content: The formatted content for the solution file
        comment_block_open: The regex key to check for existing solutions
    """
    fence_open = "```markdown\n"
    fence_close = "```\n"

    comment_open = "<!-- EXERCISE: "
    comment_close = " -->\n"
    comment_block_open = f"{comment_open}{filename} PART: {part_number} {comment_close}"
    comment_block_close = "<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->\n"

    content_payload = f"{comment_block_open}{content}{comment_block_close}"
    
    file_content = f"{fence_open}{content_payload}{fence_close}"

    return file_content, comment_block_open

def create_or_update_solutions(notebook : str, directory : str) -> None:
    """
    Create model solutions for the exercises in the notebook. These are the versions
    that should be in the notebook for exercise development and testing.

    Args:
        notebook: The notebook to create solutions for
        directory: The directory to save the solutions to
    """
    # make a txt version of the old notebook using nb4llm if old_notebook is a notebook
    code_matches, md_matches = get_solution_content(notebook)

    for match in code_matches:
        filename, part_number, content = match
        path = f"{directory}/{filename}"

        create_or_update_md_solution(filename, part_number, content, path, "code")

    for match in md_matches:
        filename, part_number, content = match
        path = f"{directory}/{filename}"

        create_or_update_md_solution(filename, part_number, content, path, "md")


def create_or_update_md_solution(filename, part_number, content, path, type : str = "code") -> None:
    """
    Replace a single markdown or code solution with a new one in the reference 
    files, or create/append a new one if it doesn't exist.
    """
    if type == "code":
        file_content, comment_open = format_code_content(content, filename, part_number)
    elif type == "md":
        file_content, comment_open = format_md_content(content, filename, part_number)
    else:
        raise ValueError(f"Invalid type: {type}")
    
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing_file_content = f.read()

        if existing_file_content == file_content:
            return
        else:
            # regex the existing content for the comment_open and get the 
            # content between it and the next comment_closed, using the 
            # get_solution_content function
            matches = re.findall(comment_open, existing_file_content, re.DOTALL)
            if len(matches) == 1:
                _, _, old_content = matches[0]
            elif len(matches) > 1:
                raise ValueError(f"Multiple copies of solution{part_number} found for {filename}")
            else:
                old_content = None  

            if old_content == None:
                #append the content to the existing file
                with open(path, 'a') as f:
                    f.write(file_content)
            else:
                # find and replace the content between the current_comment_open
                # and the next comment_closed
                old_file_content, _ = format_code_content(old_content, filename, part_number)
                new_content = re.sub(old_file_content, file_content, existing_file_content)
                with open(path, 'w') as f:
                    f.write(new_content)    

    else:  # file does not exist, create it
        with open(path, 'w') as f:
            f.write(file_content)



if __name__ == "__main__":
    # usage: python solutions.py <notebook> <directory>
    if len(sys.argv) == 1:
        print("Usage: python solutions.py <notebook> <directory>")
        sys.exit()

    notebook = sys.argv[1]
    directory = sys.argv[2]

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if not os.path.isdir(directory):
        raise ValueError(f"The provided directory {directory} is not a directory")
    
    if not os.path.exists(notebook):
        raise ValueError(f"The provided notebook {notebook} does not exist")
    
    if not os.path.isfile(notebook):
        raise ValueError(f"The provided notebook {notebook} is not a file")
        
    if notebook.endswith(".ipynb"):
        # make a txt version of the old notebook using nb4llm if old_notebook is a notebook
        txt_notebook = notebook.split('.')[:-1] + [".txt"]
        txt_notebook = "".join(txt_notebook)

        # ----- File Override Protection -----
        i = 0
        clean_up = True
        while os.path.exists(txt_notebook):
            print(f"The txt notebook {txt_notebook} already exists. ")
            # check in with the user to see if they want to replace the txt notebook
            replace = input(f"Replace the existing txt notebook, {txt_notebook}? (y/n): ")
            if "n" in replace.lower():
                # prompt the user for an alternative txt notebook name
                txt_notebook = input(
                    "Enter the alternative temporary txt notebook name: "
                )
                i += 1
                if i > 5:
                    raise ValueError(
                        "You have tried to replace the txt notebook too many times. "
                        "Please manually convert the notebook to a txt file and run the script again."
                    )
            elif "y" in replace.lower():
                clean_up = False
            else:
                raise ValueError(f"Invalid input: {replace}")

        nb4llm.convert_notebook_to_txt(notebook, txt_notebook)

    elif notebook.endswith(".txt"):
        txt_notebook = notebook
        clean_up = False

    create_or_update_solutions(txt_notebook, directory)

    if clean_up:
            os.remove(txt_notebook)  # remove the temporary txt notebook after processing

    else:
        raise ValueError(f"The provided notebook {notebook} is not a .ipynb or .md file")
