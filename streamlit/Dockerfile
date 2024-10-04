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

#RUN pip install --no-cache-dir --upgrade git+https://github.com/lsiwh37249/stdash.git@0.3.0/bashboard

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

EXPOSE 8501

#HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD  ["streamlit", "run", "app.py"]
