from datetime import datetime
from include.extraction.pullers import PullerAPI
from include.helpers.data_storage import DataStorage
from include.helpers.config import config
from airflow.models import Variable
import logging


logger = logging.getLogger(__name__)


def extract_currencies(puller: PullerAPI, storage: DataStorage) -> str:
    """
    Parameters:
        puller: module in charge of the extraction form the specific API
    Returns:
        path: str with the path to the minio location of the response data
    """
    partition_year = datetime.now().year
    partition_month = datetime.now().month
    date_name = datetime.now().strftime("%Y-%m-%d")
    partition_state = Variable.get("source-prefix")
    name = Variable.get("name")
    execution_type = config.CURRENCIES_CONFIG.get("process")[0]["execution"]

    filepath = f'{execution_type}/{partition_state}/{partition_year}/{partition_month}/{date_name}_{name}.json'
    response = puller.get_data()
    data = response.json()
    try:
        storage.write_data(data=data, destination=filepath)

    except Exception as e:
        logger.error(f"Error writing data to MinIO: {e}")
        raise

    return filepath

