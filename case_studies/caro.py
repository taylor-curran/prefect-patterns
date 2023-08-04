from prefect import task, flow

@task
def owned_fn(barbies):
    print(f"I have {barbies} number of barbies")

    return barbies

@task
def buy_barbies(owned, new):
    print(f"Now I have {owned + new} number of barbies")

    return owned + new

@flow
def caro(owned, buying):
    owned = owned_fn(owned)
    buy_barbies(owned, buying)



caro(0, 5)