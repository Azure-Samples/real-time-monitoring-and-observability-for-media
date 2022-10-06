import json
import logging
import pandas as pd

# Class for load json payload, filter it by event.type and produce DataFrame

""" Class for load json payload, filter it by event.type and produce DataFrame
    ### Initiate the class and pass the json string
    app = Transform('[{}]')

Args:
    json_data (Json): json.load result
"""

logger = logging.getLogger("TransformClass")


class Transform:
    def __init__(self, json_data: str, table: str, mappings: dict[str, str]):
        """Constructor

        Args:
            json_data: string
        """
        self.table = table

        self.json_data = self.__load_json_string(json_data)
        self.mappings = mappings
        self.mapping_properties = list(self.mappings.keys())
        self.mapping_aliases = list(self.mappings.values())

    def prepare_result(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Prepare a result DF with missed columns from initial JSON

        Args:
            data_frame (pd.DataFrame): DataFrame

        Returns:
            pd.DataFrame: DataFrame
        """

        if data_frame.empty:
            return data_frame

        transformed_df =  self.__transform(data_frame)

        for target_column in self.mapping_aliases:
            if target_column not in transformed_df:
                transformed_df[target_column] = None
        return transformed_df.loc[:, self.mapping_aliases]

    def get_dataframe(self) -> pd.DataFrame:
        """#get_dataframe is a required method on an inherited class

        Raises:
            NotImplementedError: This method must be implemented in an inherited class

        Returns:
            pd.DataFrame: Returns Dataframe
        """

        raise NotImplementedError("Must Implement #get_dataframe in Child Class")

    def create_normalized_df(self) -> pd.DataFrame:
        """It takes a JSON, normalizes it, and returns a dataframe

        Returns:
            DataFrame
        """
        # Turn data to normalized dataframe
        norm_df = pd.json_normalize(self.json_data)
        if norm_df.empty:
            return self.__get_empty_df()

        return norm_df

    # PRIVATE

    def __transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """It takes a dataframe, filters out the required columns, renames them and returns the new
        dataframe.

        Args:
            dataframe (pd.DataFrame): DataFrame to be renamed and filtered.

        Returns:
            DataFrame: Renamed Dataframe based on mapping aliases
        """

        # filter out required attributes from the row
        filtered_df = dataframe.filter(self.mapping_properties, axis=1)
        # rename the columns
        renamed = filtered_df.rename(columns=self.mappings)
        return filtered_df.rename(columns=self.mappings)

    def __load_json_string(self, json_data: str) -> list:
        """Load String to DF

        Args:
            json_data (string): json string

        Returns:
            List: loaded List
        """
        try:
            json_variable = json.loads(json_data)
        except json.decoder.JSONDecodeError as err:
            logger.error(err)
            json_variable = [{}]

        return json_variable

    def __get_empty_df(self) -> pd.DataFrame:
        """Return empty DF

        Returns:
            pd.DataFrame: DataFrame
        """
        return pd.json_normalize({})
