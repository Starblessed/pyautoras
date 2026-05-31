import h5py
import json
import numpy as np
import time
import datetime

import os

from pyproj import Transformer

from src.utils.dateutils import hec_ras_string_to_datetime, hec_ras_output_string_to_datetime

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
        self.timestamps: list = [hec_ras_output_string_to_datetime(t) for t in self.file["/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp (ms)"][:]] # type: ignore
        self.min_elevation: np.ndarray = self.file["/Geometry/2D Flow Areas/Perimeter 1/Cells Minimum Elevation"][:] # type: ignore
        self.corrected_water_surface: np.ndarray = self._correct_water_surface(self.water_surface, self.min_elevation)
        
    @staticmethod
    def _correct_water_surface(water_surface: np.ndarray, min_elevation: np.ndarray) -> np.ndarray:
        corrected = water_surface - min_elevation[np.newaxis, :]
        finite = np.isfinite(corrected)

        if not finite.any():
            return corrected

        values = corrected[finite]
        std = np.std(values)

        if not np.isfinite(std) or std == 0:
            return corrected

        z_scores = np.abs((values - np.mean(values)) / std)
        non_outliers = values[z_scores <= 1.5]

        if non_outliers.size == 0:
            return corrected

        capped = corrected.copy()
        capped[finite] = np.clip(values, np.min(non_outliers), np.max(non_outliers))

        return capped
    
    @staticmethod
    def _group_step_alerts(step_alerts: list[dict], proximity_threshold: float) -> list[list[dict]]:
        if proximity_threshold <= 0:
            return [[alert] for alert in step_alerts]

        cells: dict[tuple[int, int], list[int]] = {}

        for idx, alert in enumerate(step_alerts):
            key = (
                int(np.floor(alert["x"] / proximity_threshold)),
                int(np.floor(alert["y"] / proximity_threshold))
            )
            cells.setdefault(key, []).append(idx)

        groups = []
        visited = set()

        for idx in range(len(step_alerts)):
            if idx in visited:
                continue

            group = []
            stack = [idx]
            visited.add(idx)

            while stack:
                current = stack.pop()
                alert = step_alerts[current]
                group.append(alert)

                cell_x = int(np.floor(alert["x"] / proximity_threshold))
                cell_y = int(np.floor(alert["y"] / proximity_threshold))

                for nx in range(cell_x - 1, cell_x + 2):
                    for ny in range(cell_y - 1, cell_y + 2):
                        for candidate in cells.get((nx, ny), []):
                            if candidate in visited:
                                continue

                            other = step_alerts[candidate]
                            distance = np.linalg.norm(
                                np.array([alert["x"], alert["y"]]) - np.array([other["x"], other["y"]])
                            )

                            if distance <= proximity_threshold:
                                visited.add(candidate)
                                stack.append(candidate)

            groups.append(group)

        return groups
        
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
            "water_surface": self.water_surface,
            "timestamps": self.timestamps
        }
        
        return json_obj
    
    def get_water_surface(self, timestamp: str, coords: tuple[float, float]) -> float:
        
        closest_t = self.get_closest_timestamp(timestamp=timestamp)
        closest_cell = self.get_cell(coords=coords)

        return float(self.corrected_water_surface[closest_t, closest_cell])
    
    def get_cell(self, coords: tuple[float, float]):
        
        distances = np.linalg.norm(self.coordinates - coords, axis=1)
        idx = [i for i in range(len(distances))]
        distances, idx = zip(*sorted(zip(distances, idx)))
        
        for i in idx:
            if not np.isnan(self.min_elevation[i]):
                return i
        
        else:
            raise ValueError("No available non-nan value was found. Terrain must be corrupted!")
    
    def get_closest_timestamp(self, timestamp: str):
        parsed_datetime = hec_ras_string_to_datetime(timestamp)
        
        return self.timestamps.index(min(self.timestamps, key=lambda x: abs(x - parsed_datetime)))
        
    
    def save_csv(self, autoras_path: str, save_path: str | None = None) -> None:
        if save_path is None:
            save_path = self.filepath

        with open(autoras_path, 'r') as f:
            obj = json.load(f)
            epsg_in = obj["project_epsg"]
            epsg_out = obj["dest_epsg"]

        transformer = Transformer.from_crs(epsg_in, epsg_out, always_xy=True)

        ts_raw = self.file[
            "/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp"
        ][:] # type: ignore

        timestamps = [
            datetime.datetime.strptime(
                t.decode("utf-8"),
                "%d%b%Y %H:%M:%S"
            ).isoformat()
            for t in ts_raw # type: ignore
        ]

        with open(save_path + ".csv", "w") as f:
            f.write("latitude,longitude,timestamp,cell_id,water_surface,depth\n")

            for step_id, (snapshot, corrected_snapshot, t) in enumerate(zip(self.water_surface, self.corrected_water_surface, timestamps)):
                print(f"Exporting step {step_id + 1}...")

                for cell_id, (xy, ws, depth) in enumerate(zip(self.coordinates, snapshot, corrected_snapshot)):
                    min_z = self.min_elevation[cell_id] # type: ignore

                    if np.isnan(min_z): # type: ignore
                        continue

                    depth = float(depth)

                    # Critical: skip dry cells
                    if depth <= 0.01:
                        continue

                    lon, lat = transformer.transform(float(xy[0]), float(xy[1]))

                    f.write(
                        f"{lat},{lon},{t},{cell_id},{float(ws)},{depth}\n"
                    )
                    
    def generate_alerts(self, water_surface_thresholds: list[float], autoras_path: str, save_path: str | None = None, proximity_threshold: float = 50.0) -> dict:
        if save_path is None:
            save_path = self.filepath

        with open(autoras_path, 'r') as f:
            obj = json.load(f)
            epsg_in = obj["project_epsg"]
            epsg_out = obj["dest_epsg"]

        transformer = Transformer.from_crs(epsg_in, epsg_out, always_xy=True)

        ts_raw = self.file[
            "/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/Time Date Stamp"
        ][:] # type: ignore

        timestamps = [
            datetime.datetime.strptime(
                t.decode("utf-8"),
                "%d%b%Y %H:%M:%S"
            ).isoformat()
            for t in ts_raw # type: ignore
        ]

        alerts = {"alerts": []}
        criticity_rank = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4
        }
        
        for step_id, (snapshot, t) in enumerate(zip(self.corrected_water_surface, timestamps)):
            print(f"Exporting step {step_id + 1}...")
            step_alerts = []

            for cell_id, (xy, depth) in enumerate(zip(self.coordinates, snapshot)):
                min_z = self.min_elevation[cell_id] # type: ignore

                if np.isnan(min_z): # type: ignore
                    continue

                depth = float(depth)

                
                criticity: str
                
                # Critical: skip dry cells
                if depth <= min(water_surface_thresholds):
                    continue
                elif water_surface_thresholds[0] < depth < water_surface_thresholds[1]:
                    criticity = 'LOW'
                elif water_surface_thresholds[1] < depth < water_surface_thresholds[2]:
                    criticity = 'MEDIUM'
                elif water_surface_thresholds[2] < depth < water_surface_thresholds[3]:
                    criticity = 'HIGH'
                else:
                    criticity = 'CRITICAL'

                step_alerts.append(
                    {
                        "datetime": t,
                        "x": float(xy[0]),
                        "y": float(xy[1]),
                        "criticity": criticity
                     }
                )
            
            for group in self._group_step_alerts(step_alerts, proximity_threshold):
                x = float(np.mean([alert["x"] for alert in group]))
                y = float(np.mean([alert["y"] for alert in group]))
                criticity = max(group, key=lambda alert: criticity_rank[alert["criticity"]])["criticity"]
                lon, lat = transformer.transform(x, y)

                alerts["alerts"].append(
                    {
                        "datetime": t,
                        "latitude": lat,
                        "longitude": lon,
                        "criticity": criticity
                    }
                )
                
        if save_path is not None:
            with open(save_path + ".json", "w") as f:
                obj = json.dumps(alerts, indent=4)
                f.write(obj)
        
        return alerts

def get_output_from_plan(project_path: str, project_name: str, plan_number: int) -> FloodOutput:
    
    res_file = os.path.join(project_path, project_name + f".p{plan_number:02d}" + f".hdf")
    
    
    assert os.path.exists(res_file), f"No output available at {res_file}!"
    
    return FloodOutput(filepath=res_file)
        
    
if __name__ == "__main__":
    fo = FloodOutput(r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo.p03.hdf')
    
    # print_hdf5_tree(fo.file)
    
    print(fo.coordinates)
    print(fo.precipitation)
    print(fo.water_surface)
    print(fo.timestamps)
    print('OK')
    
    
