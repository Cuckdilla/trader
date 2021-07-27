FROM python:3.9.6-buster

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/usr/bin/python3 app.py"]