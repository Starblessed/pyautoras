from src.worker.celery_app import celery_app
from src.ras.RASController import RasController
import time
import redis

r = redis.Redis(host='localhost', port=6379, db=0)


@celery_app.task(bind=True)
def create_session(self):
    rc = None
    try:
        ras_version = '7.0'
        rc = RasController(version=ras_version)
        session_id = rc.create_session_id(self.request.id)

        r.set(f"{session_id}:stop", "0", ex=3600)

        while True:
            stop = r.get(f"{session_id}:stop")
            if stop == b"1":
                print("Stop signal received. Terminating session.")
                break
            time.sleep(1)

    except Exception as e:
        print(f'Error: {e}')
    finally:
        r.delete(f"{session_id}:stop")
        if rc:    
            rc.terminate()
        print("Task finished")

@celery_app.task(bind=True)
def logout_session(self, task_id):
    try:
        r.set(f"{task_id}:stop", "1")
    except Exception as e:
        print(f'Error: {e}')
    finally:
        print("Task finished")