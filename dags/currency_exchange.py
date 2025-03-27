"""
## Currency Exchange ETL DAG

This DAg retrieves the currency exchange information from a public API,
transforms the data, and loads it into a database.

"""

from airflow.decorators import dag, task
from datetime import datetime
import logging

@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    doc_md=__doc__,
    default_args={"owner": "algiraldohe", "retries": 1},
    tags=["etl", "finance", "data_engineering"],
)
def currency_exchange():

    logger = logging.getLogger(__name__)

    @task
    def extract():
        logger.info(" START DAG :: Executing the extraction process...")
        return "This is the extraction process"
    
    @task
    def transform():
        return "This is the transformation process"
    
    @task
    def load():
        logger.info(" END DAG :: Executing the load process...")
        return "This is the loading process"
    
    
    extract() >> transform() >> load()


currency_exchange()