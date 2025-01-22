# constants, should not be change. if you want to change these value, you should modify startdocker.sh files and config starting docker process also. 
mongo_service=27017
knowledge_management_api_port=8000

weaviate_collection_name="development"
weaviate_host="localhost"
weaviate_service=8080
weaviate_grpc=50051
vectordb_api_port=8081

embedding_api_port=5000

llm_api_port=5001

textsplitter_api_port=5002

processor_api_port=7000

minio_access_key = "minio"
minio_secret_key = "minio123"
minio_bucket = "ttu-storage"
minio_endpoint = "localhost:9000"
minio_manager_port = 9001
minio_port=9000



# variable, these value below can be change for your need.
server_235 = "192.168.10.235"
server_226 = "128.214.255.226"
may_12_labsoe = "192.168.80.125"
local = "0.0.0.0"


knowledge_management_api_host = local
vectordb_api_host = local
embedding_api_host = server_226
llm_api_host = local
processor_api_host = local
textsplitter_api_host = local



rabbitmq_url = "amqp://guest:guest@0.0.0.0/"

all_queues = {
    "vectordb": "vectordb",
    "embedding": "embedding",
    "llm": "llm",
    "processor": "processor",
}
