from prefect import flow, task
from prefect.deployments import run_deployment
from pydantic import BaseModel
from prefect_aws.s3 import S3Bucket
import asyncio

@task
async def task_f():
    print("task f")
    return {"f": "task f"}


@task
async def task_m():
    print("task m")
    return {"m": "task m"}


@task
async def task_n(m):
    print(m)
    print("task n")
    return {"n": "task n"}


@task
async def task_o():
    print("task o")
    return {"o": "task o"}


@flow(persist_result=True)
async def child_flow_a(i, sim_failure_child_flow_a):
    print(f"i: {i}")
    if sim_failure_child_flow_a:
        raise Exception("This is a test exception")
    else:
        return {"a": "child flow a"}


@flow(persist_result=True)
async def child_flow_b(i={"i": "upstream task"}, sim_failure_child_flow_b=False):
    print(f"i: {i}")
    if sim_failure_child_flow_b:
        raise Exception("This is a test exception")
    else:
        return {"b": "child flow b"}


@flow(persist_result=True)
async def child_flow_d():
    o = await task_o()
    return {"d": "child flow d"}


# -- Nested Child Flow --
@flow(persist_result=True)
async def child_flow_c():
    first_round = await asyncio.gather(*[child_flow_d(), task_m()])
    d, m = first_round
    n = await task_n(m)
    return {"c": d, "n": n}


# --


@task()
def upstream_task_h():
    print("upstream task")
    return 'hi'


@task()
async def upstream_task_i():
    print("upstream task")
    return {"i": "upstream task"}


@task()
async def downstream_task_j(a, c, sim_failure_downstream_task_j):
    if sim_failure_downstream_task_j:
        raise Exception("This is a test exception")
    else:
        print("downstream task")
        return {"j": "downstream task"}


@task()
async def downstream_task_k(d):
    print("downstream task")
    return {"k": "downstream task"}


# ---


class SimulatedFailure(BaseModel):
    child_flow_a: bool = False
    child_flow_b: bool = False
    downstream_task_j: bool = False


default_simulated_failure = SimulatedFailure(
    child_flow_a=False, child_flow_b=False, downstream_task_j=False
)


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def asyncio_gather_sub_flows(
    sim_failure: SimulatedFailure = default_simulated_failure,
):
    first_round = await asyncio.gather(
        *[upstream_task_h(), upstream_task_i(), child_flow_c()]
    )
    h, i, c = first_round

    second_round = await asyncio.gather(
        *[
            child_flow_a(i, sim_failure.child_flow_a),
            child_flow_b(i, sim_failure.child_flow_b),
        ]
    )

    a, b = second_round

    third_round = await asyncio.gather(
        *[downstream_task_j(a, c, sim_failure.downstream_task_j), downstream_task_k(b)]
    )

    j, k = third_round

    return {"j": j, "k": k}


# ---

if __name__ == "__main__":
    asyncio.run(
        asyncio_gather_sub_flows(
            sim_failure=SimulatedFailure(
                child_flow_a=False, child_flow_b=False, downstream_task_j=False
            )
        )
    )
