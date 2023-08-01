import asyncio
from prefect import flow


@flow
async def print_item(item):
    print(item)
    return item


@flow(log_prints=True)
async def parent(items: list):
    first_round = await asyncio.gather(*[print_item(item) for item in items])

    return first_round


if __name__ == "__main__":
    asyncio.run(parent(items=["foo", 42, None]))

# == ["foo", 42, None]
