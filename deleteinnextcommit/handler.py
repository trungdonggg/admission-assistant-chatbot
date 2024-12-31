from minio import Minio
from config import *
import json

# {
#   "id": "123e4567-e89b-12d3-a456-426614174000",
#   "file_name": "example.pdf",
#   "file_type": "application/pdf",
#   "file_size": 1048576,
#   "file_path": "https://yourbucket.s3.amazonaws.com/uploads/example.pdf",
#   "uploaded_by": "user_789",
#   "uploaded_at": "2024-12-30T12:00:00Z",
#   "metadata": {
#     "post_id": "post_123"
#   }
# }

class MinioHandler:
    def __init__(self):
        self.minio_url = minio_endpoint
        self.access_key = minio_access_key
        self.secret_key = minio_secret_key
        self.bucket_name = minio_bucket
        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.make_bucket()
        # self.set_policy()
        

    def make_bucket(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name
    
    # def set_policy(self):
    #     policy = {
    #         "Version": "2012-10-17",
    #         "Statement": [
    #             {
    #                 "Effect": "Allow",
    #                 "Principal": {
    #                     "AWS": ["*"]
    #                 },
    #                 "Action": [
    #                     "s3:GetBucketLocation",
    #                     "s3:ListBucket"
    #                 ],
    #                 "Resource": [
    #                     f"arn:aws:s3:::{self.bucket_name}"
    #                 ]
    #             },
    #             {
    #                 "Effect": "Allow",
    #                 "Principal": {
    #                     "AWS": ["*"]
    #                 },
    #                 "Action": [
    #                     "s3:GetObject"
    #                 ],
    #                 "Resource": [
    #                     f"arn:aws:s3:::{self.bucket_name}/*"
    #                 ]
    #             }
    #         ]
    #     }
    #     self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))


    def upload(self, key, value):
        res = self.client.put_object(self.bucket_name, key, value, -1, part_size=10*1024*1024)
        return res

    def download(self, key):
        res = self.client.get_object(self.bucket_name, key)
        return res.read()

    def delete(self, key):
        self.client.remove_object(self.bucket_name, key)
        return key
