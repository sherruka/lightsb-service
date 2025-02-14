docker compose \
    -f ./docker/docker-compose.minio.yaml \
    -f ./docker/docker-compose.web.yaml \
    -f ./docker/docker-compose.backend.yaml \
    --env-file ./env/.env.minio \
    --env-file ./env/.env.backend down

sudo rm -rf app/__pycache__ 
