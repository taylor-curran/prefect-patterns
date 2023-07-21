from prefect import task, flow
from prefect.states import Paused

@task
def pause_sometimes(pause):
    import random
    if random.random() > 0.5:
        print('Pausing!!')
        return Paused()

@flow(log_prints=True) 
def pause_flow():
    pause_sometimes(True)
    return 42

if __name__ == "__main__":
    pause_flow()