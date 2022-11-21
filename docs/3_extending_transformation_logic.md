# Extending and Customizing Transformation Logic

This sample project demonstrates the ability to take in JSON data, and convert it into an ingestible `pandas.Dataframe` that can then be ingested into Azure Data Explorer (Kusto Clusters).

`transform.py` - The current struct of this file and the `class Transform()` is to give generalized methods in preparing data from JSON to a Dataframe.

The idea will be to extend `Transform` by creating a custom `CustomTransform(Transform)`, that contains custom logic on how that transformation can happen, and what the input JSON data and **output** Dataframe structures look like.

For an example, Let's examine [slow_start_transform.py](../functions/transformations/slow_start_transform.py):

- The `slow_start_transform.py` extends from `transform.py`.

```python
class SlowStartTransform(Transform)
```

- `slow_start_transform.py` contains mappings between JSON properties and their desired `pandas.Dataframe` column names

```python
video_slow_start_mappings = {

    # { JSON_property: DataFrame_Column_Name }

    "user_details.app_session_id": "user_details_app_session_id",
    "user_details.content_session_id": "user_details_content_session_id",
    "event.formatted_timestamp": "timestamp",
    "event.attributes.startup_duration_content_ms": "measurement_startup_duration_content_ms",
    "device.browser_name": "dimension_browser_name",
    "device.os_name": "dimension_os_name",
    "geo_location.city": "dimension_city",
    "network.asn": "dimension_asn",
    "geo_location.country": "dimension_country_code",
}
```

- `SlowStartTransform` overrides `Transform.get_dataframe()`, and custom logic for transforming the data can be appended between `self.transform()` and `self.prepare_result()`

```python
def get_dataframe(self) -> pd.DataFrame:
    """For Slow Start Anomaly Detection.
    Create the dataframe specific to the slow_start anomaly table in Kusto.

    Returns:
        pd.DataFrame: filtered Slow Start Dataframe
    """
    main_df = self.transform()

    # CUSTOM LOGIC OF WHAT TO DO

    return self.prepare_result(main_df)
```

## Creating Custom Transformer

Create file for extended class `custom_transformation.py`. And also set in `local.settings.json` the name of the **target Kusto Table**.

```python
# custom_transformation.py
import pandas as pd
# which Kusto Table to target for ingesting the Dataframe
from utils.settings import TARGET_KUSTO_TABLE
from .transform import Transform

class CustomTransform(Transform)

```

```python
# utils/settings.py
import os
TARGET_KUSTO_TABLE = os.environ.get("TARGET_KUSTO_TABLE")
```

```json
// local.settings.json
{
  "Values": {
    // ...
    "TARGET_KUSTO_TABLE": "target_table"
  }
}
```

Create a `dict` with your mappings between the JSON properties you wish to **filter from the JSON**, and what their desired `pandas.Dataframe` column names are to be

```python
property_mappings = {
    "first_name": "first_name",
    "location.latitude": "location_latitude",
    "location.longitude": "location_longitude",
}
```

Edit the `__init__` constructor with correct argument values. This includes setting the
`mappings` and `table` name.

| argument   | description                          |
| ---------- | ------------------------------------ |
| `table`    | The Name of the targeted Kusto Table |
| `mappings` | JSON to Dataframe Property Mappings  |

```python
    def __init__(self, json_data: str):
        super().__init__(json_data=json_data, table=TARGET_KUSTO_TABLE, mappings=self.property_mappings)
```

Override the `get_dataframe()` class instance method. Between `self.create_normalized_df()` and `self.prepare_result`, add your custom logic.

- `create_normaled_df()` will take the JSON File and create a normalized DataFrame
- `prepare_result()` will take in a DataFrame and prepare it into an Ingestible DataFrame for Data Explorer

```python
def get_dataframe(self) -> pd.DataFrame:

    norm_df = self.create_normalized_df()

    # CUSTOM LOGIC OF WHAT TO DO
    custom_transform_df = self._do_custom_logic(norm_df)

    return self.prepare_result(custom_transform_df)
```

The last step will be to append this `CustomTransformation` to the `transformations/index.py` for import into the Azure Functions.

```python
def get_transformations(json_string: str) -> list[Transform]:
    custom_transformation = CustomTransformation(json_string)
    second_transformation = SecondTransformation(json_string)
    return [custom_transformation, second_transformation]
```

***Go to the next step to learn more about types of function triggers in this project [Function Trigger Types](/docs/4_function_triggers.md)***
