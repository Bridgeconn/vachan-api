# FROM python:3.6-alpine


# WORKDIR /vachan-api
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # We copy just the requirements.txt first to leverage Docker cache
# COPY requirements.txt /vachan-api/requirements.txt

# RUN apk update && apk add -U --no-cache bash python3 python3-dev libpq postgresql-dev unixodbc-dev musl-dev g++ libffi-dev && pip3 install --upgrade --no-cache-dir pip setuptools==49.6.0 && pip3 install --no-cache-dir -r requirements.txt && ln -s /usr/bin/python3 /usr/bin/python && apk del --no-cache python3-dev postgresql-dev unixodbc-dev musl-dev g++ libffi-dev


# COPY . /vachan-api
FROM ubuntu:18.04

WORKDIR /vachan-api
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y libpq-dev libssl-dev postgresql python3-pip python3-dev && \
    apt-get install python3.6-dev build-essential

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /vachan-api/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /vachan-api