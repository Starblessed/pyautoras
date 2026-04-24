from typing import Tuple, Any

class ConfigFile:
    
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
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