import json
import os

class ProjectManager:
    def __init__(self, projects_dir="saved_projects"):
        self.projects_dir = projects_dir
        self.current_filename = None  # Track the active file state here
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

    def save_file(self, filename, canvas):
        """Purely handles the serialization and disk write."""
        if not filename.endswith(".json"): filename += ".json"
        
        # We call a method on canvas to get the raw dict
        data = canvas.get_serialization_data()

        path = os.path.join(self.projects_dir, filename)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
        
        self.current_filename = filename.replace(".json", "")
        return filename

    def load_file(self, filename, canvas, editor):
        """Reads disk and tells canvas to rebuild itself."""
        path = os.path.join(self.projects_dir, filename)
        if not os.path.exists(path): return False

        with open(path, 'r') as f:
            data = json.load(f)

        # Canvas is responsible for knowing how to draw itself from data
        canvas.load_from_data(data, editor)
        self.current_filename = filename.replace(".json", "")
        return True
    
    def delete_file(self, filename):
        """Removes the file from disk and returns success."""
        path = os.path.join(self.projects_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def reset_session(self):
        """Resets the internal tracking of the current file."""
        self.current_filename = None