"""Organization RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic


class Organization(pydantic.BaseModel):
    id: str
    name: str
    displayName: str
    canHaveGateways: bool


class OrganizationRestBody(Organization):
    maxDeviceCount: int
    maxGatewayCount: int
