import os
import sys
sys.path.append(os.path.abspath('../'))

def define(file_name):
    folder_path = "GuideEntries/"
    file_path = f"{folder_path}{file_name}.txt"
    figure_paths = []

    # List all files in the folder
    files = os.listdir(folder_path)

    # Find figure paths matching the filename
    for file in files:
        if file.startswith(file_name) and not file.endswith('.txt'):
            figure_paths.append(os.path.join(folder_path, file))

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            print(file.read())

        # Display the figures
        if figure_paths:  # if figure_path is not empty
            for figure_path in figure_paths:
                print(f"Figure found for {file_name}: {figure_path}")
                # Code to display the figure goes here
    else:
        print(f"Sorry, there are no Guide entries for {file_name}")


def list_entries(print_list=True):
    folder_path = "GuideEntries/"
    files = os.listdir(folder_path)
    entries = []
    for file in files:
        if file.endswith('.txt'):
            if print_list:
                print(file[:-4])  # Remove the .txt extension
            entries.append(file[:-4])
    if not print_list:
        return entries

def list_notebooks(print_list=True):
    folder_path = "Notebooks/"
    files = os.listdir(folder_path)
    notebooks = []
    for file in files:
        if file.endswith('.ipynb'):
            if print_list:
                print(file[:-6])
            notebooks.append(file[:-6])
    if not print_list:
        return notebooks

def open_notebook(file_name):
    folder_path = "Notebooks/"
    file_path = f"{folder_path}{file_name}.ipynb"
    if os.path.isfile(file_path):
        print(f"Opening {file_name}...")
        os.system(f"jupyter notebook {file_path}")
    else:
        print(f"Sorry, {file_name} notebook not found")

