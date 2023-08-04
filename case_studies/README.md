    sim_failure = SimulatedFailure(
        task_a2=False, 
        task_b1=True, 
        task_t1=False
        )
    sleep_time = 30


To achieve the behavior described in the diagram, add like 60 seconds of sleep time and set task_b1 simulated failure to True.