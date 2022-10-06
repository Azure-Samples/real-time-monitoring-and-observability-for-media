import unittest

from transformations.transform import Transform
import pandas as pd


class TestTransformClass(unittest.TestCase):
    def setUp(self) -> None:
        self.table = "test_table"
        self.mappings = {
            "title": "title",
            "location.long": "location_long",
            "location.lat": "location_lat",
            "type": "type",
        }
        self.base_transform = Transform("{}", self.table, self.mappings)

    def test_class_has_attrs(self):
        """Check Transform has attribute properties"""
        attributes = [
            "json_data",
            "table",
            "mappings",
            "mapping_properties",
            "mapping_aliases",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.base_transform, attribute))

    def test_class_has_prepare_result(self):
        """Check Transform has method to get slow start"""
        self.assertTrue(callable(getattr(self.base_transform, "prepare_result", None)))

    def test_class_has_dataframe(self):
        """Check Transform has method to get slow start"""
        self.assertTrue(callable(getattr(self.base_transform, "get_dataframe", None)))

    def test_not_empty_mappings(self):
        """Check Transform has not empty filters"""
        self.assertEqual(self.base_transform.mappings, self.mappings)

    def test_not_empty_mapping_filters(self):
        """Check Transform has not empty filters"""
        self.assertTrue(len(self.base_transform.mapping_properties) > 0)
        self.assertTrue(
            self.base_transform.mapping_properties[0], list(self.mappings.keys())[0]
        )

    def test_prepare_result_returns_renamed_df(self):
        """Check if #prepare_result() returns renamed dataframe based on mappings."""
        actual_json = """[
            {
                "title": "Italian Restaurant",
                "location": {
                    "long": 188,
                    "lat": 142
                },
                "type": "Italian"
            }
        ]"""
        transform = Transform(actual_json, self.table, self.mappings)
        expected_obj = {
            "title": "Italian Restaurant",
            "location_long": 188,
            "location_lat": 142,
            "type": "Italian",
        }
        norm_df = pd.json_normalize(transform.json_data)

        df = transform.prepare_result(norm_df)

        self.assertEqual(df.values[0][0], expected_obj["title"])
        self.assertEqual(df.values[0][1], expected_obj["location_long"])
        self.assertEqual(df.values[0][2], expected_obj["location_lat"])
        self.assertEqual(df.values[0][3], expected_obj["type"])
        self.assertIsInstance(df, pd.DataFrame, "Not an instance of a DataFrame")

    def test_prepare_result_corrupted_file(self):
        """Check that corrupted file returns empty DF"""
        # Missing quotes on Italian
        actual_json = """[
            {
                "title": "Italian Restaurant",
                "location": {
                    "long": 188,
                    "lat": 142
                },
                "type": Italian
            }
        ]"""

        transform = Transform(actual_json, self.table, self.mappings)
        norm_df = pd.json_normalize(transform.json_data)

        dataframe = transform.prepare_result(norm_df)
        self.assertTrue(dataframe.empty)

    def test_prepare_result_populated_values(self):
        """Test Prepare Result Returns dataframe with missed columns filled"""
        # Missing `type` Property in JSON. Should
        actual_json = """[
            {
                "title": "Italian Restaurant",
                "location": {
                    "long": 188,
                    "lat": 142
                },
                "type": "Italian"
            }
        ]"""
        expected_obj = {
            "title": "Italian Restaurant",
            "location_long": 188,
            "location_lat": 142,
            "type": "Italian",
        }
        transform = Transform(actual_json, self.table, self.mappings)
        norm_df = pd.json_normalize(transform.json_data)
        prepared_df = transform.prepare_result(norm_df)

        self.assertEqual(prepared_df.values[0][0], expected_obj["title"])
        self.assertEqual(prepared_df.values[0][1], expected_obj["location_long"])
        self.assertEqual(prepared_df.values[0][2], expected_obj["location_lat"])
        self.assertEqual(
            prepared_df.values[0][3], expected_obj["type"], "Type Shold be Italian"
        )

    def test_prepare_result_missing_values(self):
        """Test Prepare Result Returns dataframe with missed columns filled"""
        # Missing `type` Property in JSON. Should
        actual_json = """[
            {
                "title": "Italian Restaurant",
                "location": {
                    "long": 188,
                    "lat": 142
                }
            }
        ]"""
        expected_obj = {
            "title": "Italian Restaurant",
            "location_long": 188,
            "location_lat": 142,
            "type": None,
        }

        transform = Transform(actual_json, self.table, self.mappings)
        norm_df = pd.json_normalize(transform.json_data)
        prepared_df = transform.prepare_result(norm_df)
        self.assertEqual(prepared_df.values[0][0], expected_obj["title"])
        self.assertEqual(prepared_df.values[0][1], expected_obj["location_long"])
        self.assertEqual(prepared_df.values[0][2], expected_obj["location_lat"])
        self.assertEqual(
            prepared_df.values[0][3], expected_obj["type"], "Type Should be None"
        )
