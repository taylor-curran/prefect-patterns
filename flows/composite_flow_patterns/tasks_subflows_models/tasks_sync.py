from custom_decorators_add_sleeps import flow, task
from prefect_aws.s3 import S3Bucket
from pydantic import BaseModel

# If a team will be using only Prefect's TaskRunners for their Concurrent/Asynchronous Execution, they can define their tasks like below.
# In other words, if a team does not intend to run any subflows or tasks as awaitable coroutines, they should leave their tasks as normal sync functions.


@task()
def upstream_task_h():
    print("upstream task")
    return {"h": "upstream task"}


@task()
def upstream_task_i():
    print("upstream task")
    return {"i": "upstream task"}


@task()
def mid_subflow_upstream_task_f():
    print("mid subflow task")
    return {"f": "mid subflow task"}


@task()
def downstream_task_p(h):
    print(h)
    return {"p": "downstream task"}


@task()
def downstream_task_j(a, c=None, sim_failure_downstream_task_j=False):
    if sim_failure_downstream_task_j:
        raise Exception("This is a test exception")
    else:
        print("downstream task")
        return {"j": "downstream task"}


@task()
def downstream_task_k(b=None):
    k = b
    print("downstream task")
    return {"k": "downstream task"}
