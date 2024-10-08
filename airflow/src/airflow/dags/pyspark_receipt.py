from datetime import datetime, timedelta
from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from airflow.operators.python import PythonOperator, PythonVirtualenvOperator, BranchPythonOperator

with DAG(
        'spark',
        default_args={
        'depends_on_past': True,
        'retries': 1,
        'retry_delay': timedelta(seconds=3)
    }),
    description='spark statistics',
    schedule_interval=timedelta(minutes=3),
    start_date=datetime(2024, 10, 7),
    schedule_interval = '*/3 * * * *',
    catchup=True,
    tags=['spark']
) as dag:

    task_spark = BashOperator(
            task_id = 'task_spark',
            bash_command='''
            $SPARK_HOME/bin/spark-submit --conf "spark.pyspark.driver.python=/usr/local/bin/python3" --conf "spark.pyspark.python=/usr/local/bin/python3" /opt/airflow/dags/amount.py
            '''
            )

    task_start = EmptyOperator(task_id='task_start', trigger_rule='all_done')
    task_end = EmptyOperator(task_id='task_end')

    task_start >> task_spark >> task_end
