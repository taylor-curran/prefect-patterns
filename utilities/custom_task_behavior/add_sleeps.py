import time
import functools
from prefect import Task, Flow
from contextvars import ContextVar

_SLEEP_TIME = ContextVar("sleep_time", default=0)


def task(__fn=None, **kwargs):
    if __fn:
        return CustomTask(fn=my_task_wrapper(__fn), **kwargs)
    else:
        return functools.partial(task, **kwargs)


class CustomTask(Task):
    def run(self, *args, **kwargs):
        time.sleep(_SLEEP_TIME.get())
        return super().run(*args, **kwargs)


def my_task_wrapper(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        sleep_time = kwargs.pop("sleep_time", _SLEEP_TIME.get())
        time.sleep(sleep_time)
        return fn(*args, **kwargs)

    return wrapper


class CustomFlow(Flow):
    def __call__(self, *args, **kwargs):
        sleep_time = kwargs.pop("sleep_time", 0)
        token = _SLEEP_TIME.set(sleep_time)
        try:
            retval = super().__call__(*args, **kwargs)
        finally:
            _SLEEP_TIME.reset(token)

        return retval


def flow(__fn=None, **kwargs):
    if __fn:
        return CustomFlow(fn=__fn, **kwargs)
    else:
        return functools.partial(flow, **kwargs)


if __name__ == "__main__":

    @task
    def foo():
        print("foo")

    @task
    def bar():
        print("bar")

    @flow
    def my_flow():
        foo()
        bar()

    my_flow(sleep_time=8)
