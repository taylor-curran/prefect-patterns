from prefect import flow, task
from prefect_aws.s3 import S3Bucket
import time

# If a team will be using only Prefect's TaskRunners for their Concurrent/Asynchronous Execution, they can define their tasks like below.
# In other words, if a team does not intend to run any subflows or tasks as awaitable coroutines, they should leave their tasks as normal sync functions.

# -- Child Flow Tasks --


@task
def task_l():
    print("task f")
    return {"l": "task l"}


@task
def task_m():
    print("task m")
    return {"m": "task m"}


@task
def task_n(m):
    print(m)
    print("task n")
    return {"n": "task n"}


@task
def task_o():
    print("task o")
    return {"o": "task o"}


# -- Child Flows --


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
def child_flow_a(i, sim_failure_child_flow_a, sleep_time=0):
    print(f"i: {i}")
    m = task_m.submit()
    time.sleep(sleep_time)
    o = task_o.submit()
    if sim_failure_child_flow_a:
        raise Exception("This is a test exception")
    else:
        return {"a": "child flow a"}


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
def child_flow_b(
    i={"i": "upstream task"}, sim_failure_child_flow_b=False, sleep_time=0
):
    print(f"i: {i}")
    l = task_l.submit()
    if sim_failure_child_flow_b:
        raise Exception("This is a test exception")
    else:
        o = task_o.submit()
        time.sleep(sleep_time)
        return {"b": "child flow b"}


@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
def child_flow_d(sleep_time=0):
    l = task_l.submit()
    time.sleep(sleep_time)
    o = task_o.submit()
    return {"d": "child flow d"}


# -- Nested Child Flow --
@flow(persist_result=True, result_storage=S3Bucket.load("result-storage"))
def child_flow_c(sleep_time=0):
    d = child_flow_d(sleep_time=sleep_time)
    m = task_m.submit()
    n = task_n.submit(m)
    time.sleep(sleep_time)
