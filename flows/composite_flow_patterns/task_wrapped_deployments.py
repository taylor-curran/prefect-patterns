from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from prefect.deployments import run_deployment
from tasks_subflows_models.tasks_sync import (  # could import from either tasks_async or tasks_sync
    upstream_task_h,
    upstream_task_i,
    mid_subflow_upstream_task_f,
    downstream_task_p,
    downstream_task_j,
    downstream_task_k,
)
from tasks_subflows_models.flow_params import SimulatedFailure
from prefect.task_runners import ConcurrentTaskRunner
import time


@task()
def wrapper_task_a(i, sim_failure_child_flow_a, sleep_time=0):
    print("wrapper task")
    a = run_deployment(
        "child-flow-a/a-local-docker",
        parameters={
            "i": i,
            "sim_failure_child_flow_a": sim_failure_child_flow_a,
            "sleep_time": sleep_time,
        },
    )
    return {"a": a.state.result()}


@task()
def wrapper_task_b(sim_failure_child_flow_b, sleep_time=0):
    print("wrapper task")
    b = run_deployment(
        name="child-flow-b/b-local-docker",
        parameters={
            "sim_failure_child_flow_b": sim_failure_child_flow_b,
            "sleep_time": sleep_time,
        },
    )
    # WARNING: We do not evaluate the result or state in this
    # wrapper task decoupling this wrapper task from its
    # subflow's state. This is the "fire and forget" approach.
    return {"b": "not flow result"}


@task()
def wrapper_task_c(sleep_time=0):
    print("wrapper task")
    c = run_deployment(
        name="child-flow-c/c-local-docker", parameters={"sleep_time": sleep_time}
    )
    return {"c": c.state.result()}


@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
def task_wrapped_deployments(
    sim_failure: SimulatedFailure = SimulatedFailure(), sleep_time_subflows: int = 0
):
    h = upstream_task_h.submit()
    i = upstream_task_i.submit()
    p = downstream_task_p.submit(h)
    a = wrapper_task_a.submit(
        i, sim_failure.child_flow_a, sleep_time=sleep_time_subflows
    )
    f = mid_subflow_upstream_task_f.submit()
    b = wrapper_task_b.submit(
        sim_failure_child_flow_b=sim_failure.child_flow_b,
        sleep_time=sleep_time_subflows,
        wait_for=[i],
    )
    c = wrapper_task_c.submit(sleep_time=sleep_time_subflows)
    j = downstream_task_j.submit(a, c, sim_failure.downstream_task_j)
    k = downstream_task_k.submit(wait_for=[b])
    time.sleep(sleep_time_subflows)

    return {"j": j, "k": k}


# ---

if __name__ == "__main__":
    task_wrapped_deployments(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=False, downstream_task_j=False
        ),
        sleep_time_subflows=0,
    )
