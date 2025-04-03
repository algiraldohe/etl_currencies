from include.helpers.data_storage import DataStorage
from typing import Tuple


class NotAvailableDataError(Exception):
    def __init__(self, process: Tuple[DataStorage, str]):
        super().__init__(f"No data available to process :: {process}")
