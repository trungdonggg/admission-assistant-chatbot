# Admission Assistant Chatbot System

This is a distributed system designed so you can have them working on different server.

## These are the steps to start this system:

### 1. Clone the project: 
    
    git clone https://github.com/trungdonggg/admission-assistant-chatbot

### 2. Config environment

Make a *.env* file at the root of the project:
    
    touch admission-assistant-chatbot/.env

Get a [Google AI Studio API key](https://aistudio.google.com/apikey) and add to *.env* file as I did in *.env.example*


### 3. Starting services:
   
#### 3.1 Start embedding service:
    
    sh admission-assistant-chatbot/embedding/run.sh

#### 3.2 Start text splitter service:

    sh admission-assistant-chatbot/textsplitter/run.sh

#### 3.3 Start vector database (weaviate) service:

    sh admission-assistant-chatbot/vector_database/run.sh

- If docker for vector database service is already running:

      sh admission-assistant-chatbot/vector_database/run.sh docker=false

#### 3.4 Start knowledge management service:

    sh admission-assistant-chatbot/knowledge_management/run.sh
    
- If docker for knowledge management service is already running:

      sh admission-assistant-chatbot/knowledge_management/run.sh docker=false

#### 3.5 Start the processor service:

    sh admission-assistant-chatbot/processor/run.sh


