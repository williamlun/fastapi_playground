"""Service Profile RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic
from typing import Optional


class ServiceProfile(pydantic.BaseModel):
    id: str
    name: str
    networkServerID: str
    networkServerName: Optional[str]
    organizationID: str
    addGWMetaData: bool = True
