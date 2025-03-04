# constants, should not be change. if you want to change these value, you should modify startdocker.sh files and config starting docker process also.
mongo_service = 27017

weaviate_collection_name = "development"
weaviate_host = "localhost"
weaviate_service = 8080
weaviate_grpc = 50051

minio_access_key = "minio"
minio_secret_key = "minio123"
minio_bucket = "ttu-storage"
minio_endpoint = "localhost:9000"
minio_manager_port = 9001
minio_port = 9000


knowledge_manager_api_port = 8000
messenger_adapter_api_port = 7000


# variables, these value below can be change for your need.
rabit_mq_server = "0.0.0.0"

knowledge_manager_api_host = "0.0.0.0"
messenger_adapter_api_host = "0.0.0.0"


rabbitmq_url = f"amqp://guest:guest@{rabit_mq_server}/"

all_queues = {
    "vectordb": "vectordb",
    "embedder": "embedder",
    "processor": "processor",
    "textsplitter": "textsplitter",
}
