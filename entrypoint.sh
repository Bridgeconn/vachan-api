#!/bin/sh
echo "Waiting for PostgreSQL..."
while ! nc -z postgresql 5432; do
    sleep 0.1
done
echo "PostgreSQL Started"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]