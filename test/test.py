import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
import boto3
from botocore.exceptions import ClientError

import requests


s3_client = boto3.client('s3')
bucket = "fbrakowski-pricing-analytics"
staging_object = "staging/index.csv"
staging_path = "s3://"+ bucket + "/"+ staging_object
outpath = "s3://"+bucket+"/processed"
url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.csv'

r = requests.get(url)
r.status_code
csv_split = r.text.split("\n")[5:]
csv = "\n".join(csv_split)
f.open("/tmp/index.csv", "w")
f.write(csv)
f.close()
try:
    response = s3_client.upload_file("/tmp/index.csv", bucket, staging_object)
except ClientError as e:
    logging.error(e)
dynamicFrame = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [staging_path ]},
    format="csv",
    format_options={
        "withHeader": True,
        # "optimizePerformance": True,
    },
)
glueContext.write_dynamic_frame.from_options(
    frame=dynamicFrame,
    connection_type="s3",
    format="parquet",
    connection_options={
        "path": outpath,
        "partitionKeys": ["region_code", "Tenancy", "operation", "instance_type", "TermType", "OfferingClass", "LeaseContractLength", "PurchaseOption" ]
    },
    format_options={
        # "useGlueParquetWriter": True,
    },
)
# Delete Staging Area

job.commit()