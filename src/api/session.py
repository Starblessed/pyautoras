# TODO: Session Class for managing io within an isolated process

from datetime import datetime, timedelta
from os.path import join, basename, splitext, relpath, abspath, exists, dirname
import requests

from src.ras.RASController import RasController
from src.io.output import FloodOutput, get_output_from_plan
from src.ras.models.flow import FlowConfig, UnsteadyFlowConfig
from src.ras.models.plan import PlanConfig
from src.ras.models.project import ProjectConfig, ProjectManager, create_project_from_folder
from src.utils.dateutils import hec_ras_format_date


class Session:
    def __init__(self, project_path: str, copy_to: str | None = None):
        
        self.project_path = project_path
        
        if copy_to is not None:
            self.project_path = self._copy_project(origin=project_path, destination=copy_to)
            
    def _copy_project(self, origin: str, destination: str) -> str:
        if not exists(origin):
            raise FileNotFoundError(f"Origin path not found: {origin}")
        elif not exists(destination):
            raise FileNotFoundError(f"Destination path not found: {destination}")
        
        project_path = create_project_from_folder(origin_path=origin, dest_path=destination)
        
        return project_path
    

def run_from_single_command(project_path: str, simulation_end_date: datetime,
                            latitude: float, longitude: float,
                            simulation_hours: int = 4, ras_version: str = '7.0',
                            base_flow_id: int = 2, new_flow_id: int = 3,
                            base_plan_id: int = 3, new_plan_id: int = 4):
    
    ws: float | None = None
    
    n_steps: int = int(60/15) * simulation_hours
    current_date: str = hec_ras_format_date(dt=simulation_end_date)
    
    # ---------- Initialize RAS Controller
    ras_controller: RasController = RasController(version=ras_version)
        
    print(f'[{datetime.now()}] [OK] RAS Controller Initialized')
    
    try:
    
        # ---------- Edit flow file
        flow_config: FlowConfig = UnsteadyFlowConfig(filepath=join(project_path, rf'Botafogo.u{base_flow_id:02d}'))
        
        payload: dict = {
            "last_date": current_date.upper(),
            "hours_past": simulation_hours,
            "station_id": 31
        }

        
        
        response: requests.Response = requests.post('http://127.0.0.1:8000/history', json=payload) # SIMULATED API
        pluvio_response: dict = response.json()['response']
        
        
        
        pluvio: list = [p for p in pluvio_response.values()]
        
        
        flow_config.set_precipitation(pluvio)
        flow_config.set_interval(15, 'm')
        
        flow_path: str = flow_config.save_asnew(new_flow_id)
        
        print(f'[{datetime.now()}] [OK] Flow file created')
        
        
        # ---------- Select and edit plan file
        plan_config: PlanConfig = PlanConfig(join(project_path, rf'Botafogo.p{base_plan_id:02d}'))
        
        now: datetime =  datetime.now()
        plan_config.set_simulation_date(simulation_end_date, simulation_end_date + timedelta(minutes=15*(n_steps - 1)))
        plan_config.set_flow_file(splitext(flow_path)[1][1:])
        
        plan_path: str = plan_config.save_asnew(new_plan_id)
        
        print(f'[{datetime.now()}] [OK] Plan file created')
        
        
        # ---------- Edit project info
        prj_path = join(project_path, 'Botafogo.prj')
        
        project_config: ProjectConfig = ProjectConfig(prj_path)
        project_manager: ProjectManager = ProjectManager(project_config)
        
        project_manager.add_unsteady_file(flow_path)
        
        print(f'[{datetime.now()}] [OK] Added unsteady file to project')

        project_manager.add_plan_file(plan_path)
        
        print(f'[{datetime.now()}] [OK] Added plan file to project')

        project_manager.set_current_plan(plan_path)
        
        print(f'[{datetime.now()}] [OK] Selected plan as current')

        
        # ---------- Load project
        current_project = ras_controller.open_project(project_path=prj_path)
        
        print(f'[{datetime.now()}] [OK] Project opened')
        
        
        # ---------- Run plan
        ras_controller.show_ras()
        result = ras_controller.compute_current_plan(blocking=True)
        
        print(f'[{datetime.now()}] [OK] Simulation completed')


        # ---------- Extract results
        plan_result = get_output_from_plan(project_path, "Botafogo", 4)

        ws = float(plan_result.get_water_surface(hec_ras_format_date(simulation_end_date), (latitude, longitude)))
        
        print(type(ws))
        
        print(f'[{datetime.now()}] [OK] Results extracted')
    
    except Exception as e:
       
        print("Simulation run failed:", e)
        
    finally:
        
        # ---------- Close RAS once everything was finished
        ras_controller.terminate()
        
        print(f'[{datetime.now()}] [OK] RAS Controller closed')
        
        return ws
    
