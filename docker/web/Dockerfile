FROM python:3.10
WORKDIR /app
RUN pip install "fastapi[all]" uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
