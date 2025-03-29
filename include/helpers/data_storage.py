
from abc import ABC, abstractmethod
import pandas as pd
from typing import Union
from io import BytesIO
from minio import Minio
from airflow.hooks.base import BaseHook
from airflow.models import Variable
import json
import os


class DataStorage(ABC):
    """
    DataStorage class to handle the storage of data in a database.
    """

    @abstractmethod
    def read(self, source: str):
        pass

    @abstractmethod
    def write(self, data: Union[str, pd.DataFrame], destination: str):
        pass


class MinIOStorage(DataStorage):
    """
    MinIOStorage class to handle the storage of data in a MinIO bucket.
    """
    
    def __init__(self):
        minio = BaseHook.get_connection('minio')
        endpoint_url = minio.extra_dejson.get("endpoint_url")
        client = Minio(
            endpoint=endpoint_url.split('//')[1],
            access_key = os.getenv(f"{minio.login}"),
            secret_key = os.getenv(f"{minio.password}"),
            secure=False
        )
        
        self.client = client
        self.bucket_name = Variable.get("bucket_name")

    def read(self, source: str) -> pd.DataFrame:
        """
        Read data from a MinIO bucket.

        Parameters:
            source: str with the path to the file in the MinIO bucket

        Returns:
            data: DataFrame with the data read from the MinIO bucket
        """
        # Implement the logic to read data from MinIO
        pass

    def write(self, data: dict, destination: str):
        """
        Write data to a MinIO bucket.

        Parameters:
            data: str or DataFrame with the data to be written
            destination: str with the path to the file in the MinIO bucket
        """
        # Implement the logic to write data to MinIO
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

        data = json.dumps(data, ensure_ascii=False).encode("utf8")
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=destination,
            data=BytesIO(data),
            length=len(data),
    )