def alerts_from_single_command(project_path: str, simulation_end_date: datetime,
                            alert_thresholds: list[float],
                            simulation_hours: int = 4, ras_version: str = '7.0',
                            base_flow_id: int = 2, new_flow_id: int = 3,
                            base_plan_id: int = 3, new_plan_id: int = 4):
    
    
    n_steps: int = int(60/15) * simulation_hours
    current_date: str = hec_ras_format_date(dt=simulation_end_date)
    
    # ---------- Initialize RAS Controller
    ras_controller: RasController = RasController(version=ras_version)
        
    print(f'[{datetime.now()}] [OK] RAS Controller Initialized')
    
    try:
    
        # ---------- Edit flow file
        flow_config: FlowConfig = UnsteadyFlowConfig(filepath=join(project_path, rf'Botafogo.u{base_flow_id:02d}'))
        
        payload: dict = {
            "last_date": current_date.upper(),
            "hours_past": simulation_hours,
            "station_id": 31
        }

        
        
        response: requests.Response = requests.post('http://127.0.0.1:8000/history', json=payload) # SIMULATED API
        pluvio_response: dict = response.json()['response']
        
        
        
        pluvio: list = [p for p in pluvio_response.values()]
        
        
        flow_config.set_precipitation(pluvio)
        flow_config.set_interval(15, 'm')
        
        flow_path: str = flow_config.save_asnew(new_flow_id)
        
        print(f'[{datetime.now()}] [OK] Flow file created')
        
        
        # ---------- Select and edit plan file
        plan_config: PlanConfig = PlanConfig(join(project_path, rf'Botafogo.p{base_plan_id:02d}'))
        
        now: datetime =  datetime.now()
        plan_config.set_simulation_date(simulation_end_date, simulation_end_date + timedelta(minutes=15*(n_steps - 1)))
        plan_config.set_flow_file(splitext(flow_path)[1][1:])
        
        plan_path: str = plan_config.save_asnew(new_plan_id)
        
        print(f'[{datetime.now()}] [OK] Plan file created')
        
        
        # ---------- Edit project info
        prj_path = join(project_path, 'Botafogo.prj')
        
        project_config: ProjectConfig = ProjectConfig(prj_path)
        project_manager: ProjectManager = ProjectManager(project_config)
        
        project_manager.add_unsteady_file(flow_path)
        
        print(f'[{datetime.now()}] [OK] Added unsteady file to project')

        project_manager.add_plan_file(plan_path)
        
        print(f'[{datetime.now()}] [OK] Added plan file to project')

        project_manager.set_current_plan(plan_path)
        
        print(f'[{datetime.now()}] [OK] Selected plan as current')

        
        # ---------- Load project
        current_project = ras_controller.open_project(project_path=prj_path)
        
        print(f'[{datetime.now()}] [OK] Project opened')
        
        
        # ---------- Run plan
        ras_controller.show_ras()
        result = ras_controller.compute_current_plan(blocking=True)
        
        print(f'[{datetime.now()}] [OK] Simulation completed')


        # ---------- Extract results
        plan_result = get_output_from_plan(project_path, "Botafogo", 4)

        ws = float(plan_result.get_water_surface(hec_ras_format_date(simulation_end_date), (latitude, longitude)))
        
        print(type(ws))
        
        print(f'[{datetime.now()}] [OK] Results extracted')
    
    except Exception as e:
       
        print("Simulation run failed:", e)
        
    finally:
        
        # ---------- Close RAS once everything was finished
        ras_controller.terminate()
        
        print(f'[{datetime.now()}] [OK] RAS Controller closed')
        

    
        
        
if __name__ == "__main__":
    
     # ---------- Simulation Config
    N_HOURS: int = 2
    TIME_INTERVAL: int = 15
    TIME_INTEVAL_UNIT: str = 'm'
    
    CURRENT_DATE_OBJ: datetime = datetime(year=2019,
                                          month=4,
                                          day=9,
                                          hour=18, minute=0, second=0)
    CURRENT_DATE: str = hec_ras_format_date(dt=CURRENT_DATE_OBJ)
    
    BASE_FLOW_ID: int = 2
    BASE_PLAN_ID: int = 3
    
    
    NEW_FLOW_ID: int = 3
    NEW_PLAN_ID: int = 4
    
    PROJECT_FOLDER: str = r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\projects\Botafogo1'
    
    res = run_from_single_command(PROJECT_FOLDER, CURRENT_DATE_OBJ, N_HOURS, '7.0',
                                  BASE_FLOW_ID, NEW_FLOW_ID, BASE_PLAN_ID, NEW_PLAN_ID)