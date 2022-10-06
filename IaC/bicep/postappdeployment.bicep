
param eventGridName string = ''
param blobProcessingApplicationName string = ''
param eventgridProcessingFunctionName string = ''

resource storageaccountEventGridResource 'Microsoft.EventGrid/systemTopics@2022-06-15' existing = {
  name : eventGridName
}

resource processFunctionApp 'Microsoft.Web/sites@2021-03-01' existing = {
  name: blobProcessingApplicationName
}

resource storageaccountEventGridResourceBlobCreate 'Microsoft.EventGrid/systemTopics/eventSubscriptions@2021-12-01' = {
  parent: storageaccountEventGridResource
  name: 'sub_${eventgridProcessingFunctionName}'
  properties: {
    destination: {
      properties: {
        resourceId: '${processFunctionApp.id}/functions/${eventgridProcessingFunctionName}'
        maxEventsPerBatch: 1
        preferredBatchSizeInKilobytes: 64
      }
      endpointType: 'AzureFunction'
    }
    filter: {
      includedEventTypes: [
        'Microsoft.Storage.BlobCreated'
      ]
      enableAdvancedFilteringOnArrays: true
    }
    labels: [
      'sub_${eventgridProcessingFunctionName}'
    ]
    eventDeliverySchema: 'EventGridSchema'
    retryPolicy: {
      maxDeliveryAttempts: 30
      eventTimeToLiveInMinutes: 1440
    }
  }
}
