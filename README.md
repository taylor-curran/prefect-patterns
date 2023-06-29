# prefect-patterns

## How to Run Example Flows from this Repo

### Fork or Clone this Repository
Run the following commands from the root level of your repository.

### Create Virtual Environment
```bash
conda create --name prfp python=3.9
```
```bash
conda activate prfp
```

### Install Dependencies

```bash
pip install -U prefect 
pip install prefect-aws prefect-docker prefect-github
```

### Authenticate to Prefect Cloud and Set Workspace
```bash
prefect cloud login
prefect cloud workspace set
```

### Create Blocks
```bash
python utilities/blocks.py
```

### Create Deployments
```bash
prefect deploy --all
```



