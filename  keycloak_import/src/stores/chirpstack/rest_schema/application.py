"""Application RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic
from typing import Optional


class ApplicationBase(pydantic.BaseModel):
    id: Optional[str]
    name: str
    description: str
    organizationID: str
    serviceProfileID: str


class Application(ApplicationBase):
    serviceProfileName: str


class ApplicationRestBody(ApplicationBase):
    payloadCodec: str
    payloadDecoderScript: str
    payloadEncoderScript: str
