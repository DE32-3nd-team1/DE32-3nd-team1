FROM apache/airflow:2.6.1
USER root

# 필요한 시스템 패키지 설치 (vim, git 등)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim \
        git \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# 기본 Airflow 사용자로 변경
USER airflow
COPY ./src/airflow/model/ ./model/
# pip 패키지 설치
RUN pip install --no-cache-dir --upgrade git+https://github.com/DE32-3nd-team1/DE32-3nd-team1.git@0.2.0/airflow
