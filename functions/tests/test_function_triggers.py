import json
import os
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import azure.functions as func
from blob_storage_trigger import main as blob_main
from event_grid_trigger import main as event_main
from http_trigger import main as http_main

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
    },
}
"""


class TestFunctionTriggers(unittest.TestCase):
    def setUp(self) -> None:
        self.event = func.EventGridEvent(
            id="8e3ba80a-701e-001e-3c9a-8282ce06afad",
            data={"api": "PutBlob", "blobType": "BlockBlob"},
            event_type="Microsoft.Storage.BlobCreated",
            topic="/storageaccount",
            subject="/xyz.json",
            event_time=datetime.now(),
            data_version="0.1",
        )
        self.req = func.HttpRequest("get", "https://sample_url.com", body=None)
        self.blob_input = func.blob.InputStream(
            data=BLOB_DATA.encode("utf-8"), name="sample_data.json"
        )

    @patch("event_grid_trigger.TransformHandler")
    def test_event_grid_trigger_main(
        self,
        mock_transform_handler: Mock,
    ):
        """Test Event Trigger is executed correctly"""
        mock_transform_handler_instance = mock_transform_handler.return_value
        # Act
        event_main(event=self.event, blobInput=self.blob_input)
        mock_transform_handler.assert_called_once_with(blob_input=self.blob_input)
        mock_transform_handler_instance.handle_transform_request.assert_called_once()

    @patch("blob_storage_trigger.TransformHandler")
    def test_blob_trigger_main(
        self,
        mock_transform_handler: Mock,
    ):
        """Test Blob Trigger is executed correctly"""
        mock_transform_handler_instance = mock_transform_handler.return_value
        # Act
        blob_main(blobInput=self.blob_input)
        mock_transform_handler.assert_called_once_with(blob_input=self.blob_input)
        mock_transform_handler_instance.handle_transform_request.assert_called_once()

    @patch("http_trigger.TransformHandler")
    def test_http_trigger_main(
        self,
        mock_transform_handler: Mock,
    ):
        """Test Blob Trigger is executed correctly"""
        mock_transform_handler_instance = mock_transform_handler.return_value
        # Act
        http_main(req=self.req, blobInput=self.blob_input)
        mock_transform_handler.assert_called_once_with(blob_input=self.blob_input)
        mock_transform_handler_instance.handle_transform_request.assert_called_once()
