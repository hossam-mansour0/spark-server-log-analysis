import streamlit as st
import pandas as pd
from minio import Minio
from io import BytesIO

MINIO_ENDPOINT = "minio:9000"  
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  
)

st.set_page_config(page_title="Log Analytics Dashboard", layout="wide")

BUCKET = "log-bucket"

import os
os.environ["AWS_ACCESS_KEY_ID"] = MINIO_ACCESS_KEY
os.environ["AWS_SECRET_ACCESS_KEY"] = MINIO_SECRET_KEY
BUCKET = "log-bucket"

def read_all_csv_from_path(bucket, prefix):

    objects = client.list_objects(bucket, prefix=prefix, recursive=True)
    dfs = []
    for obj in objects:
        if obj.object_name.endswith('.csv'):
            response = client.get_object(bucket, obj.object_name)
            df = pd.read_csv(BytesIO(response.read()), header=None)
            dfs.append(df)
            response.close()
            response.release_conn()
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()  

df_requests = read_all_csv_from_path(BUCKET, "analytics/requests_over_time/")
df_status = read_all_csv_from_path(BUCKET, "analytics/status_distribution/")
df_endpoints = read_all_csv_from_path(BUCKET, "analytics/top_endpoints/")
# -------- UI Layout ----------
st.title("📊 Log Analytics Dashboard")

st.header("📈 Requests Over Time")

if not df_requests.empty:
    df_requests.columns = ["timestamp", "requests"]
    df_requests["timestamp"] = pd.to_datetime(df_requests["timestamp"])
    
    st.line_chart(df_requests.set_index(df_requests.columns[0]))
else:
    st.warning("No data found for requests over time.")

st.header("📊 HTTP Status Code Distribution")

if not df_status.empty:
    df_status.columns = ["status code", "count"]
    st.bar_chart(df_status.set_index(df_status.columns[0]))
else:
    st.warning("No data found for status distribution.")

st.header("🔥 Top Endpoints")
if not df_endpoints.empty:
    df_endpoints.columns = ["endpoint", "count"]
    st.dataframe(df_endpoints)
else:
    st.warning("No data found for top endpoints.")