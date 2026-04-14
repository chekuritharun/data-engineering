FROM python:3.9

WORKDIR /app
COPY . .

RUN pip install requests psycopg2-binary pydantic

CMD ["python", "etl.py"]
