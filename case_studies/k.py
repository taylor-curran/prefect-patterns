from prefect import flow, task
import asyncio
import time

@flow
async def child_flow_a(data_source, sleep=4):
    time.sleep(sleep / 2)
    print(f"Processing {data_source}!")


@flow
async def child_flow_b(sleep):
    time.sleep(sleep)
    print("This is child flow B!")


@flow
async def child_flow_c(simulate_failure=False, sleep=4):
    if sleep > 0:
        time.sleep(sleep / 4)
    if simulate_failure:
        raise ValueError("simulated failure of task b1")
    else:
        time.sleep(2)
        print("This is child flow C!")


@task
async def task_b(sleep=2):
    if sleep > 0:
        time.sleep(sleep / 2)
    print("This is task B!")


@flow
async def coros_parent_flow(data_sources: list, simulate_failure_c: bool = False, sleep: int = 4):
    # -- Map-Like Concurrent Execution --

    coros = [child_flow_a(data_source, sleep=sleep) for data_source in data_sources]

    first_round = await asyncio.gather(*coros)

    # -- Regular Concurrent Execution --

    second_round = await asyncio.gather(
        *[child_flow_b(sleep=sleep), task_b(sleep=sleep), child_flow_c(simulate_failure=simulate_failure_c, sleep=sleep)]
    )

    return {"first_round": first_round, "second_round": second_round}


if __name__ == "__main__":
    asyncio.run(
        coros_parent_flow(
            data_sources=["data_source_1", "data_source_2"], simulate_failure_c=True, sleep=10
        )
    )
