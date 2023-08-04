from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
from prefect.deployments import run_deployment
from prefect_aws.s3 import S3Bucket
import time
from pydantic import BaseModel


class SimulatedFailure(BaseModel):
    task_a2: bool = False
    task_b1: bool = False
    task_t1: bool = False


# default is 4 for sleep time

@task
def task_t1(sim_failure, sleep_time=2):
    time.sleep(sleep_time/2)
    return "task t1"


# expensive task - long running - 1 day
# b1 fails right before it finishes
@task
def task_b1(sim_failure, sleep_time):
    time.sleep(sleep_time / 2)

    if sim_failure.task_b1:
        raise ValueError("simulated failure of task b1")
    else:
        print("task b1 finishing")

        return "task b1"


@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
def flow_b(sim_failure: SimulatedFailure, sleep_time):
    task_b1(sim_failure=sim_failure, sleep_time=sleep_time)
    return "flow b"


@task
def wrapper_task_b(sim_failure, sleep_time):
    print("deploy run flow b")
    b = run_deployment(
        name="flow-b/b-case-a-local-docker",
        parameters={
            "sim_failure": sim_failure,
            "sleep_time": sleep_time,
        },
    )
    return {"b": b.state.result()}


@task
def task_t2(b, sim_failure, sleep_time=2):
    print(f"I depend on {b}")
    return "task t2"

# @task
# def task_t3(a):
#     print(f"I depend on {a}")
#     return "task t3"

# first to complete - executes inside flow_a
@task
def task_a1():
    return "task a1"

# expensive task - long running - 2 days - executes inside flow_a - depends on task a1
@task
def task_a2(a1, sim_failure, sleep_time):
    time.sleep(sleep_time)

    if sim_failure.task_a2:
        raise ValueError("simulated failure of task a2")
    else:
        print("task a2 finishing")

        return "task a2"


@flow
def flow_a(t1, sim_failure, sleep_time):
    a1 = task_a1(t1)
    a2 = task_a2(a1, sim_failure, sleep_time)

@task
def wrapper_task_a(t1, sim_failure, sleep_time):
    print("deploy run flow a")
    a = run_deployment(
        name="flow-a/a-case-a-local-docker", 
        parameters={
            "t1": t1,
            "sim_failure": sim_failure,
            "sleep_time": sleep_time,
        },
    )
    return {"a": a.state.result()}


@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
def parent_flow_cs_a(sim_failure: SimulatedFailure, sleep_time: int = 4):
    if not sim_failure:
        sim_failure = SimulatedFailure()
    b = wrapper_task_b.submit(sim_failure, sleep_time)
    t1 = task_t1.submit(sim_failure, sleep_time)
    task_t2(b, sim_failure, sleep_time=2)
    a = wrapper_task_a(t1, sim_failure, sleep_time)
    # t3 = t3(a)


if __name__ == "__main__":
    sim_failure = SimulatedFailure(
        task_a2=False, 
        task_b1=False, 
        task_t1=False
        )
    sleep_time = 4

    # Call flow function
    parent_flow_cs_a(sim_failure, sleep_time=sleep_time)
