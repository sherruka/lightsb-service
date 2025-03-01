FROM python:3.10
COPY ./app ./app
RUN pip install "fastapi[all]" uvicorn sqlalchemy psycopg2 pydantic
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
