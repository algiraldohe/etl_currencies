import os
import yaml
from airflow.models import Variable

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance
    
    def load_config(self):
        with open(Variable.get("currency_exchange_config"), "r") as f:
            self.CURRENCIES_CONFIG = yaml.safe_load(f)

# Create single instance when module loads
config = Config()