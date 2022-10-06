targetScope='subscription'
param resourceGroupName string
param resourceGroupLocation string
param grafanaDashboardName string
param eventgridProcessingFunctionName string = ''

@allowed([
  'initialInfra'
  'postFunctionApp'
  'noOp'
])
@description('Provide which step of Infra deployment to perform. initialInfra= setup of initial infra. postFunctionApp= perform post function setup such as event grid subscription. noOp= do nothing.')
param deploymentStage string = 'noOp'

@minLength(3)
@maxLength(24)
@description('Provide a name for the external storage account. Use only alphanumeric characters. The name must be unique across Azure.')
param blobStorageName string = ''

@allowed([
  'new'
  'existing'
])
param  blobStorageNewOrExisting string = 'existing'

@minLength(3)
@maxLength(19)
@description('Provide a name for blob processing application. Use only alphanumeric characters. The name must be unique across Azure.')
param blobProcessingAppName string = ''
param environmentName string = ''

// Create Resource Group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-01-01' = {
  name: resourceGroupName
  location: resourceGroupLocation
  tags:{
    environment : environmentName
  }
}

// Execute all other infra pieces in the given resource group
module initialInfraSetup 'initialdeployment.bicep' = if(deploymentStage == 'initialInfra') {
  name: 'initialInfraSetupModule'
  scope: resourceGroup
  params: {
    environmentName: environmentName
    location: resourceGroupLocation
    blobStorageName: blobStorageName
    blobStorageNewOrExisting: blobStorageNewOrExisting
    blobProcessingApplication: '${blobProcessingAppName}app'
    eventGridName: '${blobStorageName}-eventgrid'
    dataExplorerDatabaseName: '${blobProcessingAppName}metrics'
    dataExplorerName: '${blobProcessingAppName}data'
    metricsAdvisorName: '${blobProcessingAppName}ma'
    grafanaName: grafanaDashboardName
  }
}

module postFuncDeployment 'postappdeployment.bicep' = if(deploymentStage == 'postFunctionApp') {
  name : 'postFunctionAppModule'
  scope : resourceGroup
  params: {
    eventGridName: '${blobStorageName}-eventgrid'
    blobProcessingApplicationName: '${blobProcessingAppName}app'
    eventgridProcessingFunctionName: eventgridProcessingFunctionName
  }
}
