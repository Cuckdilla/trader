FROM ubuntu:21.04

RUN apt-get update 
    && apt-get upgrade -y \
    && apt-get install -y curl python3-pip \
    && mkdir /app

WORKDIR /app

COPY ./app .

RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/bin/python3 app.py"]