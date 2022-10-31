"""Device Profile RESTful Request Data Model"""
# pylint: disable=invalid-name
import pydantic
from typing import List, Optional


class DeviceProfile(pydantic.BaseModel):
    id: str
    name: str
    networkServerID: str
    networkServerName: Optional[str]
    organizationID: str


class DeviceProfileRestBody(DeviceProfile):
    """Device Profile Request Body Model"""

    macVersion: str
    regParamsRevision: str
    adrAlgorithmID: str
    maxEIRP: int
    uplinkInterval: str
    supportsJoin: bool
    rxDelay1: int
    rxDROffset1: int
    rxDataRate2: int
    rxFreq2: int
    factoryPresetFreqs: List[int]
    supportsClassB: bool
    classBTimeout: str
    pingSlotPeriod: str
    pingSlotDR: str
    pingSlotFreq: int
    supportsClassC: bool
    classCTimeout: int
    payloadCodec: str
    payloadDecoderScript: str
    payloadEncoderScript: str
