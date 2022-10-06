import logging
import json
from typing import List
import pandas as pd
from azure.kusto.data.data_format import DataFormat
from .kusto_service_client import KustoServiceClient
from .metrics_advisor_client import MetricsAdvisorAPIClient

logger = logging.getLogger("HookHandler")

class HookHandler:
    """
        Hook handler
        config = {
            "kusto_metrics_advisor_anomaly_alerts_table": "",
            "kusto_cluster_uri": "",
            "kusto_db_name": "",
            "managed_client_id": "",
            "metrics_advisor_subscription_key": "",
            "metrics_advisor_api_key": "",
            "metrics_advisor_endpoint": ""
        }
    """
    loaded_feeds = {}

    """Instance of the MA api client"""
    metrics_advisor_api_client = {}

    # Db Schema
    schema = [
        "incident_id",
        "alert_id",
        "severity",
        "data_feed_id",
        "data_feed_name",
        "actual_value",
        "expected_value",
        "dimension",
        "timestamp"
    ]

    def __init__(self, config={}):
        """Constructor"""
        self.__check_configs(config)
        self.config = config

    def __check_configs(self, config: dict):
        """Check if env was set properly
    
        Args:
            config (dict): env configuration

        Raises:
            Exception: Env not set error
        """
        empty_envs = []
        for config_item in config:
            if not config[config_item]:
                empty_envs.append(config_item)
        if empty_envs:
            raise Exception(
                "Env setup error, please check this env variables: " + ", ".join(empty_envs))

    def __get_metrics_advisor_api_client(self) -> MetricsAdvisorAPIClient:
        """get Metrics Advisor API client

        Returns:
            MetricsAdvisorAPIClient: MetricsAdvisorAPIClient
        """
        return MetricsAdvisorAPIClient(
            self.config["metrics_advisor_subscription_key"],
            self.config["metrics_advisor_api_key"],
            self.config["metrics_advisor_endpoint"]
        )

    def __get_kusto_client(self) -> KustoServiceClient:
        """Get Kusto client

        Returns:
            KustoServiceClient: KustoServiceClient
        """
        return KustoServiceClient(
            cluster_uri=self.config["kusto_cluster_uri"],
            client_id=self.config["managed_client_id"],
            db_name=self.config["kusto_db_name"],
            table_name=self.config["kusto_metrics_advisor_anomaly_alerts_table"],
            data_format=DataFormat.CSV
        )

    def handle(self, decoded_hook_data: str) -> None:
        """Handle hook data

        Args:
            decoded_hook_data (str): String with JSON from hook
        """
        loaded_json = MetricsAdvisorAPIClient.load_json(decoded_hook_data)
    
        normalised_df = pd.json_normalize(loaded_json)
        prepared_df = self.__prepare_incidents_df(normalised_df)
        
        self.__store(prepared_df)

    def __load_incidents(self, incidentUrl: str) -> List:
        """Load incidents

        Args:
            incidentUrl (str): alert id

        Returns:
            List: list of dict
        """
        return self.metrics_advisor_api_client.get_incidents_by_incident_id(incidentUrl)

    def __store(self, prepared_df: pd.DataFrame()) -> None:
        """Store incident

        Args:
            prepared_df (pd.DataFrame): Dataframe
        """
        if prepared_df.empty:
            logger.error("DataFrame is empty, nothing to store")
            return

        self.__get_kusto_client().ingest_data_frame(prepared_df)

        logger.info("Function ingests %s rows" % str(len(prepared_df.index)))

    def __prepare_incidents_df(self, normalised_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare incidents dataframe

        Args:
            normalised_df (pd.DataFrame): DataFrame

        Returns:
            pd.DataFrame: DataFrame
        """
        data_for_df = []
        
        if not normalised_df.empty:
            logger.info('__prepare_incidents_df() - normalized df column values ' + str(normalised_df.columns.to_list()))
            
            # iterate alerts
            for index, alert in normalised_df.iterrows():
                
                if hasattr(alert, 'alertInfo.anomalyAlertingConfigurationId') and hasattr(alert, 'callBackUrl'):
                    self.metrics_advisor_api_client = self.__get_metrics_advisor_api_client()
                    alert_id = alert["alertInfo.alertId"]
                    
                    for incident in self.__load_incidents(alert["callBackUrl"]):
                        logger.info("__prepare_incidents_df() : getting incident value from __load_incident " + str(incident))
                        data_feed_id = incident["dataFeedId"]
                        data_for_df.append(
                            [
                                incident["incidentId"],
                                alert_id,
                                self.__get_incident_property(
                                    incident, "maxSeverity"),
                                data_feed_id,
                                self.__get_feed_name(data_feed_id),
                                round(self.__get_incident_property(
                                    incident, "valueOfRootNode")),
                                round(self.__get_incident_property(
                                    incident, "expectedValueOfRootNode")),
                                self.__get_incident_dimension(incident),
                                alert["alertInfo.timestamp"]
                            ]
                        )

        # Create the pandas DataFrame
        return pd.DataFrame(data_for_df, columns=self.schema)

    def __get_incident_property(self, incident: dict, sudproperty: str) -> str:
        """Get incident field

        Args:
            incident (dict): Incident
            sudproperty (str): subproperty

        Returns:
            str: Incident field
        """
        if "property" in incident and sudproperty in incident["property"]:
            return incident["property"][sudproperty]

        return ""
    
    def __get_incident_dimension(self, incident: dict) -> str: 
        """Get incident dimensions

        Args:
            incident (dict): incident
            subproperty (str): dimenion_subproperty

        Returns:
            string: incident dimension value
        """
        
        if "rootNode" in incident and "dimension" in incident['rootNode']:
            return json.dumps(incident['rootNode']['dimension'])
    
        return ""
        

    def __get_feed_name(self, data_feed_id: str) -> str:
        """Get feed name
        Cached in local variable

        Args:
            data_feed_id (str): Data feed id

        Returns:
            str: feed name
        """
        if data_feed_id not in self.loaded_feeds.keys():
            self.loaded_feeds[data_feed_id] = self.metrics_advisor_api_client \
                .get_data_feed_name_by_id(data_feed_id)

        return self.loaded_feeds[data_feed_id]
