from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from tasks_subflows_models.child_flows import child_flow_a, child_flow_b, child_flow_c
from tasks_subflows_models.tasks import upstream_task_h, upstream_task_i, mid_subflow_task_f, downstream_task_p, downstream_task_j, downstream_task_k
from tasks_subflows_models.flow_params import SimulatedFailure
from tasks_subflows_models.flow_params import SimulatedFailure
from prefect.task_runners import ConcurrentTaskRunner

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

@flow(task_runner=ConcurrentTaskRunner(), persist_result=True)
def just_tasks(sim_failure: SimulatedFailure = SimulatedFailure()):
    h = upstream_task_h.submit()
    i = upstream_task_i.submit()
    p = downstream_task_p.submit(h)
    a = task_a.submit(i, sim_failure.child_flow_a)
    f = mid_subflow_task_f.submit()
    b = task_b.submit(
        sim_failure_child_flow_b=sim_failure.child_flow_b, wait_for=[i]
    )
    c = task_c.submit()
    j = downstream_task_j.submit(a, c, sim_failure.downstream_task_j)
    k = downstream_task_k.submit(wait_for=[b])

    return {"j": j, "k": k}


# ---

if __name__ == "__main__":
    just_tasks(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=False, downstream_task_j=False
        )
    )