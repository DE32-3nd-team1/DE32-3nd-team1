# 베이스 이미지
FROM apache/airflow:2.6.1-python3.10

# 필요한 시스템 패키지 설치
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

RUN mkdir -p /opt/airflow/logs \
    && chmod -R 777 /opt/airflow/logs

# airflow user 변경
USER airflow

# 작업 디렉토리 생성
WORKDIR /opt/airflow

# 필요한 파일 복사
COPY receipt.py /opt/airflow/dags

# 환경변수 설정
ENV AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags

# uvicorn을 사용하여 FastAPI 애플리케이션 실행 (포트 8000)

CMD ["airflow", "webserver", "--host", "0.0.0.0", "--port", "8080"]
