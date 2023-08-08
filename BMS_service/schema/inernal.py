import pydantic
from typing import Optional, Any, Union
import datetime


class realtime_data(pydantic.BaseModel):
    id: str
    state: str
    value: Union[float, bool]
    timestamp: datetime.datetime = datetime.datetime.now()


class historical_data(pydantic.BaseModel):
    timestamp: str
    trend_flags: str  # "{ }"
    status: str  # "{ok}"
    value: float
