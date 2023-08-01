from prefect import flow, task
import asyncio


@flow
async def child_flow_a(data_source):
    print(f"Processing {data_source}!")


@flow
async def child_flow_b():
    print("This is child flow B!")


@task
async def task_b():
    print("This is task B!")


@flow
async def parent_flow(data_sources):
    # -- Map-Like Concurrent Execution --

    coros = [child_flow_a(data_source) for data_source in data_sources]

    first_round = await asyncio.gather(*coros)

    # -- Regular Concurrent Execution --

    second_round = await asyncio.gather(*[child_flow_b(), task_b()])

    return {"first_round": first_round, "second_round": second_round}


if __name__ == "__main__":
    asyncio.run(parent_flow(data_sources=["data_source_1", "data_source_2"]))
