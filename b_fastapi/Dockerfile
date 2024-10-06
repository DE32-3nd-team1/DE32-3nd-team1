FROM python:3.11

WORKDIR /code

RUN apt update
RUN pip install --no-cache-dir uvicorn
RUN pip install --no-cache-dir fastapi
RUN pip install --no-cache-dir --upgrade pip
COPY src/b_fastapi/main.py /code
#COPY run.sh /code/run.sh

#RUN pip install --no-cache-dir --upgrade git+https://github.com/DE32-3nd-team1/DE32-3nd-team1.git@fastapi

COPY requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
