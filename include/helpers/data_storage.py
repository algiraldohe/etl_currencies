
from abc import ABC, abstractmethod
from contextlib import contextmanager
import pandas as pd
from typing import Union
from io import BytesIO
from minio import Minio
from airflow.hooks.base import BaseHook
from airflow.models import Variable
import json
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

class DataStorage(ABC):
    """
    DataStorage class to handle the storage of data in a database.
    """

    @abstractmethod
    def get_data(self, source: str):
        pass

    @abstractmethod
    def write_data(self, data: Union[str, pd.DataFrame], destination: str):
        pass

class PostgresStorage(DataStorage):
    
    def __init__(self):
        self._connection = BaseHook.get_connection('currencies-postgres-db')
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        if self._engine is None:
            DATABASE_URL = f"postgresql+psycopg2://{self._connection.login}:{self._connection.password}@{self._connection.host}:{self._connection.port}/{self._connection.schema}"
            logger.info(f"Connecting to database: {DATABASE_URL}")
            self._engine = create_engine(DATABASE_URL)
        
        return self._engine

    @property
    def session_factory(self):
        if self._session_factory is None:
            self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            return self._session_factory
    
    @contextmanager
    def session_scope(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rolled back due to error: {e}")
            raise
        finally:
            session.close()

    def get_data(self, source):
        pass

    def write_data(self, data: Union[str, pd.DataFrame], destination: str):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Postgres write_data expects a pandas DataFrame")
        
        try:
            with self.engine.begin() as conn:
                data.to_sql(destination, conn, if_exists='append', index=False, method='multi')

        except Exception as e:
            logger.error(f"Error writing data to Postgres: {e}")
            raise


    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()


class MinIOStorage(DataStorage):
    """
    MinIOStorage class to handle the storage of data in a MinIO bucket.
    """
    
    def __init__(self):
        self._connection = BaseHook.get_connection('minio')
        self._client = None
        self.bucket_name = Variable.get("bucket_name")

    @property
    def client(self):
        endpoint_url = self._connection.extra_dejson.get("endpoint_url")
        if self._client is None:

            self._client = Minio(
                endpoint=endpoint_url.split('//')[1],
                access_key = os.getenv(f"{self._connection.login}"),
                secret_key = os.getenv(f"{self._connection.password}"),
                secure=False
            )

        
        return self._client
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._client:
            self._client = None
        
    @contextmanager
    def get_data(self, source: str):
        """
        Read data from a MinIO bucket.

        Parameters:
            source: str with the path to the file in the MinIO bucket

        Returns:
            data: DataFrame with the data read from the MinIO bucket
        """
        # Implement the logic to read data from MinIO
        object_name = source
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            yield response  # Yield the response to the 'with' block

        except Exception as e:
            logger.error(f"Error reading data from MinIO: {e}")
            raise

        finally:
            if response:
                response.close()
                response.release_conn()  # Release HTTP connection

    @contextmanager
    def _ensure_bucket(self):
        """
        Context manager to ensure the bucket exists.
        (Optional: Only needed if bucket creation is part of the write flow.)
        """
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        try:
            yield  # Yield control back to the caller
        except Exception as e:
            logger.error(f"MinIO bucket operation failed: {e}")
            raise

    def write_data(self, data: Union[dict, bytes], destination: str):
        """
        Write data to MinIO using a context manager for safety.
        
        Args:
            data: Dict to be written as JSON.
            destination: Object path in the bucket (e.g., "folder/file.json").
        """
        data_bytes = data

        if not data:
            raise ValueError("MinIO cannot write data if empty")
        
        # Convert data to JSON bytes
        if isinstance(data, dict):
            data_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")       

        # Use context managers for bucket safety and resource cleanup
        with self._ensure_bucket(), BytesIO(data_bytes) as buffer:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=destination,
                data=buffer,
                length=len(data_bytes)
            )
