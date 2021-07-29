FROM python:3.9.6-slim-buster

WORKDIR /app

COPY app/ .

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "app.py"]