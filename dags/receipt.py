from datetime import datetime, timedelta
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonVirtualenvOperator

with DAG(
    'receipt',
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=1)
    },
    description='hello world DAG',
    schedule_interval='0 0 * * *', 
    start_date=datetime(2024, 10, 3),
    #end_date=datetime(2024,10,27),

    catchup=True,
    tags=['receipt'],
) as dag:
    
    def test():
        print("*"*3000)


    test = PythonVirtualenvOperator(
            task_id="test",
            python_callable=test,
            system_site_packages=False,
            trigger_rule='all_done'
            )
    


    task_start = EmptyOperator(task_id='start')
    task_end = EmptyOperator(task_id='end', trigger_rule="all_done")

    task_start >> test >> task_end
