docker compose \
    -f ./docker/docker-compose.minio.yaml \
    --env-file ./env/.env.minio up --build
