import logging

import azure.functions as func
from shared.transform_handler import TransformHandler

logger = logging.getLogger("EventGridInit")


def main(event: func.EventGridEvent, blobInput: func.InputStream):
    """Event Grid Trigger function that ingests manipulated data from Blob Storage
    to Azure Data Explorer

    Args:
        event (func.EventGridEvent): Event Grid Event Message
        blobInput (str): created blob from Storage Account
    """

    logger.info("Event Grid Trigger Function Starting")

    handler = TransformHandler(blob_input=blobInput)
    handler.handle_transform_request()

    logger.info("Event Grid Trigger Function Completing")
