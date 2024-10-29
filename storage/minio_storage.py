from flask import request, jsonify
from flask_restful import Resource
from minio import Minio
from minio.error import S3Error
import datetime
import json
import os

class MinioClient:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        # Initialize MinIO client
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def ensure_bucket_exists(self, bucket_name):
        # Create the bucket if it doesn't exist
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload_file(self, bucket_name, object_name, file_path):
        # Upload a file to the specified bucket
        self.client.fput_object(
            bucket_name,
            object_name,
            file_path
        )

    def download_file(self, bucket_name, object_name, file_path):
        # Download a file from MinIO
        self.client.fget_object(
            bucket_name,
            object_name,
            file_path
        )

    def object_exists(self, bucket_name, object_name):
        # Check if an object exists in the bucket
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False


class ChatHistory(Resource):
    def __init__(self):
        # Set up MinIO client configuration
        self.bucket_name = "chat-history"
        self.minio_client = MinioClient(
            endpoint="127.0.0.1:9000",  # Replace with your MinIO server address
            access_key="minioadmin",   # Replace with your MinIO access key
            secret_key="minioadmin",   # Replace with your MinIO secret key
            secure=False               # Set to True if using HTTPS
        )
        
        # Ensure the bucket exists
        self.minio_client.ensure_bucket_exists(self.bucket_name)

    def post(self):
        try:
            data = request.json

            # Ensure the data contains a 'username' and 'messages'
            username = data.get("username")
            messages = data.get("messages")

            if not username or not messages:
                return jsonify({"error": "Username and messages are required"}), 400

            # Create a filename using username
            filename = f"{username}.json"
            temp_file = f"/tmp/{filename}"

            chat_history = {"username": username, "messages": [], "timestamp": ""}

            # Check if the chat history file already exists in MinIO
            if self.minio_client.object_exists(self.bucket_name, filename):
                # Download the existing file
                self.minio_client.download_file(self.bucket_name, filename, temp_file)

                # Load the existing chat history
                with open(temp_file, "r") as f:
                    chat_history = json.load(f)

                # Append the new messages
                chat_history["messages"].extend(messages)
            else:
                # Create a new chat history with the new messages
                chat_history["messages"] = messages

            # Update the timestamp
            chat_history["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save the updated chat history to a file
            with open(temp_file, "w") as f:
                json.dump(chat_history, f)

            # Upload the file to MinIO
            self.minio_client.upload_file(
                self.bucket_name,  # Bucket name
                filename,          # Object name
                temp_file          # File path
            )

            # Remove the temporary file
            os.remove(temp_file)

            return jsonify({"message": "Chat history saved successfully!"}), 200

        except S3Error as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
