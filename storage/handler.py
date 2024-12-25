from minio import Minio
from config import *
import json


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
        self.set_policy()
        

    def make_bucket(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name
    
    def set_policy(self):
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": ["*"]
                    },
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{self.bucket_name}"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": ["*"]
                    },
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{self.bucket_name}/*"
                    ]
                }
            ]
        }
        self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))


    def upload(self, key, value):
        res = self.client.put_object(self.bucket_name, key, value, -1, part_size=10*1024*1024)
        return res

    # def download(self, key, value):
    #     res = self.client.fget_object(self.bucket_name, key, value)
    #     return res 

    # def delete(self, keys):
    #     self.client.remove_objects(self.bucket_name, keys)
    #     return keys
