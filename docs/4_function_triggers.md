# Function Trigger Types

This repo contains 4 types of function triggers to demonstrate the different ways of triggering data transformations and ingestion into an Azure Data Explorer Kusto Cluster.

## Types of Triggers

- **Blob Trigger** - Execute the Function when a blob is created / deleted in the specified storage account. [Blob Trigger for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-blob-trigger?tabs=in-process%2Cextensionv5&pivots=programming-language-python)

- **Event Grid Trigger** - Execute the Function by responding to an event sent to an event grid topic. [Event Grid Triggers for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-bindings-event-grid-trigger?tabs=in-process%2Cextensionv3&pivots=programming-language-python)

- **HTTP Trigger** - Execute the Function on an HTTP Request. [HTTP Trigger for Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-bindings-http-webhook-trigger?tabs=in-process%2Cfunctionsv2&pivots=programming-language-python)

- **Metrics Advisor HTTP Hook Trigger** - Execute the Function on Metrics Advisor Webhook alerts and push the data into ADX alert table.

***To test it simply upload `sample/test_sample.json` in to storageAccount container, you will see function app gets blob_trigger and the data from sample files will be pushed to the ADX table***

***Go to the next step to setup metrics advisor and metrics advisor hook alerts. [Metrics Advisor Setup](docs/../5_metrics_advisor_setup.md)***
