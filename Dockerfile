FROM debian:buster-slim

RUN apt update 
    && apt upgrade -y \
    && apt install -y curl python3-pip \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    && mkdir /app \
    && cd /app

WORKDIR /app

COPY ./app .

RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/bin/python3 app.py"]