import unittest
from unittest.mock import Mock, patch

import pandas as pd
from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.data.data_format import DataFormat
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.ingest import KustoStreamingIngestClient
from shared.kusto_service_client import KustoServiceClient


class TestKustoClient(unittest.TestCase):
    def setUp(self) -> None:
        """Set Up Values

        self.test_cluster_uri: fake Kusto cluster ingest uri
        self.test_db_name: Fake Kusto Database name
        self.test_table_name: Fake Kusto Table name
        self.test_data_format: Fake dataformat used
        self.kusto_client: Instantiate reusable Kusto Client
        self.data_frame: Reusable pandas Dataframe in Tests
        """
        self.test_cluster_uri = "https://fakedataexplorer.region.kusto.windows.net"
        self.test_db_name = "fakedb"
        self.test_table_name = "fakeTable"
        self.test_data_format = DataFormat.CSV

        self.kusto_client = KustoServiceClient(
            cluster_uri=self.test_cluster_uri,
            client_id="xxx-123-456",
            db_name=self.test_db_name,
            table_name=self.test_table_name,
            data_format=self.test_data_format,
        )

        self.data_frame: pd.DataFrame = pd.DataFrame({"a": [1, 2, 3, 4, 5]})

    # @patch("shared.kusto_service_client.KustoConnectionStringBuilder")
    @patch("shared.kusto_service_client.KustoStreamingIngestClient")
    def test__init__(self, mock_kusto_streaming: Mock):
        """Test Init of Internal Kusto Client

        Args:
            mock_kusto_streaming (Mock): Mock call __get_client() that creates SDK Kusto Client
        """
        # Arrange

        kusto_client = KustoServiceClient(
            cluster_uri=self.test_cluster_uri,
            client_id="xxx-123-456",
            db_name=self.test_db_name,
            table_name=self.test_table_name,
            data_format=self.test_data_format,
        )
        # Assert
        self.assertEqual(kusto_client.table_name, self.test_table_name)
        self.assertEqual(kusto_client.db_name, self.test_db_name)
        self.assertEqual(kusto_client.data_format, self.test_data_format)
        self.assertEqual(kusto_client.cluster_uri, self.test_cluster_uri)
        mock_kusto_streaming.assert_called


    @patch("shared.kusto_service_client.KustoConnectionStringBuilder")
    def test_init_general_exception(self, auth_mock: Mock):
        # Arrange
        err_message = "Exception Error"
        auth_mock.with_aad_managed_service_identity_authentication.side_effect = Exception(err_message)
        expected_err_message: str = f"ERROR:KustoServiceClient:KustoServiceClient#get_client() Error: {err_message}"
        # Act
        with self.assertRaises(Exception) as e:
            with self.assertLogs("KustoServiceClient", level="INFO") as context:
                KustoServiceClient(
                    cluster_uri=self.test_cluster_uri,
                    client_id="xxx-123-456",
                    db_name=self.test_db_name,
                    table_name=self.test_table_name,
                    data_format=self.test_data_format,
                )

        # ASSERT
        self.assertEqual(context.output[0], expected_err_message)
        self.assertTrue(type(e.exception) in [Exception])

    @patch.object(
        KustoConnectionStringBuilder, "with_aad_managed_service_identity_authentication"
    )
    def test_init_kusto_service_error(self, auth_mock: Mock):
        # Arrange
        err_message = "KustoServiceError Error"
        auth_mock.side_effect = KustoServiceError(err_message)
        expected_err_message: str = f"ERROR:KustoServiceClient:KustoServiceError when creating Kusto Client: {err_message}"
        # Act
        with self.assertRaises(KustoServiceError) as e:
            with self.assertLogs("KustoServiceClient", level="INFO") as context:
                KustoServiceClient(
                    cluster_uri=self.test_cluster_uri,
                    client_id="xxx-123-456",
                    db_name=self.test_db_name,
                    table_name=self.test_table_name,
                    data_format=self.test_data_format,
                )
        # ASSERT
        self.assertEqual(context.output[0], expected_err_message)
        self.assertTrue(type(e.exception) in [KustoServiceError])

    @patch.object(KustoStreamingIngestClient, "ingest_from_dataframe")
    @patch(
        "shared.kusto_service_client.IngestionProperties"
    )
    def test_ingest_data_frame(
        self, mock_ingest_props: Mock, mock_external_ingest_from_data_frame: Mock
    ):
        """Test #ingest_data_frame in Internal Kusto Service that ingests a DataFrame

        Args:
            mock_ingest_props (Mock): Mock IngestionProperties azure.KUSTO SDK
            mock_external_ingest_from_data_frame (Mock): mock azure.kusto SDK Ingestion From DataFame
        """
        test_table = "testtable"
        ingestion_props = type(
            "IngestionProperties",
            (),
            {"database": "testdb", "table": test_table, "data_format": DataFormat.CSV},
        )
        mock_ingest_props.return_value = ingestion_props

        self.kusto_client.ingest_data_frame(data=self.data_frame)

        mock_external_ingest_from_data_frame.assert_called_once_with(
            df=self.data_frame, ingestion_properties=ingestion_props
        )
        assert mock_ingest_props.assert_called_once

    @patch.object(KustoStreamingIngestClient, "ingest_from_dataframe")
    def test_ingest_data_frame_kusto_service_exception(
        self, mock_external_ingest_from_data_frame: Mock
    ):
        """Test Error Responses from Ingest DataFrame

        Args:
            mock_external_ingest_from_data_frame (Mock): mock azure.kusto SDK Ingestion From DataFame
        """
        mock_external_ingest_from_data_frame.side_effect = KustoServiceError(
            "Kusto Service Error Emitted"
        )
        with self.assertRaises(KustoServiceError) as e:
            self.kusto_client.ingest_data_frame(data=pd.DataFrame({}))

        self.assertTrue(type(e.exception) in [KustoServiceError])

    @patch.object(KustoStreamingIngestClient, "ingest_from_dataframe")
    def test_ingest_data_frame_general_exception(
        self, mock_external_ingest_from_data_frame: Mock
    ):
        """Test Error Responses from Ingest DataFrame

        Args:
            mock_external_ingest_from_data_frame (Mock): mock azure.kusto SDK Ingestion From DataFame
        """
        mock_external_ingest_from_data_frame.side_effect = Exception(
            "Kusto Service Error Emitted"
        )
        with self.assertRaises(Exception) as e:
            self.kusto_client.ingest_data_frame(data=pd.DataFrame({}))

        self.assertTrue(type(e.exception) in [Exception])
