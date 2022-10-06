# Function Triggers

This repo contains 3 types of function triggers to demonstrate the different ways of Triggering data transformations from a Blob Storage and ingestion into an Azure Data Explorer Kusto Cluster.

## Types of Triggers

**Blob Trigger** - Execute the Function when a blob is created / deleted in the specified storage account. [Blob Trigger for Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger?tabs=in-process%2Cextensionv5&pivots=programming-language-python)

**Event Grid Trigger** - Execute the Function by responding to an event sent to an event grid topic. [Event Grid Triggers for Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid-trigger?tabs=in-process%2Cextensionv3&pivots=programming-language-python)

**HTTP Trigger** - Execute Azure function on an HTTP Request. [HTTP Trigger for Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger?tabs=in-process%2Cfunctionsv2&pivots=programming-language-python)

**Metrics Advisor HTTP Hook Trigger** - Additionally we have another HTTP trigger that handles the Metrics Advisor Webhook alerts and sends the data into ADX alert table