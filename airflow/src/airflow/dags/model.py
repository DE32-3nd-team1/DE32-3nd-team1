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
import json


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
    schedule_interval='*/1 * * * *',
    max_active_runs=1,
    max_active_tasks=1,
    #schedule_interval='0 0 * * * ',
    start_date=datetime.now(),  # 현재 시간으로 시작
    catchup=False,  # catchup을 비활성화하여 백필 방지
    #start_date=datetime(2024, 10, 9),
    #catchup=True,
    tags=['receipt'],
) as dag:

    mariadb_hook = MySqlHook(mysql_conn_id='my_mariadb_conn')
    connection = mariadb_hook.get_conn()

    def fetch_data_from_mariadb(**kwargs):
        # 설정한 연결 ID를 사용하여 MySQL Hook 생
        #mariadb_hook = MySqlHook(mysql_conn_id='my_mariadb_conn')
        #connection = mariadb_hook.get_conn()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM model WHERE predict_bool = 0 ORDER BY id LIMIT 1;")  # 쿼리 실행
        records = cursor.fetchall()

        # LIMIT 사용 안 할때 주석 제거하기
        #for record in records:
        #    print(record)  # 데이터를 출력하거나 원하는 처리를 수행

        cursor.close()
        #connection.close()

       # 만약 조회된 데이터가 없을 경우 예외 처리
        if not records:
            raise ValueError("No data found in the database.")

        return records

    # LIMIT 사용 안 할때 주석 제거하기
    #def get_path(ti):
        #records = ti.xcom_pull(task_ids='fetch_data')

        #for r in records:
        #    print(r[4])
            #donut(r[4])

    def donut(img_path):
        # LIMIT 사용하면 주석 달기
        print(f"************************ {type(img_path)}")
        print(f"************************ {img_path[2:-3]}")
        print(f"************************ {img_path[2:-3].split(',')[4][2:-1]}")
        print(f"************************ {img_path[2:-3].split(',')[0]}")

        path = img_path[2:-3].split(',')[4][2:-1]
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

        model_id = img_path[2:-3].split(',')[0]
        print(model_id)
        data = json.dumps(result, indent = 4 ,ensure_ascii=False)

        return model_id, data



    def goods(model_id, data):
        model_id = int(model_id)
        data_json = json.loads(data)
        print(data_json)
        print(f"****************************** {type(data_json)}")
        cursor = connection.cursor()

        try:
            if 'menu' in data_json:
                items = data_json['menu']
            else:
                items = data_json


            for d in items:
                print(f"==================== {type(d)}")
                print(d)
                name = d['nm']
                cnt = int(d['cnt'])
                won = int(d['price'].replace(',', ''))  # 쉼표 제거 후 숫자로 처리
                cursor.execute(
                    "INSERT INTO goods (model_id, name, cnt, won) VALUES (%s, %s, %s, %s)",
                    (model_id, name, cnt, won)
                )

            # model 테이블 업데이트
            cursor.execute(
                "UPDATE model SET predict_bool = 1 WHERE id = %s",
                (model_id,)
            )

            # 트랜잭션 커밋
            connection.commit()

        except Exception as e:
            # 오류 발생 시 롤백
            connection.rollback()
            print(f"Error occurred: {e}")

        finally:
            # 커서와 커넥션 안전하게 닫기
            cursor.close()
            connection.close()

    # MariaDB 연결
    create_connection_task = PythonOperator(
        task_id='create_mariadb_connection',
        python_callable=create_mariadb_connection,
    )


    # DB 읽기(이미지 경로, 시간)
    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data_from_mariadb,
    )

    # 모델적용
    donut_task = PythonOperator(
        task_id='donut',
        python_callable=donut,
        op_args=["{{ ti.xcom_pull(task_ids='fetch_data') }}"],
    )

    goods_task = PythonOperator(
        task_id='to.goods',
        python_callable=goods,
        op_args=["{{ ti.xcom_pull(task_ids='donut')[0] }}",
                 "{{ ti.xcom_pull(task_ids='donut')[1] }}"],
    )

    # EmptyOperator로 시작과 끝 설정
    task_start = EmptyOperator(task_id='start')
    task_end = EmptyOperator(task_id='end', trigger_rule="all_done")

    # 작업 순서 설정
    task_start >> create_connection_task >> fetch_data_task  >> donut_task >> goods_task >>  task_end
