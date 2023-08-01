from prefect import flow
from prefect_aws.s3 import S3Bucket
import time
from tasks_subflows_models.child_flows_sync import (  # could import from either child_flows_async or child_flows_sync
    child_flow_a,
    child_flow_b,
    child_flow_c,
)
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
from prefect.deployments import run_deployment


@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
def sub_deployments(sim_failure: SimulatedFailure = None, sleep_time_subflows: int = 0):
    """
    description
    """
    if not sim_failure:
        sim_failure = SimulatedFailure()
    h = upstream_task_h.submit()
    i = upstream_task_i.submit()
    p = downstream_task_p.submit(h)
    a = run_deployment(
        "child-flow-a/a-local-docker",
        parameters={
            "i": i.result(),
            "sim_failure_child_flow_a": sim_failure.child_flow_a,
            "sleep_time": sleep_time_subflows,
        },
    )
    # even though task_f has no dependencies it will still wait for child_flow_a to finish as subflow_a is blocking
    f = mid_subflow_upstream_task_f.submit()
    b = run_deployment(
        name="child-flow-b/b-local-docker",
        parameters={
            "sim_failure_child_flow_b": sim_failure.child_flow_b,
            "sleep_time": sleep_time_subflows,
        },
    )
    c = run_deployment(
        name="child-flow-c/c-local-docker",
        parameters={"sleep_time": sleep_time_subflows},
    )
    j = downstream_task_j.submit(
        a.state.result(), c.state.result(), sim_failure.downstream_task_j
    )
    k = downstream_task_k.submit(b.state.result())
    time.sleep(sleep_time_subflows)

    return {"j": j, "k": k}


if __name__ == "__main__":
    sub_deployments(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=False, downstream_task_j=False
        ),
        sleep_time_subflows=8,
    )
