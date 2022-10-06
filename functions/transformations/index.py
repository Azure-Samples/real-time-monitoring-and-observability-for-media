from transformations.slow_start_transform import SlowStartTransform
from transformations.transform import Transform


def get_transformations(json_string: str) -> list[Transform]:
    slow_start_transformation = SlowStartTransform(json_string)
    return [slow_start_transformation]
