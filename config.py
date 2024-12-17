

mongo_service=27017
database_api_port=8000


weaviate_collection_name="development"
weaviate_host="localhost"
weaviate_service=8080
weaviate_grpc=50051
vectordb_api_port=8081


embedding_api_port=5000


llm_api_port=5001

textsplitter_api_port=5002

processor_api_port=7000

minio_port=9000

server_235 = "192.168.10.235"
server_226 = "128.214.255.226"
local = "0.0.0.0"


database_api_host = local
vectordb_api_host = local
embedding_api_host = server_226
llm_api_host = local
processor_api_host = local
textsplitter_api_host = local

minio_access_key = "minio"
minio_secret_key = "minio123"
minio_bucket = "fastapi-minio"
minio_endpoint = "localhost:9000"
minio_port = 9001