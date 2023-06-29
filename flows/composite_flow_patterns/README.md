# Subflows Patterns

- **Sync Subflows**: Simplest Pattern - Subflows execute on the same flow run infrastructure as the parent.
    - They will execute synchronously and will block the execution of any concurrently executing code.
- **Task Wrapped Deployments**: Enable subflows that can leverage features of prefect tasks. 
    -  They will **not** execute on the same infrastructure as the parent since a run_deployment API call is necessary instead of a flow function call as tasks can only execute python, not flow or task functions, from within their logic.
- **Using Asyncio Gather**: This method is very subflow compatible especially if you need your subflows to run on the same parent as the infra, which removes the option of doing task-wrapped deployments. The downside is that the concurrency behavior isn't quite as smart as what the ConcurrentTaskRunner would provide. Gather groups need to be carefully optimized, but the task runner handles this optimization automatically.

In terms of adding task decorator to async functions or to normal functions.

An async task can run just fine in a sync or async fashion, there are just a few gotchas to be aware of:
- A task can only be submitted to the Task Runner if it is either non-async or if the flow function is not async, see blocking_subflows.py or child_flows.py for examples of this.
    - An async task submitted to the task runner of an async flow will not run. 
- An async task can also be awaited from inside of an async flow, see asyncio_gather_subflows.py for an example of this.
- Submitting tasks to the task runner is always preferred because the concurrent execution is dependency aware.

The recommendation is, for teams using asyncio, define your tasks with the async modifier so the task can be called in both async and sync contexts. If concurrent execution is desired, submit to the task runner as much as possible, but use asyncio.gather() where its necessary to achieve concurrent execution with subflows and do not mix `.submit()` and `await` code within the same flow.

prj/lunchlearn/prefect-patterns