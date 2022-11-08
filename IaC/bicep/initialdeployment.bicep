param blobStorageName string = ''
param blobStorageNewOrExisting string = 'existing'
param location string  = resourceGroup().location
param dataExplorerName string = ''
param dataExplorerDatabaseName string = ''
param eventGridName string = ''
param blobProcessingApplication string = ''
param environmentName string = ''
param grafanaName string = ''
param metricsAdvisorName string = ''

var managedIdentityName = '${blobProcessingApplication}-identity'
var functionAppStorage = '${blobProcessingApplication}sa'
var functionAppPlan = '${blobProcessingApplication}plan'
var functionAppConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${processFunctionAppStorageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${listKeys(processFunctionAppStorageAccount.id, processFunctionAppStorageAccount.apiVersion).keys[0].value}'



resource MyStorageAccountResource 'Microsoft.Storage/storageAccounts@2021-02-01' = if (blobStorageNewOrExisting == 'new') {
  name: blobStorageName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'    
  }
  properties: {
    supportsHttpsTrafficOnly:true
  }
  tags:{
    environment : environmentName
  }
}

resource MyStorageAccountBlobService 'Microsoft.Storage/storageAccounts/blobServices@2021-09-01' = if (blobStorageNewOrExisting == 'new') {
  parent: MyStorageAccountResource
  name: 'default'
  properties: {
    changeFeed: {
      enabled: false
    }
    restorePolicy: {
      enabled: false
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      enabled: true
      days: 7
    }
    isVersioningEnabled: false
  }
}

resource MyStorageAccountBlobserviceContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-09-01' = if (blobStorageNewOrExisting == 'new') {
  parent: MyStorageAccountBlobService
  name: 'videotelemetrycontainer'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
}

resource nameStorageAccountEventgridResource 'Microsoft.EventGrid/systemTopics@2022-06-15' = {
  name : eventGridName
  location: location
  tags:{
    environment : environmentName
  }
  properties: {
    topicType: 'Microsoft.Storage.StorageAccounts'
    source: MyStorageAccountResource.id
  }
}

resource processFunctionAppManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2021-09-30-preview' = {
  name: managedIdentityName
  location: location
  tags:{
    environment : environmentName
  }
}

resource processFunctionAppStorageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {
  name: functionAppStorage
  location: location
  tags:{
    environment : environmentName
  }
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}

resource processFunctionAppHostingPlan 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: functionAppPlan
  location: location
  tags:{
    environment : environmentName
  }
  sku: {
    name: 'F1'
    tier: 'Free'
  }
  properties: {
    reserved: true
  }
}

resource processFunctionApp 'Microsoft.Web/sites@2021-03-01' = {
  name: blobProcessingApplication
  location: location
  kind: 'functionapp,linux'
  tags:{
    environment : environmentName
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${processFunctionAppManagedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: processFunctionAppHostingPlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name:'AzureWebJobsStorage'
          value: functionAppConnectionString
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: 'funcappfiles'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: functionAppConnectionString
        }
      ]
      linuxFxVersion  : 'PYTHON|3.9'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
}

resource clusterDataExpResource 'Microsoft.Kusto/Clusters@2022-02-01' = {
  name: dataExplorerName
  location: location
  tags:{
    environment : environmentName
  }
  sku: {
    name: 'Dev(No SLA)_Standard_E2a_v4'
    tier: 'Basic'
    capacity: 1
  }
  identity: {
    type: 'SystemAssigned'
  }
}

resource clusterDataExpTable 'Microsoft.Kusto/Clusters/Databases@2022-02-01' = {
  parent: clusterDataExpResource
  name: dataExplorerDatabaseName
  location: location
  kind: 'ReadWrite'
  properties: {
    softDeletePeriod: 'P365D'
    hotCachePeriod: 'P31D'
  }
  resource sdf 'scripts' = {
    name : 'db-scripts'
    properties: {
      scriptContent: loadTextContent('kustotablesetup.kql')
      continueOnErrors: false
    }
  }
}

resource clusterDataExpFunctionAppPermission 'Microsoft.Kusto/Clusters/PrincipalAssignments@2022-02-01' = {
  parent: clusterDataExpResource
  name: '${processFunctionAppManagedIdentity.name}permission'
  properties: {
    principalId: processFunctionAppManagedIdentity.properties.principalId
    role: 'AllDatabasesAdmin'
    principalType: 'App'
  }
}

resource metricsadvisorResource 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: metricsAdvisorName
  location: location
  tags:{
    environment : environmentName
  }
  sku: {
    name: 'S0'
  }
  kind: 'MetricsAdvisor'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    apiProperties: {
    }
    customSubDomainName: metricsAdvisorName
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
  }
}

resource clustersDataexpMetricsAdvisorPermission 'Microsoft.Kusto/Clusters/PrincipalAssignments@2022-02-01' = {
  parent: clusterDataExpResource
  name: '${metricsadvisorResource.name}permission'
  properties: {
    principalId: metricsadvisorResource.identity.principalId
    role: 'AllDatabasesViewer'
    principalType: 'App'
  }
}

resource managedGrafana 'Microsoft.Dashboard/grafana@2022-08-01' = {
  name: grafanaName
  location: location
  sku: {
    name: 'Standard'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${processFunctionAppManagedIdentity.id}': {}
    }
  }
  properties: {
    zoneRedundancy: 'Disabled'
    publicNetworkAccess: 'Enabled'
    autoGeneratedDomainNameLabelScope: 'TenantReuse'
    apiKey: 'Disabled'
    deterministicOutboundIP: 'Disabled'
    grafanaIntegrations: {
      azureMonitorWorkspaceIntegrations: []
    }
  }
}
