FROM apache/airflow:2.6.1
USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY src/airaflow/dags /opt/airflow/dags/
# airflow 사용자로 변경하여 pip 패키지 설치
USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER "${AIRFLOW_UID:-50000}:0"
