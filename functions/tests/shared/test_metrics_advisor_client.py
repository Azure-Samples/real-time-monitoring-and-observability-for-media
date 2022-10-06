import unittest
from unittest.mock import patch

from shared.metrics_advisor_client import MetricsAdvisorAPIClient

metrics_advisor_subscription_key = "subscription_key"
metrics_advisor_api_key = "api_key"
metrics_advisor_endpoint = "endpoint"

class TestMetricsAdvisorAPI(unittest.TestCase):
    def test_get_headers(self):
        """Test to get headers"""
        client = self.get_client()

        headers = client._MetricsAdvisorAPIClient__get_headers()
        self.assertEqual(
            headers,
            {
                'Ocp-Apim-Subscription-Key': metrics_advisor_subscription_key,
                'x-api-key': metrics_advisor_api_key
            }
        )

    def test_get_data_feed_url(self):
        """Test to get incidents URL"""
        client = self.get_client()

        self.assertEqual(
            len(client._MetricsAdvisorAPIClient__get_data_feed_url("dd")),
            33
        )

    def get_client(self) -> MetricsAdvisorAPIClient:
        """get MetricsAdvisorAPIClient instance

        Returns:
            MetricsAdvisorAPIClient: MetricsAdvisorAPIClient
        """
        return MetricsAdvisorAPIClient(
            metrics_advisor_subscription_key,
            metrics_advisor_api_key,
            metrics_advisor_endpoint
        )