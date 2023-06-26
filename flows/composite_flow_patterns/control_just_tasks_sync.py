from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from tasks_subflows_models.tasks_sync import (  # could import from either tasks_async or tasks_sync
    upstream_task_h,
    upstream_task_i,
    mid_subflow_upstream_task_f,
    downstream_task_p,
    downstream_task_j,
    downstream_task_k,
)
from tasks_subflows_models.flow_params import SimulatedFailure

# This flow contains only tasks to serve as a control against subflow behavior


@task
def task_a(i, sim_failure_child_flow_a):
    print(f"i: {i}")
    if sim_failure_child_flow_a:
        raise Exception("This is a test exception")
    else:
        return {"a": "child flow a"}


@task
def task_b(i={"i": "upstream task"}, sim_failure_child_flow_b=False):
    print(f"i: {i}")
    if sim_failure_child_flow_b:
        raise Exception("This is a test exception")
    else:
        return {"b": "child flow b"}


@task
def task_d():
    return {"d": "child flow d"}


@task
def task_c():
    d = "child_flow_d"
    return {"c": d}


# ---


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
def just_tasks_sync(sim_failure: SimulatedFailure = SimulatedFailure()):
    h = upstream_task_h()
    i = upstream_task_i()
    p = downstream_task_p(h)
    a = task_a(i, sim_failure.child_flow_a)
    f = mid_subflow_upstream_task_f()
    b = task_b(sim_failure_child_flow_b=sim_failure.child_flow_b, wait_for=[i])
    c = task_c()
    j = downstream_task_j(a, c, sim_failure.downstream_task_j)
    k = downstream_task_k(wait_for=[b])

    return {"j": j, "k": k}


# ---

if __name__ == "__main__":
    just_tasks_sync(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=False, downstream_task_j=False
        )
    )