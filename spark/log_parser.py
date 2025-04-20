from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract, col
import sys

# Create Spark Session
spark = SparkSession.builder \
    .appName("Log Parser") \
    .getOrCreate()

# ------------------------------
# Regex Pattern for Nginx Logs
# Example log line:
# 127.0.0.1 - - [10/Oct/2020:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326

LOG_PATTERN = r'^(\S+) - - \[(.*?)\] "(.*?)" (\d{3}) (\d+)'

# ------------------------------
# Read raw logs from MinIO (s3a://)
input_path = "s3a://log-bucket/raw-logs/"
output_path = "s3a://log-bucket/parsed-logs/"

df_raw = spark.read.text(input_path)

# Extract relevant fields using regex
df_parsed = df_raw.select(
    regexp_extract('value', LOG_PATTERN, 1).alias('ip'),
    regexp_extract('value', LOG_PATTERN, 2).alias('timestamp'),
    regexp_extract('value', LOG_PATTERN, 3).alias('request'),
    regexp_extract('value', LOG_PATTERN, 4).alias('status'),
    regexp_extract('value', LOG_PATTERN, 5).alias('size')
)

# Filter out malformed lines (rows where IP or status is missing)
df_clean = df_parsed.filter((col("ip") != "") & (col("status") != ""))

# Optional: Extract method and endpoint from request
df_final = df_clean.withColumn("method", regexp_extract("request", r"^(\S+)", 1)) \
                   .withColumn("endpoint", regexp_extract("request", r"^\S+ (\S+)", 1)) \
                   .drop("request")

# Write to Parquet, partitioned by status
df_final.write.mode("overwrite").partitionBy("status").parquet(output_path)

print("✅ Log parsing and saving to Parquet completed.")

spark.stop()
