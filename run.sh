docker compose \
    -f ./docker/docker-compose.minio.yaml \
    -f ./docker/docker-compose.FastAPI.yaml \
    -f ./docker/docker-compose.nginx.yaml \
    -f ./docker/docker-compose.postgres.yaml \
    -f ./docker/docker-compose.locust.yaml \
    --env-file ./env/.env.minio \
    --env-file ./env/.env.backend up --build
