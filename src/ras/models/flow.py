import math
import random
import os

from typing import Literal

from src.io.file import ConfigFile
from src.ras.exceptions import NotAFlowException

def format_precipitation(values: list[float]):
    prec_strs = []
    
    for v in values:
        rounded = round(v, 1)
        if rounded == int(rounded):
            prec_strs.append(str(int(v)).rjust(8))
        else:
            prec_strs.append(f"{rounded}".lstrip('0').rjust(8))
        
    return ["".join(prec_strs[n:min(n+10, len(prec_strs))]) + "\n" for n in range(0, len(prec_strs), 10)]

class FlowConfig(ConfigFile):
    def __init__(self, filepath: str, type_id: str | None=None):
        if not os.path.splitext(filepath)[1].startswith(".u"):
            raise NotAFlowException("Provided filepath does not resolve to a HEC-RAS flow file!")
        super().__init__(filepath, type_id=type_id)

class UnsteadyFlowConfig(FlowConfig):
    def __init__(self, filepath: str):
        super().__init__(filepath, type_id='u')
        
    def set_precipitation(self, values: list[float]):
        prec_line = 0
        prec_length = 0
        prec_nlines = 0
        prec_length, prec_line = self._get_attribute('Precipitation Hydrograph')
        
        prec_nlines = math.ceil(int(prec_length) / 10)
        
        self._set_attribute('Precipitation Hydrograph', len(values), prec_line)
        
        # Manually add the other lines
        self._lines[prec_line + 1:prec_line + prec_nlines + 1] = format_precipitation(values=values)

            
    def set_interval(self, value: int, unit: Literal['s', 'm', 'h']='s'):
        match unit:
            case 's':
                interval_str = f"{value}SEC"
            case 'm':
                interval_str = f"{value}MIN"
            case 'h':
                interval_str = f"{value}HOUR"
            case _:
                raise(ValueError(f"{unit} is not a valid unit! Try: s | m | h"))
        
        self._set_attribute("Interval", interval_str)


if __name__ == "__main__":
    ru = [random.random()*3 for _ in range(192)]
    u = UnsteadyFlowConfig(r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo copy.u02')
    
    u.set_precipitation(ru)
    u.set_interval(30, 'm')
    
    u.save_asnew(3)