import json
import ipywidgets as widgets
from IPython.display import display, Markdown
import os

# Define the base directory for your project
GUIDE_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Checklist:
    def __init__(self):
        pass

    @staticmethod
    def get_notebook_outline(notebook_path: str):
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        outline = []
        
        for cell in notebook['cells']:
            if cell['cell_type'] == 'markdown':
                # Extract lines that start with #
                for line in cell['source']:
                    stripped_line = line.strip()
                    if stripped_line.startswith('#') and 'Contents' not in stripped_line and 'Next steps' not in stripped_line:
                        outline.append(('Markdown', stripped_line))
        
        return outline
    
    @staticmethod
    def get_notebook_exercises(notebook_path: str):
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        exercises = []
        
        for cell in notebook['cells']:
            if cell['cell_type'] == 'markdown':
                # Extract lines that start with <h2> and end with </h2>
                for line in cell['source']:
                    stripped_line = line.strip()
                    if stripped_line.startswith('<h2') and stripped_line.endswith('</h2>'):
                        exercises.append(('Markdown', stripped_line))
        
        return exercises
    
    @staticmethod
    def save_progress(notebook_name: str, progress_data: dict):
        progress_file = os.path.join(GUIDE_BASE_DIR, 'Progress', f'{notebook_name}_progress.json')
        os.makedirs(os.path.dirname(progress_file), exist_ok=True)
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_progress(notebook_name: str) -> dict:
        progress_file = os.path.join(GUIDE_BASE_DIR, 'Progress', f'{notebook_name}_progress.json')
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @staticmethod
    def create_checklist_from_notebook(notebook_name: str):
        # Full notebook path
        notebook_path = os.path.join(GUIDE_BASE_DIR, 'Notebooks', f'{notebook_name}.ipynb')

        # Extract the outline from the notebook
        outline = Checklist.get_notebook_outline(notebook_path)
        
        # Create the introduction text using the notebook name
        notebook_name = notebook_path.split('/')[-1].replace('.ipynb', '')
        intro_text = f"## {notebook_name} checklist"
        
        # Display introduction text
        display(Markdown(intro_text))
        
        # Create checklist items based on the outline
        checklist_items = [item[1] for item in outline]
        
        # Load saved progress
        progress_data = Checklist.load_progress(notebook_name)
        
        # Create checkboxes for each item
        checkboxes = [widgets.Checkbox(value=progress_data.get(item.lstrip('#').strip(), False), description=item.lstrip('#').strip()) for item in checklist_items]
        
        # Create a progress bar with a fixed width
        progress = widgets.FloatProgress(
            value=sum(checkbox.value for checkbox in checkboxes), min=0, max=len(checkboxes), description='Progress:', bar_style='info',
            layout=widgets.Layout(width='70%')
        )
        
        # Create a label to display the percentage
        percentage_label = widgets.Label(value=f"{(progress.value / len(checkboxes)) * 100:.0f}%")
        
        # Function to update the progress bar and percentage label
        def update_progress(change):
            checked_count = sum(checkbox.value for checkbox in checkboxes)
            progress.value = checked_count
            percentage = (checked_count / len(checkboxes)) * 100
            percentage_label.value = f"{percentage:.0f}%"
            
            # Save progress
            progress_data = {checkbox.description: checkbox.value for checkbox in checkboxes}
            Checklist.save_progress(notebook_name, progress_data)
        
        # Attach the update function to each checkbox
        for checkbox in checkboxes:
            checkbox.observe(update_progress, names='value')
        
        # Organize checkboxes with indentation based on the number of # characters
        indented_checkboxes = []
        for checkbox in checkboxes:
            description = checkbox.description
            num_hashes = outline[checkboxes.index(checkbox)][1].count('#')
            margin_size = num_hashes * 30
            indented_checkboxes.append(widgets.HBox([widgets.Box([checkbox], layout=widgets.Layout(margin=f'0 0 0 {margin_size}px'))]))
        
        # Display progress bar with percentage label and checkboxes
        progress_box = widgets.HBox([progress, percentage_label], layout=widgets.Layout(align_items='center'))
        display(progress_box)
        display(widgets.VBox(indented_checkboxes))

    @staticmethod
    def create_exercise_checklist_from_notebook(notebook: str) -> None:
        # Full notebook path
        notebook_path = os.path.join(GUIDE_BASE_DIR, 'Notebooks', f'{notebook}.ipynb')

        # Extract the exerises from the notebook
        exercises = Checklist.get_notebook_exercises(notebook_path)
        
        # Create the introduction text using the notebook name
        notebook_name = notebook_path.split('/')[-1].replace('.ipynb', '')
        save_name = notebook_name+'_exercises'  # for saving the json file
        intro_text = f"## {notebook_name} exercises checklist"
        
        # Display introduction text
        display(Markdown(intro_text))
        
        # Create checklist items based on the outline
        checklist_items = [item[1] for item in exercises]

        # strip the '<h2>' and '</h2>' tags from the description
        checklist_items = [item.replace('<h2>', '').replace('<h2 style="color: #808080; font-size: 24px;">', '').replace('</h2>', '').strip() for item in checklist_items]
        
        # Load saved progress
        progress_data = Checklist.load_progress(save_name)
        
        # Create checkboxes for each item
        checkboxes = [widgets.Checkbox(value=progress_data.get(item, False), 
                                       description=item
                                       ) for item in checklist_items]
        
        # Create a progress bar with a fixed width
        progress = widgets.FloatProgress(
            value=sum(checkbox.value for checkbox in checkboxes), min=0, max=len(checkboxes), description='Progress:', bar_style='info',
            layout=widgets.Layout(width='70%')
        )
        
        # Create a label to display the percentage
        if len(checkboxes) == 0:
            percentage_label = widgets.Label(value=f"100%")
        else:
            percentage_label = widgets.Label(value=f"{(progress.value / len(checkboxes)) * 100:.0f}%")
        
        # Function to update the progress bar and percentage label
        def update_progress(change):
            checked_count = sum(checkbox.value for checkbox in checkboxes)
            progress.value = checked_count
            if len(checkboxes) == 0:
                percentage_label.value = f"100%"
            else:
                percentage = (checked_count / len(checkboxes)) * 100
            percentage_label.value = f"{percentage:.0f}%"
            
            # Save progress
            progress_data = {checkbox.description: checkbox.value for checkbox in checkboxes}
            Checklist.save_progress(save_name, progress_data)
        
        # Attach the update function to each checkbox
        for checkbox in checkboxes:
            checkbox.observe(update_progress, names='value')
        
        # Organize checkboxes without indentation
        checkboxes_to_draw = []
        for checkbox in checkboxes:
            description = checkbox.description
            margin_size = 30
            checkboxes_to_draw.append(widgets.HBox([widgets.Box([checkbox], layout=widgets.Layout(margin=f'0 0 0 {margin_size}px'))]))
        
        # Display progress bar with percentage label and checkboxes
        progress_box = widgets.HBox([progress, percentage_label], layout=widgets.Layout(align_items='center'))
        display(progress_box)
        display(widgets.VBox(checkboxes))

    @staticmethod
    def list_notebooks() -> None:
        notebooks_dir = os.path.join(GUIDE_BASE_DIR, 'Notebooks')
        notebooks = [f.replace('.ipynb', '') for f in os.listdir(notebooks_dir) if f.endswith('.ipynb') and f != 'ProgressChecklist.ipynb']
        
        print("Available notebooks:")
        print("--------------------")
        for notebook in notebooks:
            # Load progress data
            progress_data = Checklist.load_progress(notebook)
            total_items = len(progress_data)
            checked_items = sum(progress_data.values())
            percentage = (checked_items / total_items) * 100 if total_items > 0 else 0
            print(f"{notebook:<45} ({percentage:>3.0f}% complete)")

# Example usage
if __name__ == '__main__':
    notebook_name = 'Introduction'  # Replace with your notebook file path
    Checklist.create_checklist_from_notebook(notebook_name)