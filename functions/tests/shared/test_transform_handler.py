import unittest
from unittest.mock import patch

import azure.functions as func
import pandas as pd
from shared.transform_handler import TransformHandler

BLOB_DATA = """
{
    "event_id": "4e39a6f4-4f2a-42d5-acba-7aa1df78145f_00.00006",
    "event": {
        "type": "playback_start",
        "timestamp": 1654012360251,
        "attributes": {
        "startup_duration_content_ms": 1344,
        "startup_duration_total_ms": 1344
        },
        "formatted_timestamp": "2022-05-31T15:52:40.0000251Z"
    },
    "user_details": {
        "app_session_id": "4e39a6f4-4f2a-42d5-acba-7aa1df78145f",
        "app_session_start_ts_ms": 1654012358444,
        "content_session_id": "bf8bd09d-8536-4aab-8f20-aba913e62f9b",
        "client_ip": "73.238.60.7",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    },
    "device": {
        "browser_name": "Chrome",
        "device_id": "1e545916-70ba-4d0e-ac01-e189737dcfb2",
        "browser_width": 1658,
        "os_name": "Mac OS X",
        "device_type": "pc",
        "browser_version": "101.0.4951.64",
        "browser_height": 927
    },
    "geo_location": {
        "country": "United States",
        "country_code": "US",
        "city": "Bristol",
        "latitude": 41.6853,
        "region": "Connecticut",
        "postal_code": "06010",
        "longitude": -72.9296,
        "region_code": "CT"
    },
    "network": {
        "asn_org": "Comcast IP Services, L.L.C.",
        "isp": "Comcast Cable Communications",
        "asn": "AS7922 Comcast Cable Communications, LLC"
    }
}
"""


class TestTransformHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.blob_input = func.blob.InputStream(
            data=BLOB_DATA.encode("utf-8"), name="sample_data.json"
        )

        self.table_name = "fake_table"
        self.data_frame = pd.DataFrame({"a": [1, 2, 3, 4, 5]})

    @patch("shared.transform_handler.KustoServiceClient")
    @patch("transformations.index.SlowStartTransform")
    def test_handle_transform_request(self, mock_transformation, mock_kusto_service):
        """Test Get JSON String from Input Stream."""
        instance = mock_transformation.return_value
        instance.table = self.table_name
        instance.get_dataframe.return_value = self.data_frame

        expected_logs = [
            f"INFO:TransformHandler:Ingested Frames to Table: {self.table_name}",
            "INFO:TransformHandler:Azure Function Completed",
        ]

        with self.assertLogs("TransformHandler", level="DEBUG") as context:
            transform_handler = TransformHandler(blob_input=self.blob_input)
            transform_handler.handle_transform_request()
        self.assertEqual(mock_transformation.call_count, 1)
        self.assertEqual(mock_kusto_service.call_count, 1)
        # make sure JSON string is converting correctly
        self.assertEqual(context.output, expected_logs)
        self.assertEqual(transform_handler.json_string, BLOB_DATA)

    @patch("shared.transform_handler.KustoServiceClient")
    @patch("transformations.index.SlowStartTransform")
    def test_frame_empty_frame(self, mock_transformation, mock_kusto_service):
        """Test Get JSON String from Input Stream."""
        instance = mock_transformation.return_value
        instance.table = self.table_name
        instance.get_dataframe.return_value = pd.DataFrame({})

        expected_logs = [
            f"DEBUG:TransformHandler:Frame is Empty or Table is not defined. Continuing",
            "INFO:TransformHandler:Azure Function Completed",
        ]

        with self.assertLogs("TransformHandler", level="DEBUG") as context:
            transform_handler = TransformHandler(blob_input=self.blob_input)
            transform_handler.handle_transform_request()
        # make sure JSON string is converting correctly
        self.assertEqual(context.output, expected_logs)
        self.assertEqual(mock_transformation.call_count, 1)
        mock_kusto_service.assert_not_called()

    @patch("shared.transform_handler.KustoServiceClient")
    @patch("transformations.index.SlowStartTransform")
    def test_table_name_undefined(self, mock_transformation, mock_kusto_service):
        """Test Get JSON String from Input Stream."""

        empty_table_name = ""
        instance = mock_transformation.return_value
        instance.table = empty_table_name
        instance.get_dataframe.return_value = self.data_frame

        expected_logs = [
            f"DEBUG:TransformHandler:Frame is Empty or Table is not defined. Continuing",
            "INFO:TransformHandler:Azure Function Completed",
        ]

        with self.assertLogs("TransformHandler", level="DEBUG") as context:
            transform_handler = TransformHandler(blob_input=self.blob_input)
            transform_handler.handle_transform_request()
        # make sure JSON string is converting correctly
        self.assertEqual(context.output, expected_logs)
        self.assertEqual(mock_transformation.call_count, 1)
        mock_kusto_service.assert_not_called()
