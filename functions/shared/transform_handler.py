import logging
from typing import Dict

import azure.functions as func
import pandas as pd
from azure.kusto.data.data_format import DataFormat
from transformations.index import get_transformations
from transformations.transform import Transform
from utils.settings import CLUSTER_URI, DB_NAME, MANAGED_CLIENT_ID

from .kusto_service_client import KustoServiceClient

logger = logging.getLogger("TransformHandler")


class TransformHandler:
    def __init__(self, blob_input: func.InputStream):
        self.json_string = self.__get_json_string(blob_input)
        self.kusto_clients = {}
        
    def __get_kusto_client_by_tablename(self, table_name: str):
        """Instantiate Kusto client

        Args:
            table_name (str): destination table name

        Returns:
            IngestionProperties: destination table name
        """
        if table_name not in self.kusto_clients:
            self.kusto_clients[table_name] = KustoServiceClient(
                cluster_uri=CLUSTER_URI,
                client_id=MANAGED_CLIENT_ID,
                db_name=DB_NAME,
                table_name=destination_table,
                data_format=DataFormat.CSV,
            )
        return self.kusto_clients[table_name]
        
    def handle_transform_request(self):
        """Handle the incoming Request to the Azure Function."""
        transformations = get_transformations(json_string=self.json_string)
        frames_dict = self.__get_dataframe_dict(transformations)
        if not frames_dict:
            logger.error("Frames Dict is Empty. Exiting Function.")
            return

        for table, frame in frames_dict.items():
            if frame.empty or not table:
                logger.debug(f"Frame is Empty or Table is not defined. Continuing")
                continue
            self.__ingest_data_frame(frame, table)
            logger.info(f"Ingested Frames to Table: {table}")

        logger.info("Azure Function Completed")

    def __get_json_string(self, input: func.InputStream) -> str:
        """Convert Input Stream to JSON String

        Args:
            input (func.InputStream): blob Input Stream

        Returns:
            str: Returns JSON String
        """
        return input.read().decode("utf-8")

    def __ingest_data_frame(
        self,
        blob_data_frame: pd.DataFrame,
        destination_table: str,
    ) -> None:
        """Ingest Data Frame to Kusto

        Args:
            blob_data_frame (pd.DataFrame): dataframe to ingest
            destination_table (str): Kusto Table that maps to the dataframe
        """
        
        self.__get_kusto_client_by_tablename(destination_table).ingest_data_frame(blob_data_frame)

    def __get_dataframe_dict(
        self, transforms: list[Transform]
    ) -> Dict[str, pd.DataFrame]:
        """Get Dictionary of table names to corresponding Data Frames

        Args:
            transform (Transform): Transform Instance that
                will transform json to data frame

        Returns:
            Dict[str, pd.DataFrame]: Dict[table_name, data_frame]
        """
        frames_dict: Dict[str, pd.DataFrame] = {}
        for transform in transforms:
            data_frame = transform.get_dataframe()
            frames_dict[transform.table] = data_frame

        return frames_dict
