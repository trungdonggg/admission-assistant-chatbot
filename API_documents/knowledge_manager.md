# Knowledge Manager API Documentation

## Overview
The Knowledge Manager is a service that handles document storage, retrieval, and chat history management. It integrates with MongoDB for metadata storage and MinIO for file storage.


## API Endpoints

### Document Management
categories = Literal[
    "thong_tin_truong_dai_hoc",   # thông tin về trường đại học
    "thong_tin_khoa_cong_nghe_thong_tin",  # thông tin về khoa công nghệ thông tin
    "thong_tin_khoa_ngon_ngu",  # thông tin về khoa ngôn ngữ
    "thong_tin_khoa_kinh_te",  # thông tin về khoa kinh tế
    "thong_tin_khoa_y",  # thông tin về khoa y
    "thong_tin_khoa_cong_nghe_sinh_hoc",  # thông tin về khoa công nghệ sinh học
    "thong_tin_khoa_dieu_duong",  # thông tin về khoa điều dưỡng
    "thong_tin_khoa_khai_phong",  # thông tin về khoa khai phóng
    "thong_tin_giang_vien",    # thông tin về giảng viên
    "thong_tin_nghien_cuu",     # thông tin về nghiên cứu
    "thong_tin_chi_phi",     # thông tin về tất cả chi phí (học phí, nợ môn, thi lại, v.v.)
] 
#### Add Document
- **Endpoint**: `/add_document`
- **Method**: POST
- **Parameters**:
  - `file`: File (Upload)
  - `content`: string
  - `owner`: string
  - `category`: List[categories]
  - `department`: string
  - `description`: string
  - `university`: string
  - `addition`: Optional[Dict]
- **Description**: Uploads a new document with metadata

#### Get Documents
- **Endpoint**: `/get_documents`
- **Method**: GET
- **Parameters**:
  - `document_name`: Optional[string]
- **Description**: Retrieves all documents or a specific document if name is provided

#### Get User Documents
- **Endpoint**: `/get_user_documents/{user}`
- **Method**: GET
- **Parameters**:
  - `user`: string
- **Description**: Retrieves all documents owned by a specific user

#### Download Document
- **Endpoint**: `/download_document/{document_name}`
- **Method**: GET
- **Parameters**:
  - `document_name`: string
- **Description**: Downloads a specific document

#### Delete Document
- **Endpoint**: `/delete_document/{document_name}`
- **Method**: DELETE
- **Parameters**:
  - `document_name`: string
- **Description**: Deletes a specific document

### Chat History Management

#### Add History
- **Endpoint**: `/add_history`
- **Method**: POST
- **Parameters**:
  - `user`: string
  - `messages`: List
  - `conversation`: List
  - `summary`: string
- **Description**: Adds chat history for a user

#### Get History
- **Endpoint**: `/get_history/{user}`
- **Method**: GET
- **Parameters**:
  - `user`: string
- **Description**: Retrieves chat history for a specific user

#### Delete History
- **Endpoint**: `/delete_history/{user}`
- **Method**: DELETE
- **Parameters**:
  - `user`: string
- **Description**: Deletes chat history for a specific user

## Data Models

### DocumentMetadata
```python
{
    "name": string,          # Name of the file
    "size": int,            # Size of the file in bytes
    "type": string,         # Type of the file
    "content": string,      # Content of the file in text format
    "owner": string,        # Owner of the file
    "category": List[categories], # Category of the file
    "department": string,   # Department associated with the file
    "description": string,  # Description of the file
    "university": string,   # University associated with the file
    "addition": Optional[dict], # Additional information
    "minio": Dict,         # Minio return data
    "url": string          # URL to download the file
}
```

### AddChatHistoryRequest
```python
{
    "user": string,         # User name
    "messages": List,       # List of all messages
    "conversation": List,   # List of human and assistant messages
    "summary": string       # Summary of conversation
}
```

## Storage Systems

### MinIO Storage
- Used for storing document files
- Configuration required:
  - `MINIO_ENDPOINT`
  - `MINIO_ACCESS_KEY`
  - `MINIO_SECRET_KEY`
  - `MINIO_BUCKET`

### MongoDB
- Used for storing document metadata and chat history
- Collections:
  - Documents
  - History

## Running the Service
1. Start the required Docker containers:
```bash
# Start MongoDB
docker run --name mongodb -d -p 27017:27017 mongo

# Start MinIO
docker run -d -p 9000:9000 -p 9001:9001 --name minio \
    -v ~/minio/data:/data \
    -e "MINIO_ROOT_USER=minio" \
    -e "MINIO_ROOT_PASSWORD=minio123" \
    quay.io/minio/minio server /data --console-address ":9001"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the service:
```bash
python app.py