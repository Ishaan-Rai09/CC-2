import json
from urllib.parse import urlparse

import boto3
from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import sys


def parse_s3_uri(uri: str) -> tuple[str, str]:
    parsed = urlparse(uri)
    return parsed.netloc, parsed.path.lstrip("/")


args = getResolvedOptions(
    sys.argv,
    ["input_path", "output_path", "user_id"],
)

spark = SparkSession.builder.appName("SmartNotesAnalyticsGlue").getOrCreate()
s3 = boto3.client("s3")

input_path = args["input_path"]
output_path = args["output_path"]
user_id = args["user_id"]

df = spark.read.json(input_path)

if df.rdd.isEmpty():
    result = {
        "top_subjects": [],
        "monthly_uploads": [],
        "file_type_distribution": [],
        "total_files": 0,
        "user_id": user_id,
    }
else:
    top_subjects = [
        {"subject": row["subject"], "count": row["count"]}
        for row in (
            df.groupBy("subject")
            .agg(F.count("*").alias("count"))
            .orderBy(F.desc("count"))
            .collect()
        )
    ]

    monthly_uploads = [
        {"month": row["month_label"], "count": row["count"]}
        for row in (
            df.groupBy("month_label", "year", "month")
            .agg(F.count("*").alias("count"))
            .orderBy("year", "month")
            .collect()
        )
    ]

    file_type_distribution = [
        {"type": row["file_type"], "count": row["count"]}
        for row in (
            df.groupBy("file_type")
            .agg(F.count("*").alias("count"))
            .orderBy(F.desc("count"))
            .collect()
        )
    ]

    result = {
        "top_subjects": top_subjects,
        "monthly_uploads": monthly_uploads,
        "file_type_distribution": file_type_distribution,
        "total_files": df.count(),
        "user_id": user_id,
    }

bucket, key = parse_s3_uri(output_path)
s3.put_object(
    Bucket=bucket,
    Key=key,
    Body=json.dumps(result).encode("utf-8"),
    ContentType="application/json",
)
