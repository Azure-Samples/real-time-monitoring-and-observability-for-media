# Initial Setup

1. Clone the following [Project GitHub Repo](https://github.com/Azure-Samples/real-time-monitoring-and-observability-for-media) to your own Azure DevOps project
1. Connect your Azure DevOps Project to Azure Subscription using [Service Connection Setup](https://learn.microsoft.com/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml)

## Infrastructure Deployment

### Infrastructure Deployment is performed in two steps

1. Step-1 - InitialInfra - This will setup initial infrastructure such as (EventGrid, App Site, Azure Data Explorer, Grafana Dashboard ...)
2. Step-2 - PostFunctionApp - This will setup infrastructure after blob processing application like Event Grid Subscription

### Infrastructure bicep code can be deployed in two ways

1. Local deployment using Azure CLI
2. Optional: Automated deployment using Azure DevOps Pipeline

- Manual Deployment

  Prerequisites

  1. Azure Subscription with the administrator level access
  2. Install Azure CLI commands on your local computer using [Install Azure CLI Instructions](https://learn.microsoft.com/cli/azure/install-azure-cli)
  3. Connect to Azure by using `az login`. If user has multiple Azure subscriptions, user needs to set right Azure subscription using bellow command:
      ```bash 
      az account set --subscription <subscription-id>
      ```
  4. Install Azure Bicep CLI using [Bicep Install Instructions](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/install)
  5. Fill in the parameters file with your own values before deployment. Path to IaC parameters file: `/IaC/bicep/Dev.parameters.json`
  6. Update kustotablesetup.kql with your own table column names and types

  Setup
  1. Perform Initial Infra setup. From command prompt, execute

     ```bash
      az deployment sub create --location eastus --template-file .\main.bicep --parameters .\Dev.parameters.json deploymentStage='initialInfra'
      ```

     - After Initial Infra setup is complete, go to azure portal. Add newley create grafana the grafana admin role at access control (IAM). When Grafana instance is created using bicep files, it will not have an admin permission which is required to be be able to access Grafana Dashboard using Grafana endpoint. [IAM Role Assignment](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal?tabs=current)
     - In the Portal. Go to the resource group you created and select Azure Managed Grafana resource. When the Initial Infra structure code is deployed, our ADX and Grafana is not automatically configured in order to Grafana Dashboard to be able to pull data from ADX. So we need to manually configure Grafana with ADX. In order to open Grafana Dashboard, select endpoint url inside the Grafana resource. It will open up Grafana Dashboard in the browser. If you get error page it means you are having admin permission issue which we covered in the previous step. On the Grafana Dashboard, go to the settings and search/add Azure Data Explorer source to your grafana dashboard. ADX will ask required credential which user can obtain all required credentials from newly created managed identity resource in the resource group.

  2. Deploy Azure Function using CI/CD Pipeline azure-depoyment-pipelines.yml. Deploy only Function_Deploy stage. See [Pipeline Setup](./2_pipelines.md)

   Step-2

  1. Perform Post Function setup. From command prompt, execute
     ```bash
     az deployment sub create --location eastus --template-file .\main.bicep --parameters .\Dev.parameters.json deploymentStage='postFunctionApp'
     ```
  2. Configure Azure Function App [Instructions](#azure-function-app-configuration)

- Optional: Azure DevOps Pipeline Deployment

  Prerequisites

  1. Create a new Azure DevOps project
  2. Create a new Azure DevOps pipeline using azure-deployment-pipelines.yml
  3. Fill in the bicep parameters file with your own values before deployment
  4. Update kustotablesetup.kql with your own table column names and types

  Setup

  1. Define variables `azureSubscription, azureServiceConnection, functionAppName` to your pipeline. See [YAML Pipeline Editor UI](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/yaml-pipeline-editor?view=azure-devops)
     - azureSubscription - Your Subscription Id
     - azureServiceConnection - Your service connection name. See [Service Connection Setup](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml)
     - functionAppName - Your function app name from initial infra deployment
  2. Run the pipeline. See [Pipeline Setup](./3_pipelines.md)
  3. Add Grafana Admin Access Control (IAM) to newly created grafana dashboard. See [IAM Role Assignment](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal?tabs=current)
  4. Configure Azure Function App [Instructions](#azure-function-app-configuration)

### Azure Function App Configuration

- See [Azure Function App Configuration](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings?tabs=portal)

- Ensure following values are added into function app settings in the portal
  - source_STORAGE - Your Storage Account Connection String. You can get it going into newly created Storage Account and select Access Keys from left panel in azure portal
  - MANAGED_CLIENT_ID - Your Managed Identity Client Id. You can get it going into newly created Managed Identity and select Overview from left panel in azure portal
  - KUSTO_URI - Your Azure Data Explorer Cluster URI. You can get it going into newly created Azure Data Explorer Cluster and select Overview from left panel in azure portal
  - KUSTO_DATABASE - Your Azure Data Explorer Database Name
  - SLOW_START_TABLE - Your Azure Data Explorer Table Name
  - METRICS_ADVISOR_ENDPOINT- Your Metrics Advisor Endpoint. You can get it going into newly created Metrics Advisor and select Overview from left panel in azure portal
  - METRICS_ADVISOR_SUBSCRIPTION_KEY - Your Metrics Advisor Subscription Key. You can get it going into newly created Metrics Advisor and select Keys and Endpoint from left panel in azure portal
  - METRICS_ADVISOR_API_KEY - Your Metrics Advisor API Key. Got to Metrics Advisor Workspace and select API Keys from left panel in Metrics Advisor
  - METRICS_ADVISOR_ALERT_CONFIGURATION_ID - Your Metrics Advisor Alert Configuration Id. Got to Metrics Advisor Workspace and select Alert Configurations from left panel in Metrics Advisor Alerts
