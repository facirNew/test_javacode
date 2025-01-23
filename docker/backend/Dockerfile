FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY ./requirements.txt /temp/requirements.txt

RUN pip install --upgrade pip; pip install -r /temp/requirements.txt

COPY ./backend/ /backend/
