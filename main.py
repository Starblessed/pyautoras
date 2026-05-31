from src.ras.RASController import RasController
from src.io.output import FloodOutput, get_output_from_plan
from src.ras.models.flow import FlowConfig, UnsteadyFlowConfig
from src.ras.models.plan import PlanConfig
from src.ras.models.project import ProjectConfig, ProjectManager, create_project_from_folder
from src.utils.dateutils import hec_ras_format_date, hec_ras_output_string_to_datetime, hec_ras_string_to_datetime
from src.api.models.alert import FloodAlertFeedBuilder

import datetime
import random
from os.path import splitext, join
import numpy as np
import json

from pprint import pprint

import requests

def main():
    
    # ---------- Simulation Config
    N_HOURS: int = 4
    TIME_INTERVAL: int = 15
    TIME_INTEVAL_UNIT: str = 'm'
    
    CURRENT_DATE_OBJ: datetime.datetime = datetime.datetime(year=2019,
                                                            month=4,
                                                            day=9,
                                                            hour=18, minute=0, second=0)
    CURRENT_DATE: str = hec_ras_format_date(dt=CURRENT_DATE_OBJ)
    
    N_STEPS: int = int(60/TIME_INTERVAL) * N_HOURS if TIME_INTEVAL_UNIT == "m" else N_HOURS

    
    BASE_FLOW_ID: int = 2
    BASE_PLAN_ID: int = 3
    
    
    NEW_FLOW_ID: int = 3
    NEW_PLAN_ID: int = 4
    
    SYNTHETIC_PLUVIO_SCALING_FACTOR: int = 3
    
    WATER_SURFACE_THRESHOLDS: list[float] = [0.2, 0.3, 0.4, 0.5]
    
    PROJECT_FOLDER: str = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautora\.devfiles\models\Botafogo'
    GTFS_FOLDER: str = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\data\gtfs_457_mvp\gtfs_457_mvp'
    
    
    # ---------- Create Project
    
    PROJECT_FOLDER: str = create_project_from_folder(PROJECT_FOLDER)
    
    # ---------- Initialize RAS Controller
    ras_version: str = '7.0'
    ras_controller: RasController = RasController(version=ras_version)
        
    print(f'[{datetime.datetime.now()}] [OK] RAS Controller Initialized')
    
    try:
    
        # ---------- Edit flow file
        flow_config: FlowConfig = UnsteadyFlowConfig(filepath=join(PROJECT_FOLDER, rf'Botafogo.u{BASE_FLOW_ID:02d}'))
        
        # pluvio = [random.random() * SYNTHETIC_PLUVIO_SCALING_FACTOR for _ in range(N_STEPS)] # RANDOM SYNTHETIC
        # pluvio = [4 * SYNTHETIC_PLUVIO_SCALING_FACTOR for _ in range(N_STEPS)] # MAX SYNTHETIC
        
        payload: dict = {
            "last_date": CURRENT_DATE.upper(),
            "hours_past": N_HOURS,
            "station_id": 31
        }

        
        
        response: requests.Response = requests.post('http://127.0.0.1:8000/history', json=payload) # SIMULATED API
        pluvio_response: dict = response.json()['response']
        
        
        
        pluvio: list = [p for p in pluvio_response.values()]
        
        
        flow_config.set_precipitation(pluvio)
        flow_config.set_interval(TIME_INTERVAL, TIME_INTEVAL_UNIT)
        
        flow_path: str = flow_config.save_asnew(NEW_FLOW_ID)
        
        print(f'[{datetime.datetime.now()}] [OK] Flow file created')
        
        
        # ---------- Select and edit plan file
        plan_config: PlanConfig = PlanConfig(join(PROJECT_FOLDER, rf'Botafogo.p{BASE_PLAN_ID:02d}'))
        
        now: datetime.datetime =  datetime.datetime.now()
        plan_config.set_simulation_date(CURRENT_DATE_OBJ, CURRENT_DATE_OBJ + datetime.timedelta(minutes=TIME_INTERVAL*(N_STEPS - 1)))
        plan_config.set_flow_file(splitext(flow_path)[1][1:])
        
        plan_path: str = plan_config.save_asnew(NEW_PLAN_ID)
        
        print(f'[{datetime.datetime.now()}] [OK] Plan file created')
        
        
        # ---------- Edit project info
        project_path: str = join(PROJECT_FOLDER, 'Botafogo.prj')
        
        project_config: ProjectConfig = ProjectConfig(project_path)
        project_manager: ProjectManager = ProjectManager(project_config)
        
        project_manager.add_unsteady_file(flow_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Added unsteady file to project')

        project_manager.add_plan_file(plan_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Added plan file to project')

        project_manager.set_current_plan(plan_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Selected plan as current')

        
        # ---------- Load project
        current_project = ras_controller.open_project(project_path=project_path)
        
        print(f'[{datetime.datetime.now()}] [OK] Project opened')
        
        
        # ---------- Run plan
        ras_controller.show_ras()
        result = ras_controller.compute_current_plan(blocking=True)
        
        print(f'[{datetime.datetime.now()}] [OK] Simulation completed')


        # ---------- Extract results
        
        
        plan_result = get_output_from_plan(PROJECT_FOLDER, "Botafogo", 4)
        
        alerts = plan_result.generate_alerts(WATER_SURFACE_THRESHOLDS, join(PROJECT_FOLDER, "autoras.json"))
        
        pprint(alerts)

        gtfs_feed = FloodAlertFeedBuilder(GTFS_FOLDER).build_feed(alerts)
        print(gtfs_feed)
        
        print(f'[{datetime.datetime.now()}] [OK] Results extracted')
    
    except Exception as e:
        
        print("Simulation run failed:", e)
        
    finally:
        
        # ---------- Close RAS once everything was finished
        ras_controller.terminate()
        
        print(f'[{datetime.datetime.now()}] [OK] RAS Controller closed')


if __name__ == "__main__":
    main()
