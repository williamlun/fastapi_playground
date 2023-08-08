import pydantic
import enum
import datetime
from typing import Optional, Any, Union


class errorMessageModel(pydantic.BaseModel):
    message: list
    stacktrace: Optional[Any]


class realtime_data(pydantic.BaseModel):  # using pyG3
    id: str
    state: str
    value: Union[float, bool]


class realtime_point_property(pydantic.BaseModel):  # using bql call
    href: str  # include path
    val: str
    status: str
    _is: str  # def/baja:StatusNumeric
    display: str
    display_name: str
    unit: str


class historical_sensor_data(pydantic.BaseModel):
    timestamp: datetime.datetime
    trend_flags: str  # "{ }"
    status: str  # "{ok}"
    value: float


class realtime_data_response(pydantic.BaseModel):
    success: bool
    error: dict
    payload: list[realtime_data]


class historical_data_response(pydantic.BaseModel):
    success: bool
    error: dict
    payload: list[historical_sensor_data]
