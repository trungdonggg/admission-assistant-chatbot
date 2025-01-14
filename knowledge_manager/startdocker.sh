# Start Docker for database (MongoDB)
docker run --name mongodb -d -p 27017:27017 mongo



# Start Docker for object storage (MinIO)
mkdir -p ~/minio/data

docker run \
    -d \
    -p 9000:9000 \
    -p 9001:9001 \
    --name minio \
    -v ~/minio/data:/data \
    -e "MINIO_ROOT_USER=minio" \
    -e "MINIO_ROOT_PASSWORD=minio123" \
    quay.io/minio/minio server /data --console-address ":9001"
    