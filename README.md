# Admission Assistant Chatbot

An intelligent chatbot system designed to assist with university admissions inquiries using advanced natural language processing and vector database technology.

## 🌟 Features

- Natural language processing for understanding admission-related queries
- Vector database-powered knowledge retrieval
- Facebook Messenger integration
- Modular architecture with microservices
- Scalable document processing and embedding
- Containerized deployment support

## 🏗️ Architecture

The project is organized into several key components:

- `embedder/`: Text embedding service
- `knowledge_manager/`: Knowledge base management system
- `messenger_adapter/`: Facebook Messenger integration
- `processor/`: Query processing service
- `textsplitter/`: Document processing service
- `vector_database/`: Vector storage and retrieval system

## 🚀 Getting Started

### Prerequisites

- Python 3.11
- Docker
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/trungdonggg/admission-assistant-chatbot
cd admission-assistant-chatbot
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Get a [Google AI Studio API key](https://aistudio.google.com/apikey) and add it to the `.env` file

4. Get a [Facebook Page Access Token](https://developers.facebook.com/) and [Page Access Token](https://developers.facebook.com/) and add it to the `.env` file

### Deployment

#### 1. Start RabbitMQ Service
RabbitMQ should be running on port 5672
```bash
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```
Add ip-address of the machine that run RabbitMQ to config.py


#### 2. Start Individual Services

##### Embedding Service
```bash
cd embedding
sh run.sh
```

##### Text Splitter Service
```bash
cd textsplitter
sh run.sh
```

##### Vector Database (Weaviate) Service
```bash
cd vector_database
```
For first-time setup:
```bash
sh startdocker.sh
sh run.sh
```
For subsequent runs:
```bash
sh run.sh
```

##### Knowledge Manager Service
```bash
cd knowledge_manager
```
For first-time setup:
```bash
sh startdocker.sh
sh run.sh
```
For subsequent runs:
```bash
sh run.sh
```
Add ip-address of the machine that run Knowledge Manager Service to config.py

##### Processor Service
```bash
cd processor
sh run.sh
```

##### Messenger Adapter
```bash
cd messenger_adapter
sh run.sh
```
## How to test:
1. Add docs to database:
- Check API_doccuments/document_manager.md

2. Test chatbot: We will test at messenger_adapter endpoint.
- @app.post("/test_embedder")
	{content: list[str]}

- @app.post("/test_splitter")
	{text: str}

- @app.post("/test_query")
	{
		user: str
    	query: str
    }

- check messenger_adapter/app.py for more...

## 🔧 Services

### Core Services
- MongoDB: Document storage (Port: 27017)
- Weaviate: Vector database (Port: 8080, gRPC: 50051)
- MinIO: Object storage (Ports: 9000, 9001)
- RabbitMQ: Message queue (Port: 5672)

### API Services
- Knowledge Manager API (Port: 8000)
- Messenger Adapter API (Port: 7000)

## 📚 API Documentation

API documentation can be found in the `API_documents/` directory.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 👥 Authors

- [Project Owner]
- Contributors

## 📞 Support

For support and queries, please open an issue in the repository.
