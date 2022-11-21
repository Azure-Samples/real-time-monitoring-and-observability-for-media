# Metrics Advisor Setup

## MetricsAdvisorHookTrigger - Python

The `metrics_advisor_hook_trigger` is an HTTP trigger for an alert event that triggers by a hook configuration. See [Metrics Advisor Hook Configuration](https://learn.microsoft.com/azure/applied-ai-services/metrics-advisor/how-tos/alerts) for more details.

## Metrics Advisor configuration

Metrics Advisor (MA) detects anomalies from the dataset which is coming from ADX. When the anomalies are detected in the dataset, MA creates an alert with an incident ID. Using MA REST API and passing required parameters from incident report, we can retrieve the alert details and save it to ADX table using Azure HTTP trigger function.

In order to get an alert and save it to ADX table, we need to follow the below configuration steps:

### Adding the Datafeed in the MA

Go to Azure Portal, Open the MA Resource, and click on `Go to your Workspace`. It will open another browser page where the user needs to select the right directory, subscription, and workspace from dropdowns. Click *Add data feed* and it will ask required configurations:

- **Source Type** - Select Azure Data Explorer
- **Granularity** - Recommend minutely. More details [Granularity](https://learn.microsoft.com/azure/applied-ai-services/metrics-advisor/glossary)
- **Ingested data since** - Data set from ADX table should have exact timestamp for ingestion time otherwise MA will not pick up data set
- **Authentication type** - managed identity
- **Connection String** - Connection string to Kusto Database Ex. `Data Source=https://<kustodatabasename>.<deployedlocation.kusto.windows>.net/;Initial Catalog=<metricsadvisorname>;`
- **Query** - Ex:
  
```kql
slow_start_anomaly_detection 
| project timestamp, user_details_content_session_id, user_details_app_session_id, measurement_startup_duration_content_ms, dimension_browser_name, dimension_os_version, dimension_os_name, dimension_city, dimension_country_code, dimension_asn
| where measurement_startup_duration_content_ms >= 0
| where timestamp >= datetime(@IntervalStart) and timestamp < datetime(@IntervalEnd)
| summarize max_measurement_startup_duration_content_ms= max(measurement_startup_duration_content_ms) by dimension_asn, dimension_browser_name, dimension_city, dimension_country_code, dimension_os_name,
dimension_os_version
```

Load the data by clicking button **load data**.

***Recommendation: to test it, manually ingest data into Kusto slow_start_anomaly_detection table with random data starting with timestamp covering one week, ensure the measurements are normal and not far too apart from each other, and then add random two to three data with measurement that is too far apart for general dataset. That way MA can be tested if it is detecting the anomalies in the dataset***

## Detect Anomalies

When metrics advisor detects anomalies, MA will create an incident ID and anomaly are show in the incident hub. In order to save the alert info into ADX table, we need a Metrics Advisor Hook webhook configured. MA hook will trigger an http webhook alert and send the alert info into our Azure HTTP trigger function App. Using *hook_handler.py* we can retrieve the alert details and save it to ADX table. See [Metrics Advisor Hook Handler Code](../functions/shared/metrics_advisor_hook_handler.py) for more details.

## REST API call to get alert details

Following paramaters are required to get alert details:

- POST /metricsadvisor/v1.0/metrics/{metricId}/series/query HTTP/1.1
- Host: {Cluster name}.cognitiveservices.azure.com
- Ocp-Apim-Subscription-Key: {Azure > Metrics Advisor > MA details page > Resource management > KEY 1}
- x-api-key: {Azure > Metrics Advisor > MA app > API keys > Primary API Key}
- Content-Type: application/json

See [Metrics Advisor Rest API](https://westus2.dev.cognitive.microsoft.com/docs/services/MetricsAdvisor/operations/getIncidentsFromAlertByAnomalyAlertingConfiguration/console) for more details.

## Create Web Hook on MA

1. In the MA Workspace. On the left hand side panel click Hooks -> Create hook. Set up Webhook. You are required to provide Endpoint API when the alert is triggered. Ex. `https://<functionAppName>.azurewebsites.net/api/<metrics_advisor_hook_trigger - this_is_the_function_name_that_handles_http_trigger_from_metrics_advisor_hook>?code=<Azure Function App Function Key>`
2. Once the webhook is set, we need to configure our alert hook with our data feed metrics. Go to Data Feed in the Workspace and select recently added data feed. Click the metric name. It will open up your metrics detection configuration page. On the left hand side below the detection configuration, there is an alert configuration. Add alert by clicking plus (+) icon and set up your alert configuration.

To learn more about MA hooks see [Metrics Advisor Hooks](https://learn.microsoft.com/en-us/azure/applied-ai-services/metrics-advisor/how-tos/alerts)

***Now the webhook is configured with our data feed metrics***

***Go to the next step to run the test to test current setup. [Running Tests Locally](/docs/6_running_tests_locally.md)***
