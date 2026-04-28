from win32com import client
import pythoncom
from src.ras.exceptions import InvalidVersionException

from typing import Any

class RasController:
    
    def __init__(self, version: str='7.0') -> None:
        self._version = version
        self._controller = self._get_w32_ras_controller(version=version)
        
        
    def _get_ras_dispatch_string(self, version: str) -> str:
        """Gets the RAS Dispatch string from the specified RAS version.

        Args:
            version (float): RAS version to use.

        Returns:
            str: RAS Dispatch string.
        """
        
        return f"RAS{version.replace(".", "")}.HECRASController"
    
    def _get_w32_ras_controller(self, version: str) -> client.CDispatch:
        """Gets the win32com RAS Controller Object.

        Args:
            version (float): RAS version to use.

        Returns:
            win32com.client.CDispatch: win32com RAS Controller Object.
        """
        
        try:
            return client.Dispatch(self._get_ras_dispatch_string(version)) # type: ignore
            
        except pythoncom.com_error:
            raise(InvalidVersionException(f"Invalid RAS version {version}"))
        
    def __repr__(self):
        return f"RAS Controller for HEC-RAS v{self._version}\nMethods: {dir(self)}"
    
    def show_ras(self):
        self._controller.ShowRas()
    
    def open_project(self, project_path: str) -> Any:
        try:
            return self._controller.Project_Open(project_path)
        except Exception as e:
            print(e)
            raise(e)
        
    def close_project(self):
        try:
            self._controller.Project_Close()
        except Exception as e:
            print(e)
            raise(e)
    
    def create_session_id(self, task_id: str) -> str:
        return f"session:{task_id}"

    def compute_current_plan(self, blocking=True):
        result = self._controller.Compute_CurrentPlan(None, None, blocking)

        if isinstance(result, tuple):
            success = bool(result[0])
            n_messages = result[1] if len(result) > 1 else None
            messages = result[2] if len(result) > 2 else ""
        else:
            success = bool(result)
            n_messages = None
            messages = ""

        if not success:
            raise RuntimeError(messages or "HEC-RAS Compute_CurrentPlan failed")

        return {
            "success": success,
            "n_messages": n_messages,
            "messages": messages,
        }
        
    def close(self) -> None:
        try:
            self._controller.QuitRas()
        except Exception as e:
            print(e)
            raise(e)
        
    def terminate(self) -> int:
        code = 0
        try:
            self.close_project()
        except Exception as e:
            print(e)
            code = -1
        finally:
            self.close()
        return code

if __name__ == "__main__":
    
    # Creates an instance of the RasController class
    rc = RasController(version="7.0")
    
    # Shows the object's string representation
    print(rc)
    
    # Opens a project
    proj_path = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.prj'
    proj = rc.open_project(proj_path)
    
    # Shows the project's string representation
    print(proj)
    print(type(proj))
    
    rc.show_ras()
    
    rc.close_project()
    rc.close()
    
    
    