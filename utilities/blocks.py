from prefect_aws import AwsCredentials
from prefect_aws.s3 import S3Bucket
from prefect.blocks.notifications import SlackWebhook

from dotenv import load_dotenv
import os
import time

# -- env vars --
load_dotenv()
aws_staging_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_staging_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

# -- aws --

aws_creds = AwsCredentials(
    aws_access_key_id=aws_staging_access_key_id,
    aws_secret_access_key=aws_staging_secret_access_key,
)

aws_creds.save("my-aws-creds", overwrite=True)

time.sleep(10)

s3_bucket_result_storage = S3Bucket(
    bucket_name="se-demo-result-storage",
    aws_credentials=AwsCredentials.load("my-aws-creds"),
)
s3_bucket_result_storage.save("result-storage", overwrite=True)

print("Blocks Updated!")
