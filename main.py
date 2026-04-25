from src.ras.RASController import RasController
from src.io.output import FloodOutput
from src.ras.models.flow import UnsteadyFlowConfig
from src.ras.models.plan import PlanConfig
from src.ras.models.project import ProjectConfig, ProjectManager

import datetime
import random
from os.path import splitext

def main():
    
    # Initialize RAS Controller
    ras_version = '7.0'
    rc = RasController(version=ras_version)
    
    print(f'[{datetime.datetime.now()}] [OK] RAS Controller Initialized')


    # TODO: Edit flow file
    uf = UnsteadyFlowConfig(filepath=r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.u02')
    
    synthetic_pluvio = [random.random() * 3 for _ in range(192)]
    
    uf.set_precipitation(synthetic_pluvio)
    uf.set_interval(15, 'm')
    
    flow_path = uf.save_asnew(3)
    print(f'[{datetime.datetime.now()}] [OK] Flow file created')
    
    # TODO: Select and edit plan file
    pf = PlanConfig(r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.p03')
    
    now =  datetime.datetime.now()
    pf.set_simulation_date(now, now + datetime.timedelta(minutes=15*191))
    pf.set_flow_file(splitext(flow_path)[1][1:])
    
    plan_path = pf.save_asnew(4)
    print(plan_path)
    
    print(f'[{datetime.datetime.now()}] [OK] Plan file created')
    
    
    # TODO: edit project info
    project_path = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.prj'
    
    projf = ProjectConfig(project_path)
    pm = ProjectManager(projf)
    
    pm.add_unsteady_file(flow_path)
    print(f'[{datetime.datetime.now()}] [OK] Added unsteady file to project')

    pm.add_plan_file(plan_path)
    print(f'[{datetime.datetime.now()}] [OK] Added plan file to project')

    
    pm.set_current_plan(plan_path)
    print(f'[{datetime.datetime.now()}] [OK] Selected plan as current')

    
    # TODO: Load project
    proj = rc.open_project(project_path=project_path)
    
    print(f'[{datetime.datetime.now()}] [OK] Project opened')
    
    # TODO: Run plan
    rc.show_ras()
    result = rc.compute_current_plan(blocking=True)
    
    # TODO: Extract results
    print(result)


if __name__ == "__main__":
    main()
