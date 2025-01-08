# Admission Assistant Chatbot System

This is a distributed system designed so you can have them working on different server.

## These are the steps to start this system:

### 1. Clone the project: 
    
    git clone https://github.com/trungdonggg/admission-assistant-chatbot
    cd admission-assistant-chatbot

### 2. Config environment

Make a *.env* file at the root of the project:
    
    touch .env

Get a [Google AI Studio API key](https://aistudio.google.com/apikey) and add to *.env* file as I did in *.env.example*


### 3. Starting services:
   
#### 3.1 Start embedding service:

    cd embedding
    sh run.sh

#### 3.2 Start text splitter service:

    cd textsplitter
    sh run.sh

#### 3.3 Start vector database (weaviate) service:

    cd vector_database

- If you haven't started vector database (weaviate) docker:

        sh startdocker.sh
        sh run.sh

- If you already started vector database (weaviate) docker:

        sh run.sh


#### 3.4 Start knowledge management service:

    cd knowledge_management

- If you haven't started knowledge management's docker:

        sh startdocker.sh
        sh run.sh

- If you already started knowledge management's docker:

        sh run.sh
    

#### 3.5 Start the processor service:

    cd processor
    sh run.sh


