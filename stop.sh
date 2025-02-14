docker compose \
    -f ./docker/docker-compose.minio.yaml \
    -f ./docker/docker-compose.web.yml \
    --env-file ./env/.env.minio down

sudo rm -rf app/__pycache__ 
