from prefect import flow
from prefect_aws.s3 import S3Bucket
from tasks_subflows_models.flow_params import SimulatedFailure
from tasks_subflows_models.child_flows_async import ( # must import from child_flows_async since this flow is async
    child_flow_a,
    child_flow_b,
    child_flow_c,
)
from tasks_subflows_models.tasks_async import ( # must import from tasks_async since tasks are awaited
    upstream_task_h,
    upstream_task_i,
    mid_subflow_upstream_task_f,
    downstream_task_p,
    downstream_task_j,
    downstream_task_k,
)
import asyncio


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
async def asyncio_gather_sub_flows(
    sim_failure: SimulatedFailure = SimulatedFailure(),
):
    first_round = await asyncio.gather(
        *[upstream_task_h(), upstream_task_i(), child_flow_c()]
    )
    h, i, c = first_round

    # Its better to run this task with the above gather since it, like nodes h, i, and c, has no dependencies,
    # But to illustrate how a task can be run without gather, I've left it here
    f = await mid_subflow_upstream_task_f()

    second_round = await asyncio.gather(
        *[
            child_flow_a(i, sim_failure.child_flow_a),
            child_flow_b(i, sim_failure.child_flow_b),
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
        asyncio_gather_sub_flows(
            sim_failure=SimulatedFailure(
                child_flow_a=False, child_flow_b=False, downstream_task_j=False
            )
        )
    )
