# Trying to figure out if I can have async subflows but its not working

from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from prefect.utilities.asyncutils import sync_compatible

# from tasks_subflows_models.child_flows import child_flow_a, child_flow_b, child_flow_c
from tasks_subflows_models.tasks import (
    upstream_task_h,
    upstream_task_i,
    mid_subflow_upstream_task_f,
    downstream_task_p,
    downstream_task_j,
    downstream_task_k,
)
from tasks_subflows_models.flow_params import SimulatedFailure
from prefect.task_runners import ConcurrentTaskRunner
import tracemalloc

tracemalloc.start()


@task
def task_f():
    print("task f")
    return {"f": "task f"}


@task
def task_m():
    print("task m")
    return {"m": "task m"}


@task
def task_n(m):
    print(m)
    print("task n")
    return {"n": "task n"}


@task
def task_o():
    print("task o")
    return {"o": "task o"}


@sync_compatible
@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def child_flow_a(i, sim_failure_child_flow_a):
    print(f"i: {i}")
    task_f()
    if sim_failure_child_flow_a:
        raise Exception("This is a test exception")
    else:
        return {"a": "child flow a"}


@sync_compatible
@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def child_flow_b(i={"i": "upstream task"}, sim_failure_child_flow_b=False):
    print(f"i: {i}")
    if sim_failure_child_flow_b:
        raise Exception("This is a test exception")
    else:
        return {"b": "child flow b"}


@sync_compatible
@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def child_flow_d():
    o = task_o()
    return {"d": "child flow d"}


# -- Nested Child Flow --
@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def child_flow_c():
    m = task_m()
    n = task_n(m)
    return {"c": n}


# --


@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
async def blocking_subflows(sim_failure: SimulatedFailure = SimulatedFailure()):
    h = upstream_task_h.submit()
    i = upstream_task_i.submit()
    p = downstream_task_p.submit(h)
    a = await child_flow_a.with_options(name="my_flow").submit(
        i, sim_failure.child_flow_a
    )
    f = mid_subflow_task_f.submit()
    b = child_flow_b(sim_failure_child_flow_b=sim_failure.child_flow_b, wait_for=[i])
    c = child_flow_c()
    j = downstream_task_j.submit(a, c, sim_failure.downstream_task_j)
    k = downstream_task_k.submit(wait_for=[b])

    return {"j": j, "k": k}


if __name__ == "__main__":
    blocking_subflows(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=False, downstream_task_j=False
        )
    )
