FROM python:3.8

WORKDIR /vachan-api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
    apt-get install -y libpq-dev libopenblas-dev liblapack-dev libssl-dev gcc gfortran cython postgresql python3-pip python3-dev && \
    pip3 install srsly

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /vachan-api/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /vachan-api