"""Device RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic
from typing import Dict


class DeviceBase(pydantic.BaseModel):
    applicationID: str
    description: str
    devEUI: str
    deviceProfileID: str
    name: str


class Device(DeviceBase):
    deviceProfileName: str
    deviceStatusBattery: int
    deviceStatusBatteryLevel: int
    deviceStatusBatteryLevelUnavailable: bool
    deviceStatusExternalPowerSource: bool
    deviceStatusMargin: int
    lastSeenAt: str


class DeviceRestBody(DeviceBase):
    isDisable: bool
    refeneceAltitude: int
    skipFCntCheck: bool
    tags: Dict
    variables: Dict


class DeviceOTAAKeys(pydantic.BaseModel):
    devEUI: str = ""
    nwkKey: str = ""
    appKey: str = ""
    genAppKey: str = ""


class DeviceABPKeys(pydantic.BaseModel):
    devEUI: str = ""
    devAddr: str = ""
    appSKey: str = ""
    nwkSEncKey: str = ""
    sNwkSIntKey: str = ""
    fNwkSIntKey: str = ""
    fCntUp: int = 0
    nFCntDown: int = 0
    aFCntDown: int = 0
