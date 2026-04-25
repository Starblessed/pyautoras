from src.io.file import ConfigFile
from src.ras.exceptions import NotAPlanException, NotAFlowException
from src.utils import dateutils

import os
from datetime import datetime, timedelta
class PlanConfig(ConfigFile):
    def __init__(self, filepath: str) -> None:
        if not os.path.splitext(filepath)[1].startswith(".p"):
            raise NotAPlanException("Provided filepath does not resolve to a HEC-RAS plan file!")
        super().__init__(filepath, type_id='p')
        
    def set_simulation_date(self, start: datetime, end: datetime, mode: str='hm') -> None:
        f_start = dateutils.hec_ras_format_date(start, mode=mode, sep=',')
        f_end = dateutils.hec_ras_format_date(end, mode=mode, sep=',')
        
        f_str = ",".join([f_start, f_end])
        
        self._set_attribute("Simulation Date", value=f_str)
        
    def set_flow_file(self, flow: str):
        if not flow.startswith('u'):
            raise NotAFlowException("Provided flow identifier does not resolve to a valid flow file!")
        self._set_attribute('Flow File', flow)

if __name__ == "__main__":
    # Load plan
    p = PlanConfig(r'C:\Users\danma\OneDrive\Documentos\Projetos\pyautoras\.devfiles\models\Botafogo\Botafogo copy.p03')
    
    # Set date
    now = datetime.now()
    p.set_simulation_date(now - timedelta(days=4), now - timedelta(days=2))
    
    # Save changes
    p.save_changes()