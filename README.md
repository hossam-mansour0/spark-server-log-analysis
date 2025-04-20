# Log Analytics with Apache Spark and Airflow
This project involves building a log analytics pipeline using Apache Spark and orchestrating the tasks with Apache Airflow. The pipeline processes logs from various sources, performs analytics, and visualizes the results. 
This project helps uncover traffic patterns, detect anomalies, and deliver valuable insights for DevOps and business stakeholders.
## Business Goal

**Objective:**  
Analyze web server access logs at scale to identify traffic spikes, error patterns, and popular resources.

**Key Insight:**  
DevOps and business stakeholders can leverage log insights to optimize site performance, detect security issues, and enhance user experience.

## Features
- Log Parsing and Analytics with Spark
- Orchestration with Apache Airflow
- Integration with MinIO for S3-like object storage
- Dashboard for visualization using Streamlit
- Docker-based deployment for all components
## Technologies Used
- **Apache Spark**: For distributed data processing and analytics
- **Apache Airflow**: For orchestrating the data pipeline
- **MinIO**: For S3-compatible object storage
- **Streamlit**: For building a dashboard to visualize log data
- **Docker**: For containerization and environment isolation
## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/log-analytics-spark-airflow.git
   cd log-analytics-spark-airflow
   ```

2. Ensure that Docker is installed on your machine. You can follow the installation guide from Docker's [official website](https://www.docker.com/get-started).

3. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. Once the containers are running, open your browser and access the following services:
   - **Airflow Web UI**: http://localhost:8082
   - **Streamlit Dashboard**: http://localhost:8501

5. To run the pipeline manually through Airflow, trigger the `log_etl_dag` from the Airflow UI.
## Usage

- **Log Parsing**: The pipeline begins by parsing logs from various sources. You can customize the log source and format in the DAG file.
- **Spark Analytics**: The logs are processed and analyzed by Spark, generating useful insights.
- **Airflow DAGs**: Use the Airflow Web UI to monitor and trigger the tasks.
- **Streamlit Dashboard**: Visualize the output of the log analytics in a web dashboard.

