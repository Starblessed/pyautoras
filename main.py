from src.ras.RASController import RasController
from src.io.output import FloodOutput
from src.ras.models.flow import UnsteadyFlowConfig
from src.ras.models.plan import PlanConfig

import datetime
import random

def main():
    # TODO:Initialize RAS Controller
    ras_version = '7.0'
    project_path = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.prj'
    
    rc = RasController(version=ras_version)
    print(f'[{datetime.datetime.now()}] [OK] RAS Controller Initialized')

    
    # TODO: Load project
    proj = rc.open_project(project_path=project_path)
    
    print(f'[{datetime.datetime.now()}] [OK] Project Opened')
    
    # TODO: Edit flow file
    uf = UnsteadyFlowConfig(filepath=r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.u02')
    
    synthetic_pluvio = [random.random() * 3 for _ in range(192)]
    
    uf.set_precipitation(synthetic_pluvio)
    uf.set_interval(30, 'm')
    
    uf.save_asnew(3)
    
    # TODO: Select plan
    pf = PlanConfig(r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.p03')
    
    now =  datetime.datetime.now()
    pf.set_simulation_date(now - datetime.timedelta(days=4), now -  datetime.timedelta(days=2))
    
    pf.save_asnew(4)
    
    plan = rc.set_current_plan("p3")
    
    
    print(f'[{datetime.datetime.now()}] [OK] Plan Selected')


    
    # TODO: Run plan
    
    rc.show_ras()
    
    # TODO: Extract results


if __name__ == "__main__":
    main()
