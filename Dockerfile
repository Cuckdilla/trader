FROM debian:buster-slim

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/usr/bin/python3 app.py"]