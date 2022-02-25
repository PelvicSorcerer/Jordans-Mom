# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY JordansMomBot.py JordansMomBot.py
COPY sound.py sound.py
COPY token.txt token.txt
COPY BotFiles BotFiles

CMD [ "python3", "-m", "JordansMomBot", "run"]