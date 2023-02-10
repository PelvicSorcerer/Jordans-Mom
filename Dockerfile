# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install libopus-dev
RUN apt-get -y install ffmpeg

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY JordansMomBot.py JordansMomBot.py
COPY sound.py sound.py
COPY token.txt token.txt

CMD [ "python3", "-u", "-m", "JordansMomBot", "run"]