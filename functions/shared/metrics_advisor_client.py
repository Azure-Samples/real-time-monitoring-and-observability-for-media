import logging
import json
import string
from typing import List
import http.client

logger = logging.getLogger("MetricsAdvisorAPIClient")


class MetricsAdvisorAPIClient:
    metrics_advisor_subscription_key = ""
    metrics_advisor_api_key = ""
    metrics_advisor_endpoint = ""

    def __init__(
        self,
        metrics_advisor_subscription_key: str,
        metrics_advisor_api_key: str,
        metrics_advisor_endpoint: str
    ):
        """Constructor

        Args:
            metrics_advisor_subscription_key (string): metrics advisor subscription key
            metrics_advisor_api_key (string): metrics advisor api key
            metrics_advisor_endpoint (string): metrics advisor endpoint
        """
        self.metrics_advisor_subscription_key = metrics_advisor_subscription_key
        self.metrics_advisor_api_key = metrics_advisor_api_key
        self.metrics_advisor_endpoint = metrics_advisor_endpoint

    def __init_connection(self) -> http.client.HTTPSConnection:
        """Create https API connection

        Returns:
            http.client.HTTPSConnection: _description_
        """
        return http.client.HTTPSConnection(
            self.metrics_advisor_endpoint.replace("https://", ""))

    def __get_headers(self) -> dict:
        """Get headers

        Returns:
            dict: headers
        """
        return {
            'Ocp-Apim-Subscription-Key': self.metrics_advisor_subscription_key,
            'x-api-key': self.metrics_advisor_api_key
        }

    def get_incidents_by_incident_id(self, incidentUrl: str) -> List:
        """Load incidents from API

        Args:
            incidentUrl (str): Alert id

        Returns:
            List: list of dict
        """
        try:
            connection = self.__init_connection()
            connection.request(
                "GET",
                incidentUrl,
                "",
                self.__get_headers()
            )

            response = connection.getresponse()
            data = response.read()
            connection.close()

            responce_json = self.load_json(data)
            
            logger.info("Reponse json from callback " + str(responce_json))

            if "code" in responce_json and responce_json['code'] == "Not Found":
                logger.error("Incidents not found. " + str(responce_json))
                return self.load_json('{}')
            return self.load_json(data)
        except Exception as e:
            logger.error(
                f"MetricsAdvisorClientError when getting incidents list by the incidentUrl {incidentUrl}: {e}")
            raise e

    def get_data_feed_name_by_id(self, data_feed_id: str) -> str:
        """Load data feed name from API

        Args:
            data_feed_id (str): data feed id

        Returns:
            str: data feed name
        """
        try:
            connection = self.__init_connection()
            connection.request(
                "GET",
                self.__get_data_feed_url(data_feed_id),
                "",
                self.__get_headers()
            )
            response = connection.getresponse()
            data = response.read()
            connection.close()

            result = self.load_json(data)

            if "dataFeedName" in result:
                return result["dataFeedName"]

            return ""
        except Exception as e:
            logger.error(
                f"MetricsAdvisorClientError when getting data feed by id {data_feed_id}: {e}")
            raise e

    def __get_data_feed_url(self, data_feed_id: str) -> str:
        """Get incidents url

        Args:
            data_feed_id (str): data feed id

        Returns:
            str: url string
        """
        return "/metricsadvisor/v1.0/dataFeeds/%s" % data_feed_id

    @staticmethod
    def load_json(data: string) -> List:
        """Load raw data

        Args:
            data (string): Receiving raw data as a POST request and loading as a json

        Returns:
            List
        """
        try:
            json_data = json.loads(data)

            if 'value' in json_data:
                return json_data['value']
            return json_data
        except json.decoder.JSONDecodeError as e:
            logger.error(f"Load Json Error: {e}")
            raise e
