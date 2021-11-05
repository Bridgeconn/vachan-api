FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app/app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
