# app/Dockerfile

FROM python:3.11.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY src/streamlit/app.py /app/

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

EXPOSE 8501

CMD  ["streamlit", "run", "app.py"]
