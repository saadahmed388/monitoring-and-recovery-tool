import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime 

class RecoveryHistoryManager(QObject):
    history_updated = pyqtSignal()
    def __init__(self, filepath="data_and_config_files/recovery_history.json"):
        super().__init__()
        folder = os.path.dirname(filepath)
        os.makedirs(folder, exist_ok=True)
        self.filepath = filepath
        self.history = self.load_history()
        

    def load_history(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                return {}
        return {}

    def save_history(self): 
        with open(self.filepath, "w") as f:
            json.dump(self.history, f, indent=4, default=str)
        self.history_updated.emit()

    def add_history(self, q_name, env, pre_rec_data = None, post_rec_data = None):

        date = datetime.now().strftime('%d-%m-%Y')

        record = (
            self.history
            .setdefault(date, {})
            .setdefault(env, {})
            .setdefault(q_name, {})
        )

        if pre_rec_data:
            record["pre_rec_data"] = pre_rec_data
    
        if post_rec_data:
            record["post_rec_data"] = post_rec_data

    
    def delete_history(self, name, env):
        self.history = [q for q in self.queries if q["name"] != name]
        

    def get_all_history(self):        
        return self.history

