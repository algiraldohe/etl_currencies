"""
## Currency Exchange ETL DAG

This DAg retrieves the currency exchange information from a public API,
transforms the data, and loads it into a database.

"""

from airflow.decorators import dag, task
from datetime import datetime
from include.extraction.pullers import APILayer
from include.helpers.data_storage import MinIOStorage
from include.extraction.domain import extract_currencies
from include.transformation.domain import transform_currencies
import logging

@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    doc_md=__doc__,
    default_args={"owner": "algiraldohe"},
    tags=["etl", "finance", "data_engineering"],
)
def currency_exchange():

    logger = logging.getLogger(__name__)

    @task
    def extract():
        logger.info(" START DAG :: Executing the extraction process...")

        puller = APILayer()
        storage = MinIOStorage()

        return extract_currencies(puller=puller, storage=storage)
    
    @task
    def transform(filepath: str):
        logger.info(" PROCESSING DAG :: Executing the transformation process...")

        storage = MinIOStorage()
        logger.info(f"Processing file: {filepath}")
        return transform_currencies(storage=storage, filepath=filepath)
        

    
    @task
    def load():
        logger.info(" END DAG :: Executing the load process...")
        return "This is the loading process"
    
    
    # extract() >> transform(filepath='{{ ti.xcom_pull(task_ids="extract") }}') >> load()
    transform(filepath="daily/src/2025/4/2025-04-03_currencies.json")


currency_exchange()