FROM python:3.10
COPY ./app ./app
RUN pip install "fastapi[all]" uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
