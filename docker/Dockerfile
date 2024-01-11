FROM tiangolo/uvicorn-gunicorn:python3.10

COPY ./app /app/app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
WORKDIR /app/app
