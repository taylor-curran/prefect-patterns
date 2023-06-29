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
pip install prefect-aws prefect-docker prefect-github python-dotenv
```

### Authenticate to Prefect Cloud and Set Workspace
```bash
prefect cloud login
prefect cloud workspace set
```

### Set Up AWS Creds and Blocks
1. Add a `.env` file with the following variables:
    ```bash
    AWS_ACCESS_KEY_ID=add-your-key-id
    AWS_SECRET_ACCESS_KEY=add-your-secret-access-key
    ```
2. Create an S3 Bucket with name `se-demo-result-storage`.
### Create Blocks
```bash
python utilities/blocks.py
```

### Create Deployments
```bash
prefect deploy --all
```

#### Tip!
Remember to push any changes you make to the flow code and/or change the pull step accordingly.
