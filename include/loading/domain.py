import pandas as pd
from io import StringIO
from include.helpers.data_storage import DataStorage
from include.helpers.config import config
import logging
from sqlalchemy import text


logger = logging.getLogger(__name__)

def load_currencies_data(filepath:str, storage: DataStorage, *, object_storage: DataStorage) -> None:
    # load csv data from minio
    with object_storage.get_data(source=filepath) as response:  
        csv_content = response.read().decode("utf-8")
    
    df = pd.read_csv(StringIO(csv_content))

    # then format the data correctly to match the schema
    columns = config.CURRENCIES_CONFIG["mapping"]
    df.rename(columns=columns, inplace=True)

    # add ref currency as a column in the final dataset
    reference_currency_value = config.CURRENCIES_CONFIG["reference_currency"]
    ref_column = ''.join(["rate_", reference_currency_value.lower()])
    df[ref_column] = float(1)
    df["reference_currency"] = reference_currency_value

    # sorting columns in appropriate order
    df = df[["timestamp", "reference_currency", ref_column] + list(columns.values())]
    # TODO: rename this column since the transformation step
    df.rename(columns={"timestamp": "date_key"}, inplace=True)
    print(df.info())

    # then load the data into the postgres database
    with storage.session_scope() as session:
        try:
            query = text(
                """
                SELECT 
                    MIN(date_key) min_date_key, 
                    MAX(date_key) max_date_key 
                FROM currency_exchange_rates
                """
            )

            result = session.execute(query).fetchall()
            print("QUERY_OUTPUT:", result)

        except Exception as e:
            logger.error(f"Error loading data into database: {e}")
            raise

        else:
            if result and all(item is not None for item in result[0]):
                min_date_key, max_date_key = result[0]
                logger.info("Existing date_keys: %s - %s", min_date_key, max_date_key)
                
                print(df.shape)
                df = df[~df["date_key"].between(min_date_key, max_date_key, inclusive='both')]
                print(df.shape)

                if df.empty:
                    message = "No new date_keys to load into the database."
                    logger.info(message)

            else:
                try:
                    storage.write_data(data=df, destination="currency_exchange_rates")
                    logger.info(f"Data loaded into the database. {df.shape[0]} rows inserted.")

                except Exception as e:
                    logger.error("Error inserting DataFrame into Postgres: %s", e)
                    raise

    return "Data loaded successfully"