import unittest

from transformations.slow_start_transform import SlowStartTransform
from utils.settings import SLOW_START_TABLE

JSON_DATA = """
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


class TestSlowStartTransformClass(unittest.TestCase):
    def test_has_get_dataframe(self):
        """Check Transform has #get_dataframe"""
        slow_start_transform = SlowStartTransform("{}")
        self.assertTrue(callable(getattr(slow_start_transform, "get_dataframe", None)))

    def test_has_mappings_set(self):
        """Check SlowStartTransform has mappings property set from Transform Parent Class"""
        slow_start_transform = SlowStartTransform("{}")
        self.assertTrue(hasattr(slow_start_transform, "mappings"))
        self.assertEqual(
            slow_start_transform.mappings,
            slow_start_transform.video_slow_start_mappings,
        )

    def test_has_table_set(self):
        """Check SlowStartTransform has table property set from Transform Parent Class"""
        slow_start_transform = SlowStartTransform("{}")
        self.assertTrue(hasattr(slow_start_transform, "table"))
        self.assertEqual(slow_start_transform.table, SLOW_START_TABLE)

    def test_get_dataframe(self):
        """Test #getdataframe returns a filtered Dataframe"""

        slow_start_transform = SlowStartTransform(JSON_DATA)
        expected_dict = {
            "user_details_content_session_id": "bf8bd09d-8536-4aab-8f20-aba913e62f9b",
            "user_details_app_session_id": "4e39a6f4-4f2a-42d5-acba-7aa1df78145f",
            "measurement_startup_duration_content_ms": "",
            "dimension_browser_name": "Chrome",
            "dimension_os_name": "Mac OS X",
            "dimension_country_code": "United States",
            "dimension_city": "Bristol",
            "dimension_asn": "AS7922 Comcast Cable Communications, LLC",
            "timestamp": "2022-05-31T15:52:40.0000251Z",
        }

        actual_df = slow_start_transform.get_dataframe()
        self.assertEqual(
            actual_df.values[0][0], expected_dict["user_details_content_session_id"]
        )
        self.assertEqual(
            actual_df.values[0][-1], expected_dict["timestamp"]
        )

    def test_get_empty_dataframe_bad_json(self):
        """Test #getdataframe returns a filtered Dataframe"""

        # event_id missing quote
        bad_json = """
        {
            "event_id: "4e39a6f4-4f2a-42d5-acba-7aa1df78145f_00.00006",
            "event": {
                "type": "playback_start",
                "timestamp": 1654012360251,
                "attributes": {
                "startup_duration_content_ms": 1344,
                "startup_duration_total_ms": 1344
                },
                "formatted_timestamp": "2022-05-31T15:52:40.0000251Z"
            },
        }
        """
        slow_start_transform = SlowStartTransform(bad_json)
        actual_df = slow_start_transform.get_dataframe()
        self.assertTrue(actual_df.empty)
