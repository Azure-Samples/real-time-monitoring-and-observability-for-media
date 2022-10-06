import logging
from typing import Literal, Union

from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.data.data_format import DataFormat
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.ingest import IngestionProperties, KustoStreamingIngestClient
from pandas import DataFrame

logger = logging.getLogger("KustoServiceClient")


class KustoServiceClient:
    """Kusto Service Class for handling Kusto Python SDK Calls"""

    def __init__(
        self,
        cluster_uri: str,
        client_id: str,
        db_name: str,
        table_name: str,
        data_format: Union[Literal[DataFormat.JSON], Literal[DataFormat.CSV]],
    ) -> None:
        """Constructor of KustoClient

        Args:
            cluster_uri (str): Kusto Cluster Ingest URI
            client_id (str): Managed Identity Client ID
            db_name (str): Database Name on Kusto Cluster
            table_name (str): Table Name in `db_name`
            data_format (Union[Literal[DataFormat.JSON], Literal[DataFormat.CSV]]): Data Format for Ingestion
        """
        self.cluster_uri = cluster_uri
        self.db_name = db_name
        self.table_name = table_name
        self.data_format = data_format
        self.client_id = client_id
        self.client: KustoStreamingIngestClient = self.__get_client()

    def ingest_data_frame(self, data: DataFrame) -> None:
        """Ingest Pandas DataFrame of incoming data to Data Explorer

        Args:
            data (DataFrame): Pandas DataFrame to be uploaded to Data Explorer
        """
        ingestion_props = self.__get_ingestion_properties()
        try:
            self.client.ingest_from_dataframe(
                df=data, ingestion_properties=ingestion_props
            )
        except KustoServiceError as err:
            logger.error(f"KustoServiceError when Ingesting From Dataframe: {err}")
            raise err
        except Exception as err:
            logger.error(f"KustoServiceClient#ingest_data_frame() Error: {err}")
            raise err

    def __get_client(self) -> KustoStreamingIngestClient:
        """Get Kusto Streaming Client

        Returns:
            KustoStreamingIngestClient: Streaming Ingest Kusto Client
        """
        try:
            # ? use #with_az_cli_authentication for local function developement
            # kcsb_ing = KustoConnectionStringBuilder.with_az_cli_authentication(self.cluster_uri)
            kcsb_ing = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(
                self.cluster_uri, self.client_id
            )
            return KustoStreamingIngestClient(kcsb_ing)
        except KustoServiceError as err:
            logger.error(f"KustoServiceError when creating Kusto Client: {err}")
            raise err
        except Exception as err:
            logger.error(f"KustoServiceClient#get_client() Error: {err}")
            raise err

    def __get_ingestion_properties(self) -> IngestionProperties:
        """Get Ingestion Properties for Kusto Client Instance

        Returns:
            IngestionProperties:
                database: Name of Database for Ingestion
                table: Table in Database that the data will be uploaded to
                data_format: JSON or CSV format for upload.
        """
        return IngestionProperties(
            database=self.db_name, table=self.table_name, data_format=self.data_format
        )
