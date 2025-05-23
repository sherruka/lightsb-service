FROM python:3.8-slim

WORKDIR /locust
COPY locustfile.py .
RUN pip install --no-cache-dir locust requests-toolbelt

ENTRYPOINT ["locust", "-f", "locustfile.py"]
