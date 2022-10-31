"""Gateway Profile RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic
from typing import List, Optional


class GatewayProfile(pydantic.BaseModel):
    id: str
    name: str
    networkServerID: str
    networkServerName: Optional[str]


class GatewayProfileRestBody(GatewayProfile):
    channels: List[int]
    statsInterval: str
