import pytest
from sqlalchemy import create_engine
from airflow.hooks.base import BaseHook
from sqlalchemy.exc import SQLAlchemyError
from airflow.models import Connection
from airflow.settings import Session
from unittest.mock import patch
import pandas as pd


def test_connection():
    _connection = BaseHook.get_connection("currencies-postgres-db")
    DATABASE_URL = f"postgresql+psycopg2://{_connection.login}:{_connection.password}@{_connection.host}:{_connection.port}/{_connection.schema}"
    engine = create_engine(DATABASE_URL)

    with engine.connect() as con:
        df = pd.read_sql("SELECT now()", con)
        print(df)

def test_sample():
    assert True

