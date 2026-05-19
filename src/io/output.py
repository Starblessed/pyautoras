import h5py
import json
import numpy as np
import time
import datetime

import os

def print_hdf5_tree(h5_file, tree=[]):
    k = h5_file.keys()
    for key in k:
        print('-' * len(tree) + '|' + key)
        nk = h5_file[key]
        try:
            print_hdf5_tree(nk, tree=tree+[key])
        except Exception as e:
            print('-' * len(tree) + '|  Data: ' + f'{nk}')
                
class HDF5Output:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.file = h5py.File(self.filepath, 'r')
        
class FloodOutput(HDF5Output):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath)
        self.coordinates: np.ndarray = self.file["/Geometry/2D Flow Areas/Perimeter 1/Cells Center Coordinate"][:] # type: ignore
        self.precipitation: np.ndarray = self.file["/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/Perimeter 1/Cell Cumulative Precipitation Depth"][:] # type: ignore
        self.water_surface: np.ndarray = self.file["/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/Perimeter 1/Water Surface"][:] # type: ignore
        self.timestamps: np.ndarray = self.file["/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp (ms)"][:] # type: ignore
    def save_json(self, save_path: str) -> None:
        """Saves the output to JSON format.

        Args:
            save_path (str): Path to save the result JSON.
        """
        json_obj = {
            "project_filepath": self.filepath,
            "coordinates": self.coordinates.tolist(),
            "precipitation": self.precipitation.tolist(),
            "water_surface": self.water_surface.tolist()
        }
        
        with open(save_path, 'w') as f:
            json.dump(json_obj, f, indent=4)
        
        print(f"Results saved to {save_path}")
    
    def to_dict(self) -> dict:
        """Returns the output in dict format."""
        json_obj = {
            "project_filepath": self.filepath,
            "coordinates": self.coordinates,
            "precipitation": self.precipitation,
            "water_surface": self.water_surface
        }
        
        return json_obj
    
    def get_water_surface(self, timestamp: float, coords):
        pass
        

def get_output_from_plan(project_path: str, project_name: str, plan_number: int) -> FloodOutput:
    res_file = os.path.join(project_path, project_name + f".p{plan_number:02d}" + f".hdf")
    
    assert os.path.exists(res_file), f"No output available for plan {project_name}.p{plan_number:02d}!"
    
    return FloodOutput(filepath=res_file)
        
    
if __name__ == "__main__":
    fo = FloodOutput(r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.p03.hdf')
    
    # print_hdf5_tree(fo.file)
    
    print(fo.coordinates)
    print(fo.precipitation)
    print(fo.water_surface)
    print(fo.timestamps)
    print('OK')
    
    