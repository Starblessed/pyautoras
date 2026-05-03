from src.io.file import ConfigFile
from src.ras.exceptions import NotAPlanException, NotAFlowException, NotAProjectException
from src.utils import dateutils

import os
from os.path import splitext
from datetime import datetime, timedelta



class ProjectConfig(ConfigFile):
    def __init__(self, filepath: str) -> None:
        if not os.path.splitext(filepath)[1].startswith(".prj"):
            raise NotAProjectException("Provided filepath does not resolve to a HEC-RAS project file!")
        super().__init__(filepath, type_id='prj')
        


class ProjectManager:
    def __init__(self, project_config: ProjectConfig | None=None):
        self.current_project = project_config
        
    def change_project(self, project_config: ProjectConfig):
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
