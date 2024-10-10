FROM apache/airflow:2.6.1

COPY src/airflow/dags/model.py /opt/airflow/dags/model.py
COPY src/airflow/dags/amount.py /opt/airflow/dags/amount.py
COPY src/airflow/dags/pyspark_receipt.py /opt/airflow/dags/pyspark_receipt.py

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER root

RUN apt-get update \
  && apt-get -y install wget ssh curl openjdk-11-jdk python3-pip \
  && apt-get install -y --no-install-recommends \
        vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# airflow 사용자로 변경하여 pip 패키지 설치
#USER airflow

## SPARK
# Spark 다운로드 및 설치
RUN wget https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz \
  && tar -zxvf spark-3.5.1-bin-hadoop3.tgz -C /opt/airflow/ \
  && rm spark-3.5.1-bin-hadoop3.tgz

# 환경 변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_HOME=/opt/airflow/spark-3.5.1-bin-hadoop3
ENV PYSPARK_PYTHON=/usr/bin/python3
ENV PATH="$PATH:/opt/airflow/spark-3.5.1-bin-hadoop3/sbin"
ENV SPARK_NO_DAEMONIZE=true

# DAG 파일 복사
#COPY ./dags/pyspark_receipt.py ./dags/pyspark_receipt.py
#COPY ./py/amount.py ./py/amount.py
#COPY requirements.txt requirements.txt

# Spark 관련 디렉토리 생성 및 권한 부여
RUN mkdir -p /opt/airflow/spark-3.5.1-bin-hadoop3/logs /opt/airflow/spark-3.5.1-bin-hadoop3/work /dags /logs \
  && chown -R "${AIRFLOW_UID:-50000}:0" /opt/airflow /dags /logs \
  && chmod -R 755 /opt/airflow /dags /logs \
  && chmod -R 755 /opt/airflow/spark-3.5.1-bin-hadoop3/logs /opt/airflow/spark-3.5.1-bin-hadoop3/work



USER "${AIRFLOW_UID:-50000}:0"
