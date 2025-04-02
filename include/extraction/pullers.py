from abc import ABC, abstractmethod
import os
from airflow.models import Variable
import requests
from include.helpers.process_type import ProcessType
import json
import yaml
import logging
from include.helpers.config import config


ENDPOINT_TABLE = {
    ProcessType.BULK: "timeframe",
    ProcessType.DAILY: "live",

}

logger = logging.getLogger(__name__)

class PullerAPI(ABC):
    """
    PullerAPI class to handle the extraction of data from a public API.
    """
    @abstractmethod
    def get_data(self) -> str:
        pass


class RequestBuilder:

    API_URL = Variable.get("api_url")
    API_KEY = os.getenv("API_LAYER_KEY")
    CONFIG = config.CURRENCIES_CONFIG


    def __init__(self):
        self.exec_type = ProcessType(RequestBuilder.CONFIG.get("process")[0]["execution"])
    

    def get_historical(self, endpoint:str) -> str:
        """
        Parameters: Come from the config of the workflow and not directly passed to the user.
            begin: date
            end: date

        Returns:
            request: string with the specific request for the API
        """

        start_date = RequestBuilder.CONFIG.get("process")[1]["start_date"]
        end_date = RequestBuilder.CONFIG.get("process")[2]["end_date"]
        query = f"?start_date={start_date}&end_date={end_date}"
        headers = {"Content-Type": "application/json", "apikey": self.API_KEY}

        request = {
            "url": f"{self.API_URL}{endpoint}{query}",
            "headers": headers
        }

        return request
    
    def get_live(self, endpoint:str) -> str:
        """
        Parameters: Come from the config of the workflow and not directly passed to the user.
            reference_currency: str
            currencies_list: list    

        Returns:
            data: json like str with the data from the API
        """
        reference_currency = RequestBuilder.CONFIG.get("reference_currency")
        currencies_list = RequestBuilder.CONFIG.get("currencies")
        query = f"?source={reference_currency}&currencies={','.join(currencies_list)}"
        headers = {"Content-Type": "application/json", "apikey": self.API_KEY}

        request = {
            "url": f"{self.API_URL}{endpoint}{query}",
            "headers": headers
        }

        return request
    

class APILayer(PullerAPI):

    def get_data(self) -> str:
        """
        Parameters: Come from the config of the workflow and not directly passed to the user.
            reference_currency: str
            currencies_list: list    

        Returns:
            data: json like str with the data from the API
        """
        builder = RequestBuilder()

        if builder.exec_type == ProcessType.BULK:
            request = builder.get_historical(ENDPOINT_TABLE[builder.exec_type])

        elif builder.exec_type == ProcessType.DAILY:
            request = builder.get_live(ENDPOINT_TABLE[builder.exec_type])

        try:
            return requests.get(request["url"], headers=request["headers"])

        except Exception as e:
            logging.error(f"Error in the request: {e}")
            raise
