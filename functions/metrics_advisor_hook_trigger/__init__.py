import logging
import os
import azure.functions as func
from shared.metrics_advisor_hook_handler import HookHandler

config = {
    "kusto_metrics_advisor_anomaly_alerts_table": os.getenv("KUSTO_METRICS_ADVISOR_ANOMALY_ALERTS_TABLE"),
    "kusto_cluster_uri": os.getenv("KUSTO_URI"),
    "kusto_db_name": os.getenv("KUSTO_DATABASE"),
    "managed_client_id": os.getenv("MANAGED_CLIENT_ID"),
    # The subscription key to your Metrics Advisor resource. You can find this in the Keys
    # and Endpoint section of your resource in the Azure portal
    "metrics_advisor_subscription_key": os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY"),
    # The API key for your Metrics Advisor instance. You can find this in the web portal
    # for Metrics Advisor, in API keys on the left navigation menu.
    "metrics_advisor_api_key": os.getenv("METRICS_ADVISOR_API_KEY"),
    "metrics_advisor_endpoint": os.getenv("METRICS_ADVISOR_ENDPOINT", "")
}


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Metrics Advisor hook handler function to receive alerts from Metrics Advisor
    and ingest the data into Azure Data Explorer Alert table

    Args:
        req (func.HttpRequest): HttpRequest

    Returns:
        func.HttpResponse: HttpResponse
    """
    decoded_hook_data = req.get_body().decode("utf-8")
    logger.info("Alert Raw Data " + decoded_hook_data)    

    app = HookHandler(config)
    app.handle(decoded_hook_data)

    return func.HttpResponse(f"Success")
