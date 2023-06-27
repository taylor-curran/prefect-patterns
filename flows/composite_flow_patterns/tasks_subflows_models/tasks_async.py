from custom_decorators_add_sleeps import flow, task
from prefect_aws.s3 import S3Bucket
from prefect.utilities.asyncutils import sync_compatible

# thanks to sync_compatible, these tasks can be defined as async but still run in a synchronous flow
# the same cannot be said for a task that is not async, it will error out if executed in an asyncio.gather()


@task()
async def upstream_task_h():
    print("upstream task")
    return {"h": "upstream task"}


@task()
async def upstream_task_i():
    print("upstream task")
    return {"i": "upstream task"}


@task()
async def mid_subflow_upstream_task_f():
    print("mid subflow task")
    return {"f": "mid subflow task"}


@task()
async def downstream_task_p(h):
    print(h)
    return {"p": "downstream task"}


@task()
async def downstream_task_j(a, c=None, sim_failure_downstream_task_j=False):
    if sim_failure_downstream_task_j:
        raise Exception("This is a test exception")
    else:
        print("downstream task")
        return {"j": "downstream task"}


@task()
async def downstream_task_k(b=None):
    k = b
    print("downstream task")
    return {"k": "downstream task"}
