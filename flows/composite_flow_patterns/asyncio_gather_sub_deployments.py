from prefect import flow
from prefect_aws.s3 import S3Bucket
from tasks_subflows_models.flow_params import SimulatedFailure
from tasks_subflows_models.tasks_async import ( # must import from tasks_async since tasks are awaited
    upstream_task_h,
    upstream_task_i,
    mid_subflow_upstream_task_f,
    downstream_task_p,
    downstream_task_j,
    downstream_task_k,
)
import asyncio
from prefect.deployments import run_deployment


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def asyncio_gather_sub_deployments(
    sim_failure: SimulatedFailure = SimulatedFailure(),
):
    first_round = await asyncio.gather(
        *[upstream_task_h(), upstream_task_i(), run_deployment(name="child-flow-c/dep-child-c")]
    )
    h, i, c = first_round

    # Its better to run this task with the above gather since it, like nodes h, i, and c, has no dependencies,
    # But to illustrate how a task can be run without gather, I've left it here
    f = await mid_subflow_upstream_task_f()

    second_round = await asyncio.gather(
        *[
            run_deployment(
                "child-flow-a/dep-child-a",
                parameters={
                    "i": i,
                    "sim_failure_child_flow_a": sim_failure.child_flow_a,
                },
            ),
            run_deployment(
                name="child-flow-b/dep-child-b",
                parameters={
                    "i": i,
                    "sim_failure_child_flow_b": sim_failure.child_flow_b,
                },
            ),
            downstream_task_p(h),
        ]
    )

    a, b, p = second_round

    third_round = await asyncio.gather(
        *[downstream_task_j(a, c, sim_failure.downstream_task_j), downstream_task_k(b)]
    )

    j, k = third_round

    return {"j": j, "k": k}


# ---

if __name__ == "__main__":
    asyncio.run(
        asyncio_gather_sub_deployments(
            sim_failure=SimulatedFailure(
                child_flow_a=False, child_flow_b=False, downstream_task_j=False
            )
        )
    )