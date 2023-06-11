from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from child_flows import child_flow_a, child_flow_b, child_flow_c
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


# ---


class SimulatedFailure(BaseModel):
    child_flow_a: bool = False
    child_flow_b: bool = False
    downstream_task_j: bool = False


default_simulated_failure = SimulatedFailure(
    child_flow_a=False, child_flow_b=False, downstream_task_j=False
)


# prefect deployment build normal_subflows_no_tr.py:normal_subflows_no_tr -n dep-normal-sf-no-tr -t subflows -t normal-sf-no-tr -t parent -a
@flow(persist_result=True, result_storage=S3Bucket(bucket_path=("result-storage")))
def sync_subflows(sim_failure: SimulatedFailure = default_simulated_failure):
    h = upstream_task_h()
    i = upstream_task_i()
    p = downstream_task_p(h)
    a = child_flow_a(i, sim_failure.child_flow_a)
    b = child_flow_b(sim_failure_child_flow_b=sim_failure.child_flow_b, wait_for=[i])
    c = child_flow_c()
    j = downstream_task_j(a, c, sim_failure.downstream_task_j)
    k = downstream_task_k(wait_for=[b])

    return {"j": j, "k": k}


if __name__ == "__main__":
    sync_subflows(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=False, downstream_task_j=False
        )
    )
