"""Common RESTful Response Data Model"""
# pylint: disable=invalid-name
from pydantic.generic import GenericModel
from typing import Generic, TypeVar, List

from stores.chirpstack.rest_schema.application import Application
from stores.chirpstack.rest_schema.device_profile import DeviceProfile
from stores.chirpstack.rest_schema.device import Device
from stores.chirpstack.rest_schema.gateway_profile import GatewayProfile
from stores.chirpstack.rest_schema.gateway import Gateway
from stores.chirpstack.rest_schema.network_server import NetworkServer
from stores.chirpstack.rest_schema.organization import Organization
from stores.chirpstack.rest_schema.service_profile import ServiceProfile

ResponseType = TypeVar("ResponseType")
SupportedType = [
    Application,
    DeviceProfile,
    Device,
    GatewayProfile,
    Gateway,
    NetworkServer,
    Organization,
    ServiceProfile,
]


"""
Example:
ResponseModel[ServiceProfile](result=[], totalCount=0s)
"""


class ResponseModel(GenericModel, Generic[ResponseType]):
    result: List[ResponseType]
    totalCount: int
