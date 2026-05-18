from src.io.file import ConfigFile
from src.ras.exceptions import NotAPlanException, NotAFlowException, NotAProjectException
from src.utils import dateutils

import os
from os.path import splitext
from datetime import datetime, timedelta

import shutil
from pathlib import Path
import json



class ProjectConfig(ConfigFile):
    def __init__(self, filepath: str) -> None:
        if not os.path.splitext(filepath)[1].startswith(".prj"):
            raise NotAProjectException("Provided filepath does not resolve to a HEC-RAS project file!")
        super().__init__(filepath, type_id='prj')
        


class ProjectManager:
    def __init__(self, project_config: ProjectConfig | None=None):
        if project_config is not None: assert os.path.exists(project_config.filepath), f"Project filepath {project_config.filepath} does not exist!"
        self.current_project = project_config
        
    def change_project(self, project_config: ProjectConfig):
        assert os.path.exists(project_config.filepath), f"Project filepath {project_config.filepath} does not exist!"
        self.current_project = project_config

    def add_unsteady_file(self, filepath: str) -> None:
        assert self.current_project is not None, "Can't perform operation because there is no selected project"
        
        unsteady_lines = []
        for i, l in enumerate(self.current_project._lines):
            if "Unsteady File=" in l:
                unsteady_lines.append(i)
        
        start = min(unsteady_lines)
        end = max(unsteady_lines) + 1
        
        new_unsteady_id = splitext(filepath)[1][1:]
        
        new_unsteady_line = f"Unsteady File={new_unsteady_id}\n"
        if not new_unsteady_line in self.current_project._lines:
            self.current_project._lines[start:end] = self.current_project._lines[start:end] + [new_unsteady_line]
        
        self.current_project.save_changes()
        
    def add_plan_file(self, filepath: str) -> None:
        assert self.current_project is not None, "Can't perform operation because there is no selected project"
        
        plan_lines = []
        for i, l in enumerate(self.current_project._lines):
            if "Plan File=" in l:
                plan_lines.append(i)
        
        start = min(plan_lines)
        end = max(plan_lines) + 1
        
        new_plan_id = splitext(filepath)[1][1:]
        new_plan_line = f"Plan File={new_plan_id}\n"
        if not new_plan_line in self.current_project._lines:
            self.current_project._lines[start:end] = self.current_project._lines[start:end] + [new_plan_line]
        
        self.current_project.save_changes()
        
    def set_current_plan(self, filepath: str) -> None:
        assert self.current_project is not None, "Can't perform operation because there is no selected project"
        
        plan_id = splitext(filepath)[1][1:]
        
        self.current_project._set_attribute("Current Plan", plan_id)
        self.current_project.save_changes()

def create_project_from_folder(origin_path: str, dest_path: str="projects") -> str:
    dest_folder = os.path.join(dest_path, os.path.basename(origin_path))
    os.makedirs(dest_path, exist_ok=True)
    n = 0 
    while os.path.exists(dest_folder):
        n += 1
        if n == 1: print("Specified path already exists, creating new indexed project.")
        
        dest_folder = os.path.join(dest_path, os.path.basename(origin_path) + str(n))
    else:
        shutil.copytree(origin_path, dest_folder)
        
    # TODO Later: Remove Rio de Janeiro hardcoded values
    make_autoras_file(23, "S", os.path.basename(origin_path) + '.prj', 4674, dest_folder)
        
    return os.path.abspath(dest_folder)

def make_autoras_file(utm_zone: int, utm_zone_hemisphere: str, prj_filepath: str, dest_epsg: int, project_folder: str) -> None:
    assert utm_zone_hemisphere in ["S", "N"], f"Invalid hemisphere {utm_zone_hemisphere}"
    epsg_hemisphere = 326 if utm_zone_hemisphere == "N" else 327
    obj = {
        "prj_filepath": prj_filepath,
        "utm_zone": utm_zone,
        "utm_zone_hemisphere": utm_zone_hemisphere,
        "project_epsg": f"epsg:{epsg_hemisphere}{utm_zone:02d}",
        "dest_epsg": f"epsg:{dest_epsg}"
    }
    
    with open(os.path.join(project_folder, "autoras.json"), 'w', encoding="utf8") as jf:
        json_str = json.dumps(obj=obj, indent=4)
        
        jf.write(json_str)
        