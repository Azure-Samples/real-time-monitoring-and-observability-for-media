# Local Development Setup

Follow the steps below to setup the local environment for development.

## Prerequisites

- Azure Subscription
- [python](https://www.python.org/downloads/release/python-3913/) version 3.9

Optional:

- [Visual Studio Code](https://code.visualstudio.com/download)
- VSCode Extensions ([Managing Extensions](https://code.visualstudio.com/docs/editor/extension-marketplace)):
  - `ms-azuretools.vscode-azurefunctions`
  - `ms-python.python`
- [docker](https://docs.docker.com/get-docker/) (If wanting to use Megalinter container)

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Common Configuration

> Set the listed env vars in the table below in a `functions/local.settings.json` file.

```bash
touch functions/local.settings.json
```

| Name                                     | Example Value                                                                                                     | Description                                                                                                                             |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `FUNCTIONS_WORKER_RUNTIME`               | python                                                                                                            | The runtime of the Azure Functions                                                                                                      |
| `AzureWebJobsStorage`                    | `DefaultEndpointsProtocol=https;AccountName=<storage_acct>;AccountKey=xx-xx-xx==;EndpointSuffix=core.windows.net` | Storage Account connection string for Azure Web Jobs used by Functions                                                                  |
| `datazoom_STORAGE`                       | `DefaultEndpointsProtocol=https;AccountName=<storage_acct>;AccountKey=xx-xx-xx==;EndpointSuffix=core.windows.net` | Storage Account connection string for Input blobs                                                                                       |
| `MANAGED_CLIENT_ID`                      | `XXX-XXX-XXX`                                                                                                     | Azure Managed Service Identity Client ID                                                                                                |
| `KUSTO_URI`                              | `https://<data_explorer_resource_name>.<region>.kusto.windows.net"`                                               | Azure Data Explorer Kusto Cluster Resource URI.                                                                                        |
| `KUSTO_DATABASE`                         | `testdata`                                                                                                        | The name of the targeted Kusto Database                                                                                                 |
| `SLOW_START_TABLE`                       | `slow_start_anomaly_detection`                                                                                    | Slow Start Anomaly Detection Table                                                                                                      |
| `METRICS_ADVISOR_ENDPOINT`               | `https://name-metricsadvisor.cognitiveservices.azure.com/`                                                        | Metrics Advisor Endpoint                                                                                                               |
| `METRICS_ADVISOR_SUBSCRIPTION_KEY`       | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`                                                                                | The subscription key to your Metrics Advisor. Can be found in Keys and Endpoint section of metrics advisor resource in the Azure portal |
| `METRICS_ADVISOR_API_KEY`                | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`                                                                            | Metrics Advisor API Key. Can be found in Azure Metics Advisor Workspace                                                                |
| `METRICS_ADVISOR_ALERT_CONFIGURATION_ID` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`                                                                            | Metrics Advisor configuration ID. Can be found in Azure Metics Advisor Workspace                                                       |

## Development

### Running Azure Functions

To run the Azure Functions locally, follow this guide: [Develop and Code Azure Functions Locally](https://learn.microsoft.com/azure/azure-functions/functions-develop-local)

### Extending Data Transformations

This project allows for extending the `Data Transformation` logic into more custom logic that fits your use case.

This doc will walk you through how to extend the Transformation and add custom logic and scripts: [Develop Custom Data Transformations](./4_extending_transformation_logic.md)

### Linting

The linter used is the [Megalinter](https://oxsecurity.github.io/megalinter/latest/)

To use locally, follow this guide: [Using Megalinter Locally](https://oxsecurity.github.io/megalinter/latest/mega-linter-runner/)

## Deployment

There are a few ways to deploy Azure Functions.

1. Deploy through [VSCode](https://learn.microsoft.com/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level#publishing-to-azure)
2. Deploy via [Azure CLI](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-python?tabs=azure-cli%2Cbash%2Cbrowser#create-supporting-azure-resources-for-your-function)

***Go to the next step to change the data transformation logic based on your project needs. [Extending and Customizing Transformation Logic](/docs/3_extending_transformation_logic.md)***
