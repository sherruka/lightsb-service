FROM python:3.10
RUN pip install "fastapi[all]" uvicorn sqlalchemy psycopg2 pydantic bcrypt==4.0.1 jwt passlib python-jose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
