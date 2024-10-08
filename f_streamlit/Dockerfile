# 베이스 이미지 선택
FROM python:3.11.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY src/f_streamlit/ /app/

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

CMD  ["streamlit", "run", "user_page.py"]
