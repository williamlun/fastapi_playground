"""Gateway RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic
from typing import Optional


class Location(pydantic.BaseModel):
    accuracy: int
    altitude: int
    latitude: int
    longitude: int
    source: str


class Gateway(pydantic.BaseModel):
    id: str
    name: str
    description: str
    networkServerID: str
    organizationID: str
    networkServerName: Optional[str]
    location: Location


class GateWayRestBody(Gateway):
    serviceProfileID: str
