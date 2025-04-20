from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("LogAnalyticsJob") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

from pyspark.sql.functions import col, count, to_timestamp, date_trunc

df = spark.read.parquet("s3a://log-bucket/parsed-logs/")

df = df.withColumn("time", to_timestamp("timestamp", "dd/MMM/yyyy:HH:mm:ss Z"))

df_requests_over_time = df.groupBy(date_trunc("hour", "time").alias("hour")).count()


# Status Code Distribution
df_status_dist = df.groupBy("status").count()

df_top_endpoints = df.groupBy("request").count().orderBy(col("count").desc()).limit(10)

df_requests_over_time.write.mode("overwrite").csv("s3a://log-bucket/analytics/requests_over_time")
df_status_dist.write.mode("overwrite").csv("s3a://log-bucket/analytics/status_distribution")
df_top_endpoints.write.mode("overwrite").csv("s3a://log-bucket/analytics/top_endpoints")
