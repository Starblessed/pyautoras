from src.ras.RASController import RasController
from src.io.output import FloodOutput
import datetime

def main():
    # TODO:Initialize RAS Controller
    ras_version = '7.0'
    project_path = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.prj'
    
    rc = RasController(version=ras_version)
    print(f'[{datetime.datetime.now()}] [OK] RAS Controller Initialized')

    
    # TODO: Load project
    proj = rc.open_project(project_path=project_path)
    
    print(f'[{datetime.datetime.now()}] [OK] Project Opened')
    
    # TODO: Select plan
    plan = rc.set_current_plan("botafogov3")
    
    rc.show_ras()
    
    print(f'[{datetime.datetime.now()}] [OK] Plan Selected')

    # TODO: Edit flow file
    
    
    # TODO: Run plan
    
    
    # TODO: Extract results


if __name__ == "__main__":
    main()
