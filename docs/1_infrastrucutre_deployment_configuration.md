# Initial Setup

1. Clone the following [Project GitHub Repo](https://github.com/Azure-Samples/real-time-monitoring-and-observability-for-media) to your local repo

## Infrastructure Deployment

Infrastructure as a Code (IaC) is located under `IaC/bicep` folder and deployed using bicep CLI. To lear more about bicep see [Learn Bicep](https://learn.microsoft.com/azure/azure-resource-manager/bicep/learn-bicep)

### Prerequisites

1. Azure Subscription with Admin level access
2. Azure CLI installed locally.Required Azure CLI version 2.20.0 or later. [Install Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
3. VS Code. [Install VS Code](https://code.visualstudio.com/download)

### IaC File Structure

- `initialdeployment.bicep` - defines all the required resource for initial deployment
- `postappdeployment.bicep` - defines all the required resource for post deployment
- `main.bicep` - imports both initialdeployment and postappdeploment modules. It is an entry point for deploying resources. User will only call main.bicep with passing a condition in bicep CLI command which module to deploy. More details covered below
- `Dev.parameters.json` - Parameters file for bicep resources. User needs to specify where the resources will be deployed and resource names
- `kustotablesetup.kql` - Parameter file for creating Kusto Database Tables

#### Setup and Deploy resources

It is required to login to Azure before deploying any resources. Open up cloned project with VS Code. Open the bash terminal in VS Code and login to Azure Cloud:

1. Type `az login` to login your Azure Cloud Account.
2. Set the right Azure Subscription if you have more then one subscription.

```bash
   az account set --subscription <subscription-id>
```

#### Setup

Before deploying resources to the Azure Cloud. It is required to setup IaC and Kusto Table parameter files:

1. `/IaC/bicep/Dev.parameters.json` - fill in with your own resourceGroupName, Location, and Resource names for resource deployment
2. `/IaC/bicep/kustotablesetup.kql` - user can change the table creation based on their project needs and expected media telemetry data. Leave it as it is if deploying resources for learning purposes

#### Deploy Resources

1. Navigate to the `IaC/bicep` folder in the bash terminal. Type following az command to deploy initial resources to the Azure Cloud. This command will deploy resources to the eastus. Change it to your deployment location if it is different. `deploymentStage` will determine which bicep module to deploy in the main.bicep. It takes some time to deploy all the resources. Once the deployment is complete you can verify all the deployed resource by going to Azure Portal.

```bash
   az deployment sub create --location eastus --template-file .\main.bicep --parameters .\Dev.parameters.json deploymentStage='initialInfra'
```

2. After the Initial deployment is successful, it is required to do manual configuration in the Azure Portal.

   a. Newly created Grafana Resource requires grafana admin role access in order to access the Grafana Dashboard. Go to Azure Portal, navigate to newly created grafana resource. If you click the endpoint url, you will see page error. That is due to grafana admin role is not granted to this resource. To grant the required permission:
   - click on IAM on the left hand side
   - click add role assignment
   - search for Grafana Admin
   - select it and click Review+Assign the role.For more details on IAM see [IAM Role Assignment](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal?tabs=current)

   b. Grafana Dashboard needs to be configured with ADX in order Grafana Dashboard to pull data from ADX tables and visualize on the Dashboard.
   - Go to Grafana resource on the Azure Portal and click on endpoint url
   - Once the Grafana dashboard opens up, navigate to the settings
   - On the data source tab, search for Azure Data Explorer
   - Provide Connection details:
     - Cluster URL - To get it, got ot Azure Portal, open newly create ADX resource, and on the overview page you will see Data Ingestion URI
     - Tenant ID - Go to Azure Active Directory -> properties -> Directory ID
     - Client ID - Go to Azure Active Directory -> App Registration -> Choose your APP -> Application ID
  
***After following all the steps above you have successfully deployed initial resources and successfully configured Grafana Dashboard with ADX. You can manually insert data into existing tables in ADX and query those tables in Grafana Dashboard for testing***

#### Post App Deployment

After initial deployment and configuration. Now it is time for post deployment. Post deployment will deploy Azure Function App and Event Grid. These resources are in the post deployment because they require initial resources are deployed, configured, and running

  1. Navigate to `IaC/bicep` in the bash terminal and run the following command to deploy post deployment resources

```bash
   az deployment sub create --location eastus --template-file .\main.bicep --parameters .\Dev.parameters.json deploymentStage='postFunctionApp'
```

   2. Go to Azure Portal to see the resources are successfully deployed. Azure Function App is not configured yet with other resources such as ADX storage account and Azure Metrics Advisor in order to receive data and process. To Configure the Function App that is communicates with other resources properly see bellow required Function App configuration

### Azure Function App Configuration

- Navigate to the Azure Function App. On the left hand side panel select Settings -> Configuration. Add the bellow names with values. Once all added restart the function app
  - source_STORAGE - Your Storage Account Connection String. You can get it going into newly created Storage Account and select Access Keys from left panel in azure portal
  - MANAGED_CLIENT_ID - Your Managed Identity Client Id. You can get it going into newly created Managed Identity and select Overview from left panel in azure portal
  - KUSTO_URI - Your Azure Data Explorer Cluster URI. You can get it going into newly created Azure Data Explorer Cluster and select Overview from left panel in azure portal
  - KUSTO_DATABASE - Your Azure Data Explorer Database Name
  - SLOW_START_TABLE - Your Azure Data Explorer Table Name
  - METRICS_ADVISOR_ENDPOINT- Your Metrics Advisor Endpoint. You can get it going into newly created Metrics Advisor and select Overview from left panel in azure portal
  - METRICS_ADVISOR_SUBSCRIPTION_KEY - Your Metrics Advisor Subscription Key. You can get it going into newly created Metrics Advisor and select Keys and Endpoint from left panel in azure portal
  - METRICS_ADVISOR_API_KEY - Your Metrics Advisor API Key. Got to Metrics Advisor Workspace and select API Keys from left panel in Metrics Advisor
  - METRICS_ADVISOR_ALERT_CONFIGURATION_ID - Your Metrics Advisor Alert Configuration Id. Got to Metrics Advisor Workspace and select Alert Configurations from left panel in Metrics Advisor Alerts

***To test it simply upload `sample/test_sample.json` in to storageAccount container, you will see function app gets blob_trigger and the data from sample files will be pushed to the ADX table***

***Once all the steps above is complete, your Azure Function App is successfully configured***

***Go to the next step to setup local development environment [local development setup](/docs/2_local_development_setup.md)***
