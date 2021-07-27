FROM python:3.9.6-alpine3.14

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/usr/bin/python3 app.py"]