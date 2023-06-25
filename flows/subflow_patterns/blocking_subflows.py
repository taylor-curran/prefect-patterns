from prefect import flow
from prefect_aws.s3 import S3Bucket
from tasks_subflows_models.child_flows import child_flow_a, child_flow_b, child_flow_c
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


@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
def blocking_subflows(sim_failure: SimulatedFailure = SimulatedFailure()):
    h = upstream_task_h.submit()
    i = upstream_task_i.submit()
    p = downstream_task_p.submit(h)
    a = child_flow_a(i, sim_failure.child_flow_a)
    # even though task_f has no dependencies it will still wait for child_flow_a to finish as subflow_a is blocking
    f = mid_subflow_upstream_task_f.submit()
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
