docker compose \
    -f ./docker/docker-compose.minio.yaml \
    -f ./docker/docker-compose.backend.yml \
    --env-file ./env/.env.minio up --build
