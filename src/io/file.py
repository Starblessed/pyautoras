from typing import Tuple, Any
from os.path import splitext, basename

class ConfigFile:
    
    def __init__(self, filepath: str, type_id: str | None=None) -> None:
        self.filepath = filepath
        self.project_name = splitext(basename(self.filepath))[0]
        self.type_id = type_id
        self._load()
        
    def _load(self):
        with open(self.filepath, 'r') as f:
            self._lines = f.readlines()
            
    def _save(self):
        with open(self.filepath, 'w') as f:
            f.writelines(self._lines)
        
    def _get_attribute(self, key: str) -> Tuple[str, int]:
        for i, line in enumerate(self._lines):
            if f"{key}=" in line:
                value = line.split('=')[1].strip()
                return value, i
        else:
            raise(KeyError(f"Key \"{key}\" not found in config file!"))
        
    def _set_attribute(self, key: str, value: Any, line: int | None=None):
        if line is None:
            line = self._get_attribute(key=key)[1]
        
        self._lines[line] = f"{key}={value}\n"
        
    def save_changes(self):
        self._save()
        
    def save_asnew(self, n: int) -> str:
        new_filepath = splitext(self.filepath)[0] + f'.{self.type_id}{n:02d}'
        with open(new_filepath, 'w') as f:
            f.writelines(self._lines)
            
        return new_filepath