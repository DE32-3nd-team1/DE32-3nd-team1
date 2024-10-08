from datetime import datetime, timedelta
from airflow.models import Connection
from airflow.utils.db import provide_session
from sqlalchemy.exc import IntegrityError
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import PythonVirtualenvOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from donut import DonutModel
from PIL import Image
import torch

# MariaDB 연결을 생성하는 함수 정의
@provide_session
def create_mariadb_connection(session=None):
    try:
        # MariaDB 연결 객체 생성
        conn = Connection(
            conn_id='my_mariadb_conn',  # 연결 ID
            conn_type='mysql',           # 데이터베이스 유형 - 'mysql'로 설정
            host='172.17.0.1',           # 데이터베이스 서버 주소
            schema='team1',            # 스키마 또는 데이터베이스 이름
            login='team1',               # 사용자 이름
            password='1234',             # 비밀번호
            port=53306                   # 포트 (MariaDB 기본 포트: 3306)
        )

        # SQLAlchemy 세션을 사용하여 연결을 추가
        if not session.query(Connection).filter(Connection.conn_id == conn.conn_id).first():
            session.add(conn)
            session.commit()
            print(f"Connection {conn.conn_id} created successfully.")
        else:
            print(f"Connection {conn.conn_id} already exists.")
    except IntegrityError:
        print(f"Connection {conn.conn_id} already exists.")
    except Exception as e:
        print(f"Failed to create connection {conn.conn_id}: {e}")

with DAG(
    'receipt',
    default_args={
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=1)
    },
    description='hello world DAG',
    schedule_interval='@daily',
    start_date=datetime(2024, 10, 1),
    catchup=True,
    tags=['receipt'],
) as dag:

    def fetch_data_from_mariadb(**kwargs):
        # 설정한 연결 ID를 사용하여 MySQL Hook 생성
        mariadb_hook = MySqlHook(mysql_conn_id='my_mariadb_conn')
        connection = mariadb_hook.get_conn()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM receipt LIMIT 10;")  # 쿼리 실행
        records = cursor.fetchall()
        for record in records:
            print(record)  # 데이터를 출력하거나 원하는 처리를 수행

    model = DonutModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")

    def donut():

        if torch.cuda.is_available():
            model.half()
            device = torch.device("cuda")
            model.to(device)
        else:
            device = torch.device("cpu")
            model.encoder.to(torch.float)
            model.to(device)

        model.eval() 

    def process(path):
        image = Image.open(path).convert("RGB")
        output = model.inference(image=image, prompt="<s_cord-v2>")

        return output


    # MariaDB 연결
    create_connection_task = PythonOperator(
        task_id='create_mariadb_connection',
        python_callable=create_mariadb_connection,
    )


    # DB 읽기(이미지 경로, 시간)
    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data_from_mariadb,
        provide_context=True,
    )

    # 모델적용
    donut_task = PythonOperator(
        task_id='donut',
        python_callable=donut,
        provide_context=True,
    )

    # EmptyOperator로 시작과 끝 설정
    task_start = EmptyOperator(task_id='start')
    task_end = EmptyOperator(task_id='end', trigger_rule="all_done")

    # 작업 순서 설정
    task_start >> create_connection_task >> fetch_data_task >> donut_task >> task_end
