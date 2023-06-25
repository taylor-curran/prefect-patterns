from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from tasks_subflows_models.child_flows import child_flow_a, child_flow_b, child_flow_c
from pydantic import BaseModel


@task()
def upstream_task_h():
    print("upstream task")
    return {"h": "upstream task"}


@task()
def upstream_task_i():
    print("upstream task")
    return {"i": "upstream task"}


@task()
def mid_subflow_task_f():
    print("mid subflow task")
    return {"f": "mid subflow task"}


@task()
def downstream_task_p(h):
    print(h)
    return {"p": "downstream task"}


@task()
def downstream_task_j(a):
    print("downstream task")
    return {"j": "downstream task"}


@task()
async def downstream_task_j(a, c, sim_failure_downstream_task_j):
    if sim_failure_downstream_task_j:
        raise Exception("This is a test exception")
    else:
        print("downstream task")
        return {"j": "downstream task"}


@task()
def downstream_task_k():
    print("downstream task")
    return {"k": "downstream task"}
