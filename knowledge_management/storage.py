from minio import Minio
from config import *
from typing import Dict

class MinioHandler:
    def __init__(self) -> None:
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

    def make_bucket(self) -> str:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name
   
    def upload(self, key, value) -> Dict:
        res = self.client.put_object(self.bucket_name, key, value, -1, part_size=10*1024*1024)
        return {
            "bucket_name": self.bucket_name,
            "object_name": res.object_name
        }

    def download(self, key) -> bytes:
        res = self.client.get_object(self.bucket_name, key)
        return res.read()

    def delete(self, key) -> str:
        self.client.remove_object(self.bucket_name, key)
        return key
