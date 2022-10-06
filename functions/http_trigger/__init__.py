import logging

import azure.functions as func
from shared.transform_handler import TransformHandler

logger = logging.getLogger("HTTPTriggerInit")


def main(req: func.HttpRequest, blobInput: func.InputStream) -> func.HttpResponse:
    """HTTP Trigger function that ingests manipulated data from Blob Storage
    to Azure Data Explorer

    Args:
        req (func.HttpRequest): HTTP Request object.
        blobInput (str): created blob from Storage Account

    Returns:
        func.HttpResponse: Returns an HTTP Response Object
    """

    logger.info("HTTP Trigger Function Starting")

    handler = TransformHandler(blob_input=blobInput)
    handler.handle_transform_request()

    logger.info("HTTP Trigger Function Completing")

    return func.HttpResponse(f"HTTP triggered function executed successfully.")
