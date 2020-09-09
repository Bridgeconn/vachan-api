FROM python:3.8.1-slim-buster


WORKDIR /vachan-api
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /vachan-api/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /vachan-api