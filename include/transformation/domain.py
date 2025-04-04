from include.transformation.transformers import CurrenciesTransformer
from datetime import datetime
from airflow.models import Variable
import logging
import json
from typing import Any, Tuple
from include.helpers.data_storage import MinIOStorage
from include.helpers.config import config
from include.helpers.process_type import ProcessType


logger = logging.getLogger(__name__)

def transform_currencies(storage: MinIOStorage, filepath: str) -> str:
    execution_type = config.CURRENCIES_CONFIG.get("process")[0]["execution"]
    transformer = CurrenciesTransformer()

    # first read data from minio
    with storage.get_data(source=filepath) as response:  
        data = json.loads(response.read().decode("utf-8"))

    # then extract and format the timestamp
    raw_formatted_data = transformer.format_json_data(data)
    csv_bytes = transformer.json_to_csv(raw_formatted_data)

    # TODO: Create a function that encapsulates this logic to create filepath
    partition_year = datetime.now().year
    partition_month = datetime.now().month
    date_name = datetime.now().strftime("%Y-%m-%d")
    partition_state = Variable.get("staging-prefix")
    name = Variable.get("name")
    execution_type = config.CURRENCIES_CONFIG.get("process")[0]["execution"]

    new_filepath = f'{execution_type}/{partition_state}/{partition_year}/{partition_month}/{date_name}_{name}.csv'
    storage.write_data(data=csv_bytes, destination=new_filepath)

    return new_filepath