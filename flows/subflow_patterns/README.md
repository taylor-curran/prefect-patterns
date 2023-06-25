# Subflows Patterns

- **Sync Subflows**: Simplest Pattern - Subflows execute on the same flow run infrastructure as the parent.
    - They will execute synchronously and will block the execution of any concurrently executing code.
- **Task Wrapped Deployments**: Enable subflows that can leverage features of prefect tasks. 
    -  They will *not* execute on the same infrastructure as the parent since a run_deployment API call is necessary instead of a flow function call as tasks can only execute python, not flow or task functions, from within their logic.