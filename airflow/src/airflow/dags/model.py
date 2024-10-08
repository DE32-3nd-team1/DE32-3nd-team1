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
import torch
from PIL import Image
import re
from transformers import DonutProcessor, VisionEncoderDecoderModel


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
    schedule_interval='*/3 * * * *',
    start_date=datetime(2024, 10, 7),
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

    

    def donut(path):
        processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
        model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")

        # 이미지 불러오기
        image = Image.open(path).convert('RGB')
        pixel_values = processor(image, return_tensors="pt").pixel_values

        task_prompt = "<s_cord-v2>"
        decoder_input_ids = processor.tokenizer(
            task_prompt,
            add_special_tokens=False,
            return_tensors="pt").input_ids

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        outputs = model.generate(
            pixel_values.to(device),
            decoder_input_ids = decoder_input_ids.to(device),
            max_length = model.decoder.config.max_position_embeddings,
            early_stopping=True,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        sequence = processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token

        # 결과 뽑기
        import json

        result = processor.token2json(sequence)
        print("*"*1000)
        print(json.dumps(result, indent = 4 ,ensure_ascii=False))

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
        op_args=['/opt/airflow/dags/test.png'],
    )

    # EmptyOperator로 시작과 끝 설정
    task_start = EmptyOperator(task_id='start')
    task_end = EmptyOperator(task_id='end', trigger_rule="all_done")

    # 작업 순서 설정
    task_start >> create_connection_task >> donut_task >> fetch_data_task  >> task_end

