from src.ras.RASController import RasController
from src.io.output import FloodOutput
from src.ras.models.flow import UnsteadyFlowConfig
from src.ras.models.plan import PlanConfig
from src.ras.models.project import ProjectConfig, ProjectManager, create_project_from_folder

import datetime
import random
from os.path import splitext, join

def main():
    
    # ---------- Simulation Config
    N_STEPS = 16
    TIME_INTERVAL = 15
    TIME_INTEVAL_UNIT = 'm'
    
    BASE_FLOW_ID = 2
    BASE_PLAN_ID = 3
    
    
    NEW_FLOW_ID = 3
    NEW_PLAN_ID = 4
    
    SYNTHETIC_PLUVIO_SCALING_FACTOR = 3
    
    PROJECT_FOLDER = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo'
    
    
    # ---------- Create Project
    
    PROJECT_FOLDER = create_project_from_folder(PROJECT_FOLDER)
    
    # ---------- Initialize RAS Controller
    ras_version = '7.0'
    rc = RasController(version=ras_version)
        
    print(f'[{datetime.datetime.now()}] [OK] RAS Controller Initialized')
    
    try:
    
        # ---------- Edit flow file
        uf = UnsteadyFlowConfig(filepath=join(PROJECT_FOLDER, rf'Botafogo.u{BASE_FLOW_ID:02d}'))
        
        synthetic_pluvio = [random.random() * SYNTHETIC_PLUVIO_SCALING_FACTOR for _ in range(N_STEPS)]
        uf.set_precipitation(synthetic_pluvio)
        uf.set_interval(TIME_INTERVAL, TIME_INTEVAL_UNIT)
        
        flow_path = uf.save_asnew(NEW_FLOW_ID)
        
        print(f'[{datetime.datetime.now()}] [OK] Flow file created')
        
        
        # ---------- Select and edit plan file
        pf = PlanConfig(join(PROJECT_FOLDER, rf'Botafogo.p{BASE_PLAN_ID:02d}'))
        
        now =  datetime.datetime.now()
        pf.set_simulation_date(now, now + datetime.timedelta(minutes=TIME_INTERVAL*(N_STEPS - 1)))
        pf.set_flow_file(splitext(flow_path)[1][1:])
        
        plan_path = pf.save_asnew(NEW_PLAN_ID)
        
        print(f'[{datetime.datetime.now()}] [OK] Plan file created')
        
        
        # ---------- Edit project info
        project_path = join(PROJECT_FOLDER, 'Botafogo.prj')
        
        projf = ProjectConfig(project_path)
        pm = ProjectManager(projf)
        
        pm.add_unsteady_file(flow_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Added unsteady file to project')

        pm.add_plan_file(plan_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Added plan file to project')

        pm.set_current_plan(plan_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Selected plan as current')

        
        # ---------- Load project
        proj = rc.open_project(project_path=project_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Project opened')
        
        
        # ---------- Run plan
        rc.show_ras()
        result = rc.compute_current_plan(blocking=True)
        
        print(f'[{datetime.datetime.now()}] [OK] Simulation completed')


        # ---------- Extract results
        print(result)
        
        print(f'[{datetime.datetime.now()}] [OK] Results extracted')
    
    except Exception as e:
        
        print("Simulation run failed:", e)
        
    finally:
        
        # ---------- Close RAS once everything was finished
        rc.terminate()
        
        print(f'[{datetime.datetime.now()}] [OK] RAS Controller closed')


if __name__ == "__main__":
    main()
