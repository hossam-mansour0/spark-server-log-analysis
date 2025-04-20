# from pyspark.sql import SparkSession
# from pyspark.sql.functions import regexp_extract, col
# import sys


# spark = SparkSession.builder \
#     .appName("ReadLogFromMinIO") \
#     .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
#     .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
#     .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
#     .config("spark.hadoop.fs.s3a.path.style.access", "true") \
#     .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
#     .getOrCreate()

# # ------------------------------

# LOG_PATTERN = r'^(\S+) - - \[(.*?)\] "(.*?)" (\d{3}) (\d+)'

# # ------------------------------
# # Read raw logs from MinIO (s3a://)
# input_path = "s3a://log-bucket/raw-logs/access.log"
# output_path = "s3a://log-bucket/parsed-logs/"

# df_raw = spark.read.text(input_path)

# # Extract relevant fields using regex
# df_parsed = df_raw.select(
#     regexp_extract('value', LOG_PATTERN, 1).alias('ip'),
#     regexp_extract('value', LOG_PATTERN, 2).alias('timestamp'),
#     regexp_extract('value', LOG_PATTERN, 3).alias('request'),
#     regexp_extract('value', LOG_PATTERN, 4).alias('status'),
#     regexp_extract('value', LOG_PATTERN, 5).alias('size')
# )

# # Filter out malformed lines (rows where IP or status is missing)
# df_clean = df_parsed.filter((col("ip") != "") & (col("status") != ""))

# # Optional: Extract method and endpoint from request
# df_final = df_clean.withColumn("method", regexp_extract("request", r"^(\S+)", 1)) \
#                    .withColumn("endpoint", regexp_extract("request", r"^\S+ (\S+)", 1)) \
#                    .drop("request")

# # Write to Parquet, partitioned by status
# df_final.write.mode("overwrite").partitionBy("status").parquet(output_path)

# print("✅ Log parsing and saving to Parquet completed.")

# spark.stop()
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract, col, length
import sys

# Initialize Spark session
spark = SparkSession.builder \
    .appName("ReadLogFromMinIO") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# ------------------------------
# Apache Combined Log Format regex
LOG_PATTERN = r'^(\S+) - - \[([^\]]+)\] "(\S+) (\S+)[^"]*" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"'

# ------------------------------
# Paths
input_path = "s3a://log-bucket/raw-logs/access.log"
output_path = "s3a://log-bucket/parsed-logs/"

df_raw = spark.read.text(input_path)

# Parse logs with regex
df_parsed = df_raw.select(
    regexp_extract('value', LOG_PATTERN, 1).alias('ip'),
    regexp_extract('value', LOG_PATTERN, 2).alias('timestamp'),
    regexp_extract('value', LOG_PATTERN, 3).alias('method'),
    regexp_extract('value', LOG_PATTERN, 4).alias('request'),
    regexp_extract('value', LOG_PATTERN, 5).alias('status'),
    regexp_extract('value', LOG_PATTERN, 6).alias('size'),
    regexp_extract('value', LOG_PATTERN, 7).alias('referer'),
    regexp_extract('value', LOG_PATTERN, 8).alias('user_agent')
)

# Filter out malformed rows (missing ip, request, or status)
df_clean = df_parsed.filter(
    (col("ip") != "") &
    (col("request") != "") &
    (col("status") != "") &
    (col("method") != "")
)

# Remove outliers in size (e.g., > 10MB) or if size is not a number
df_filtered = df_clean.filter(
    (col("size").rlike("^\d+$")) & (col("size").cast("long") < 10 * 1024 * 1024)
)

# Write to Parquet partitioned by status
df_filtered.write.mode("overwrite").partitionBy("status").parquet(output_path)

print("Log parsing and saving to Parquet completed.")
spark.stop()
