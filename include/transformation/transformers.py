import csv
from io import StringIO
from typing import Any, Tuple
from datetime import datetime
from include.helpers.config import config
from include.helpers.process_type import ProcessType
import logging


logger = logging.getLogger(__name__)

class CurrenciesTransformer:
    CONFIG = config.CURRENCIES_CONFIG

    def __init__(self):
        self.currencies = self.CONFIG.get("currencies")
        self.reference_currency = self.CONFIG.get("reference_currency")
        self.exec_type = ProcessType(CurrenciesTransformer.CONFIG.get("process")[0]["execution"])

    def format_json_data(self, data:dict) -> dict:
        if self.exec_type == ProcessType.DAILY:
            datetime_ =  format_timestamp_to_datetime(data["timestamp"])
            raw_formatted_data = {
                datetime_ : data["quotes"]
            }

        elif self.exec_type == ProcessType.BULK:
            raw_formatted_data = data["quotes"]

        return raw_formatted_data

    def json_to_csv(self, data: dict) -> bytes:

        fieldnames = list(CurrenciesTransformer.CONFIG.get("mapping").keys())
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()

        for row in data.items():
            writer.writerow(row[1])

        csv_bytes = csv_buffer.getvalue().encode("utf-8")
        csv_buffer.close()

        return csv_bytes
         

def format_timestamp_to_datetime( timestamp:str) -> str:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    

def filter_by_currency(data:str) -> Tuple[str, str]:
    pass

def structure_as_tabular(data:str) -> Any:
    pass
