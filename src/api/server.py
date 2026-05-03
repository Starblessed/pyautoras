from multiprocessing import Process, freeze_support
from secrets import token_hex

from src.api.models.addresses import RedisConfig, Address
from src.ras.RASController import RasController
from src.ras.models.project import ProjectConfig, ProjectManager

from redis import Redis

class ProcessManagerServer:
    
    def __init__(self, redis_config: RedisConfig, max_connections: int=5):
        self.max_connections = max_connections
        self.connections = {}
        self.r = Redis(host=redis_config.address.host, port=redis_config.address.port)
        
        
    def _gen_token_hex(self, length: int=4):
        return token_hex(length)
    
    def create_session(self):
        token = self._gen_token_hex()
        
        # TODO: spawn a process for the run_session method
        
        with self.r.pipeline() as pipe:
            pipe.set(name=f"ses-{token}-lc", value='create', ex=86400)
        return token
    
    @staticmethod
    def run_session(ras_version: str ="7.0"):
        controller = RasController(version=ras_version)
        manager = ProjectManager()
        
        # TODO: create an instance of session and run it
        
        ...
    
    
if __name__ == "__main__":
    addr = Address('localhost', 6973)
    server = ProcessManagerServer(RedisConfig(address=addr), 5)
    print(server._gen_token_hex(8))