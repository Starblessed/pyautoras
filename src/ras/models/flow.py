import math
import random

def format_precipitation(values: list[float]):
    prec_strs = []
    
    for v in values:
        rounded = round(v, 1)
        if rounded == int(rounded):
            prec_strs.append(str(int(v)).rjust(8))
        else:
            prec_strs.append(f"{rounded}".lstrip('0').rjust(8))
        
    return ["".join(prec_strs[n:min(n+10, len(prec_strs))]) + "\n" for n in range(0, len(prec_strs), 10)]

class FlowConfig:
    def __init__(self, filepath: str):
        self.filepath = filepath
        

class UnsteadyFlowConfig(FlowConfig):
    def __init__(self, filepath: str):
        super().__init__(filepath)
        
    def set_precipitation(self, values: list[float]):
        prec_line = 0
        prec_length = 0
        prec_nlines = 0
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
            
            for i, line in enumerate(lines):
                if "Precipitation Hydrograph=" in line:
                    prec_length = int(line.strip().split('=')[1])
                    prec_line = i
                    prec_nlines = math.ceil(prec_length / 10)
                    break
        
        lines[prec_line + 1:prec_line + prec_nlines + 1] = format_precipitation(values=values)
        
        with open(self.filepath, 'w') as f:
            f.writelines(lines)
            
            
            


if __name__ == "__main__":
    ru = [random.random()*3 for _ in range(192)]
    u = UnsteadyFlowConfig(r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo copy.u02')
    
    u.set_precipitation(ru)