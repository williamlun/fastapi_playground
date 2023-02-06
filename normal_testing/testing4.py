"""Internal Services Schema """
from typing import Union, Optional

import enum
import pendulum
import pydantic
import pandas as pd
import pytz
from datetime import datetime
import json
import itertools


class DataUnit(pydantic.BaseModel):
    key: str
    timestamp: pendulum.DateTime
    value: Union[float, int, str, bool]

    def to_dict(self):
        return {
            "key": self.key,
            "timestamp": datetime.fromtimestamp(self.timestamp.timestamp()),
            "value": self.value,
        }


class AggregationType(enum.Enum):
    SUM = "sum"
    MEAN = "mean"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    FIRST = "first"
    DESCRIBE = "describe"


def _convert_df_to_data_unit(df: pd.DataFrame) -> list[DataUnit]:
    response_list: list[list] = [[] for _ in range(len(df.columns.values))]

    result = df.to_json(orient="table")
    parsed = json.loads(result)["data"]

    for row in parsed:
        for idx, point in enumerate(list(df.columns.values)):
            data_unit = {
                df.index.name: pendulum.parse(row[df.index.name]).in_tz("Asia/Hong_Kong"),  # type: ignore
                "key": point,
                "value": row[point],
            }
            response_list[idx].append(data_unit)

    return list(itertools.chain(*response_list))


def apply_aggregation_function(
    agg: AggregationType,
    grouping_interval: Optional[str],
    data: list[DataUnit],
) -> list[DataUnit]:
    original_df = pd.DataFrame.from_records(data)
    original_df = original_df.pivot_table(
        index="timestamp", columns="key", values="value"
    )

    df = original_df.groupby(pd.Grouper(freq=grouping_interval))
    df = df.agg(agg.value)
    return _convert_df_to_data_unit(df)


# pendulum.now().add(minutes=i)
fake_data = []
for i in range(100):
    fake_data.append(
        DataUnit(
            key="on9", timestamp=pendulum.now().add(minutes=i), value=str(i)
        ).to_dict()
    )


result = apply_aggregation_function(AggregationType.MEAN, "5T", fake_data)
print(result)
