FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app/app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app/app
RUN mkdir ../logs
RUN touch ../logs/API_logs.log
