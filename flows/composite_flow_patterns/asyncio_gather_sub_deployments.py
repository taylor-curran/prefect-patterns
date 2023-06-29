from prefect import flow
from prefect.utilities.annotations import quote
import time
from prefect_aws.s3 import S3Bucket
from tasks_subflows_models.flow_params import SimulatedFailure
from tasks_subflows_models.tasks_async import (  # must import from tasks_async since tasks are awaited
    upstream_task_h,
    upstream_task_i,
    mid_subflow_upstream_task_f,
    downstream_task_p,
    downstream_task_j,
    downstream_task_k,
)
import asyncio
from prefect.deployments import run_deployment

# TODO This flow is not working, gather it seems is unable to unpack the results of the subflows


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def asyncio_gather_sub_flows(
    sim_failure: SimulatedFailure = SimulatedFailure(), sleep_time_subflows: int = 0
):
    first_round = await asyncio.gather(
        *[
            upstream_task_h(),
            upstream_task_i(),
            run_deployment(
                name="child-flow-c/c-local-docker",
                parameters={"sleep_time": sleep_time_subflows},
            ),
        ]
    )
    h, i, c = first_round

    # Its better to run this task with the above gather since it, like nodes h, i, and c, has no dependencies,
    # But to illustrate how a task can be run without gather, I've left it here
    f = await mid_subflow_upstream_task_f()

    second_round = await asyncio.gather(
        *[
            run_deployment(
                "child-flow-a/a-local-docker",
                parameters={
                    "i": i,
                    "sim_failure_child_flow_a": sim_failure.child_flow_a,
                    "sleep_time": sleep_time_subflows,
                },
            ),
            run_deployment(
                name="child-flow-b/b-local-docker",
                parameters={
                    "sim_failure_child_flow_b": sim_failure.child_flow_b,
                    "sleep_time": sleep_time_subflows,
                },
            ),  # I don't believe fire and forget is possible with asyncio since the result is unpacked
            downstream_task_p(h),
        ]
    )

    a, b, p = second_round

    third_round = await asyncio.gather(
        *[downstream_task_j(a, c, sim_failure.downstream_task_j), downstream_task_k(b)]
    )

    j, k = third_round
    time.sleep(sleep_time_subflows)

    return {"j": j, "k": k}


# ---

if __name__ == "__main__":
    asyncio.run(
        asyncio_gather_sub_flows(
            sim_failure=SimulatedFailure(
                child_flow_a=False, child_flow_b=False, downstream_task_j=False
            ),
            sleep_time_subflows=0,
        )
    )
