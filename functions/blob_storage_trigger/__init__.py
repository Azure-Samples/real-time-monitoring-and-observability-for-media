import logging

import azure.functions as func
from shared.transform_handler import TransformHandler

logger = logging.getLogger("BlobTriggerInit")


def main(blobInput: func.InputStream):
    """Blob Trigger function that ingests manipulated data from Blob Storage
    to Azure Data Explorer

    Args:
        blobInput (str): created blob from Storage Account
    """
    logger.info("Blob Trigger Function Starting")

    handler = TransformHandler(blob_input=blobInput)
    handler.handle_transform_request()

    logger.info("Blob Trigger Function Completing")
