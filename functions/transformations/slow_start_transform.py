import pandas as pd
import logging
from utils.settings import SLOW_START_TABLE

from .transform import Transform


class SlowStartTransform(Transform):
    """Class that inherits from Transform for Slow Start Table.
    It takes in a JSON string and converts to a DataFrame that is ready for ingestion to the Slow Start Table.

    video_slow_start_mappings (dict[str,str]): Mappings of JSON nested keys to their pd.Dataframe column names
    """
    video_slow_start_mappings = {
        "user_details.content_session_id": "user_details_content_session_id",
        "user_details.app_session_id": "user_details_app_session_id",
        "event.attributes.startup_duration_content_ms": "measurement_startup_duration_content_ms",
        "device.browser_name": "dimension_browser_name",
        "device.os_name": "dimension_os_name",
        "geo_location.country": "dimension_country_code",
        "geo_location.city": "dimension_city",
        "network.asn": "dimension_asn",
        "event.formatted_timestamp": "timestamp",
    }

    def __init__(self, json_data: str):
        """Constructor

        Args:
            json_data (str): _description_
        """
        super().__init__(
            json_data=json_data,
            table=SLOW_START_TABLE,
            mappings=self.video_slow_start_mappings,
        )

    # Create Custom Function to get desired Dataframe output
    def get_dataframe(self) -> pd.DataFrame:
        """For Slow Start Table.
        Create the dataframe specific to the slow_start table in Kusto.

        Returns:
            pd.DataFrame: filtered Slow Start Dataframe
        """
        norm_df = self.create_normalized_df()

        # CUSTOM LOGIC OF WHAT TO DO
        events = ["playback_start"]
        if "event.type" in norm_df:
            norm_df = norm_df.loc[norm_df["event.type"].isin(events)]

        if norm_df.empty:
            logging.info("Dataframe does not contain Desired Event Type. Returning Empty Dataframe")
            return pd.DataFrame({})


        return self.prepare_result(norm_df)
