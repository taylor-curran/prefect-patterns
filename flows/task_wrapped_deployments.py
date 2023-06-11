from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from prefect.deployments import run_deployment
from prefect.task_runners import ConcurrentTaskRunner
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
def wrapper_task_a(i, sim_failure_child_flow_a):
    print("wrapper task")
    a = run_deployment(
        "child-flow-a/dep-child-a",
        parameters={"i": i, "sim_failure_child_flow_a": sim_failure_child_flow_a},
    )
    return {"a": a.state.result()}


@task()
def wrapper_task_b(sim_failure_child_flow_b):
    print("wrapper task")
    b = run_deployment(
        name="child-flow-b/dep-child-b",
        parameters={"sim_failure_child_flow_b": sim_failure_child_flow_b},
    )
    # WARNING: We do not evaluate the result or state in this
    # wrapper task decoupling this wrapper task from its
    # subflow's state.
    return {"b": "not flow result"}


@task()
def wrapper_task_c():
    print("wrapper task")
    c = run_deployment("child-flow-c/dep-child-c")
    return {"c": c.state.result()}


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
def downstream_task_k(b="b"):
    print(b)
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


# prefect deployment build task_wrapped_deployments.py:task_wrapped_deployments -n dep_task_wrapped -t sub-flows -t task-wrapped -t parent -a
@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
def task_wrapped_deployments(sim_failure: SimulatedFailure = default_simulated_failure):
    h = upstream_task_h.submit()
    i = upstream_task_i.submit()
    a = wrapper_task_a.submit(i, sim_failure.child_flow_a)
    b = wrapper_task_b.submit(
        sim_failure_child_flow_b=sim_failure.child_flow_b, wait_for=[i]
    )
    c = wrapper_task_c.submit()
    j = downstream_task_j.submit(a, c, sim_failure.downstream_task_j)
    k = downstream_task_k.submit(wait_for=[b])

    return {"j": j, "k": k}


# ---

if __name__ == "__main__":
    task_wrapped_deployments(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=True, downstream_task_j=False
        )
    )
