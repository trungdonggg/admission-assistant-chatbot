# Start Docker for vector database (Weaviate)
mkdir -p ~/weaviate/data

docker run -d \
        -p 8080:8080 -p 50051:50051 \
        -v ~/weaviate/data:/var/lib/weaviate \
        --name weaviate_vdb \
        semitechnologies/weaviate