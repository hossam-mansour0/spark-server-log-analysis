from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='log_etl_dag',
    default_args=default_args,
    description='ETL log data with Spark and update dashboard',
    schedule_interval=None,
    catchup=False
) as dag:

    ingest_logs_to_minio = BashOperator(
        task_id='ingest_logs_to_minio',
        bash_command="""
        mc alias set localminio http://minio:9000 minioadmin minioadmin &&
        mc mb localminio/log-bucket &&
        mc cp /opt/airflow/logs/access.log localminio/log-bucket/raw-logs/access.log
        """,
    )

    run_log_parser = SparkSubmitOperator(
        task_id='run_log_parser',
        application='/opt/bitnami/spark/work/log_parser.py',
        conn_id='spark_default',
        conf={
            'spark.hadoop.fs.s3a.endpoint': 'http://minio:9000',
            'spark.hadoop.fs.s3a.access.key': 'minioadmin',
            'spark.hadoop.fs.s3a.secret.key': 'minioadmin',
            'spark.hadoop.fs.s3a.path.style.access': 'true',
        },
        verbose=True
    )

    run_log_analytics = SparkSubmitOperator(
        task_id='run_log_analytics',
        application='/opt/bitnami/spark/work/log_analytics.py',
        conn_id='spark_default',
        conf={
            'spark.hadoop.fs.s3a.endpoint': 'http://minio:9000',
            'spark.hadoop.fs.s3a.access.key': 'minioadmin',
            'spark.hadoop.fs.s3a.secret.key': 'minioadmin',
            'spark.hadoop.fs.s3a.path.style.access': 'true',
        },
        verbose=True
    )

    refresh_dashboard = BashOperator(
        task_id='refresh_dashboard',
        bash_command='touch /opt/airflow/streamlit_dashboard/refresh.txt'
     
    )

    # Dependencies
    ingest_logs_to_minio >> run_log_parser >> run_log_analytics >> refresh_dashboard
