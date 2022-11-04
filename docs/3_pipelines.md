# Pipelines

This doc will cover the pipelines found in this Repo.

There are 2 Pipelines found in this Project:

- The CI Pipeline: [.azure-pipelines.yml](../.azure-pipelines.yml)
- The Azure Infrastructure and Function Deployment Pipeline: [azure-deploy-pipelines.yml](../azure-deploy-pipelines.yml)

## CI Pipeline

The CI Pipeline is used for checking the quality of code and ensure that new code added adhere to tests to improve maintainability.

### CI Pipeline Trigger

The Pipeline will trigger on Pull Requests made to `main` branch

### CI Pipeline Notable Details

[Megalinter](https://oxsecurity.github.io/megalinter/) is used for the `linting` job as the primary tool for linting code. Megalinter identifies updated code in PR and will run the corresponding linters.

### CI Pipeline Variables

`MEGALINTER_IMAGE` - defines which docker image to use for the Megalinter

- `MEGALINTER_IMAGE: megalinter/megalinter-documentation:v5.12.0`

### CI Pipeline Composition

The Pipeline is comprised of the following:

- 2 Jobs
  - Linting Job
    - 1 Step
      - MegaLinter Step
  - Testing Job
    - 4 Steps
      - Set Python Version to `3.9`
      - `pip install` packages
      - `pytest` step
      - Publish Testing Results Step

## Deployment Pipeline

The Deployment Pipeline is used for deploying the **Azure Infrastructure** and **Azure Function** based on latest code changes in `main` branch. This pipeline will build the Azure Function and deploy it to a Remote Azure Function App within an Azure Subscription.

For this pipeline to function, there are a set of variables that need to be set in Azure DevOps for this Pipeline to work correctly. For a list of Necessary Variables to be instantiated, refer to [Deployment Pipeline Variables](#deployment-pipeline-variables).

### Deployment Pipeline Trigger

This Pipeline has no trigger, and requires **manual** action to trigger the Azure Functions build and deploy.

### Deployment Pipeline Notable Details

This pipeline has the following **Prerequisite**:

- Existing [Azure Function App](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings?tabs=portal)

The Deployment Process consists of building a `.zip` out fo the Function App, archiving it as an Artifact, and then using that Artifact in the latter `deploy` Stage to deploy the Function App.

### Deployment Pipeline Variables

There are 3 environment variables that must be set for the Azure Pipelines, `azureSubscription`, `azureServiceConnection` and `functionAppName`.

`functionAppName` - The Name of the existing Azure Function App.
`azureSubscription` - The Name of the Azure Subscription where the Function App is located.
`azureServiceConnection` - The Name of the Azure Service Connection that has access to the Azure Subscription. [Service Connection Setup](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml)

To set these variables, you can refer to [Azure Pipelines Variables Documentation](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops&tabs=yaml%2Cbatch)

### Deployment Pipeline Composition

1. Build Stage

- 1 Job
  - Build Job - Build Files
    - 5 Steps
    - Build Extensions
    - Use `python v3.9`
    - Install Python Dependencies
    - Archive Build Files to `.zip`
    - Publish Archived `.zip` as Artifact for use in Deploy Stage

2. Initial Infra Deployment Stage

- 1 job
  - Deploy Infrastructure Job
    - 1 Step
      - Deploy Infrastructure Step
        - AzureSubscription - use `azureServiceConnection` variable

3. Deploy Stage

- 1 Job
  - Deploy Job
    - 2 Steps
      - Download `.zip` Artifact
      - Deploy `.zip` to Azure Function App using `azureSubscription` and `functionAppName` variables

4. Post Deployment Stage

- 1 Job
  - Post Deployment Job
    - 1 Step
      - Post Deployment Step
        - AzureSubscription - use `azureServiceConnection` variable


### If initial and post infrastrucutre deployment steps are not needed or deployed manually, comment out step 2 and 4 in the pipeline and run steps 1 and 3 for azure function deployment
