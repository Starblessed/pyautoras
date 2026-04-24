from src.io.file import ConfigFile
from src.ras.exceptions import NotAPlanException, NotAFlowException, NotAProjectException
from src.utils import dateutils

import os
from datetime import datetime, timedelta

class ProjectConfig(ConfigFile):
    def __init__(self, filepath: str) -> None:
        if not os.path.splitext(filepath)[1].startswith(".prj"):
            raise NotAProjectException("Provided filepath does not resolve to a HEC-RAS plan file!")
        super().__init__(filepath, type_id='prj')
        
    # TODO: flow/plan manager methods
        