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

### Set Up AWS Creds and S3 Bucket
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
### Create Local Docker Work Pool
```bash
prefect work-pool create local-docker --type docker
```

### Reconfigure Build and Pull Steps where Necessary
In the `prefect.yaml` file:
#### 1. **Build Step:** should point to your image registry.
```yaml
build:
- prefect_docker.deployments.steps.build_docker_image:
    requires: prefect-docker>=0.3.0
    image_name: taycurran/test-projects-june11 # CHANGE HERE
    tag: '{{ get-commit-hash.stdout }}'
    dockerfile: auto
    push: true
```
#### 2. **Pull Step:** If you forked this repo, point to your github URL.
```yaml
pull:
- prefect.deployments.steps.git_clone:
    repository: https://github.com/taylor-curran/prefect-patterns.git # CHANGE HERE
    branch: main
```

### Create Deployments
```bash
prefect deploy --all
```
