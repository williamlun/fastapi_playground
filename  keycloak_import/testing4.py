import pydantic
import enum
from typing import Generic, TypeVar


class Scope(str):
    DATA_HISTORICAL = "data:historical"
    DATA_REALTIME = "data:realtime"
    ALARM_READ = "alarm:read"
    ALARM_ACK = "alarm:ack"
    BACNET_READ = "bacnet:read"


class KeyCloakResourceType:
    scope: list[Scope] = []
    type: str
    pass


class LORA_SENSOR(KeyCloakResourceType):
    scpoe = [
        Scope.DATA_HISTORICAL,
        Scope.DATA_REALTIME,
    ]

    type = "LoRa Sensor"


class ALARM(KeyCloakResourceType):
    scopes = [
        Scope.ALARM_ACK,
        Scope.ALARM_READ,
    ]

    type = "Alarm"


class BACNET(KeyCloakResourceType):
    scopes = [
        Scope.BACNET_READ,
    ]

    type = "BACnet"


T = TypeVar("T", bound=KeyCloakResourceType)


class MyResourceBase(Generic[T], pydantic.BaseModel):
    name: str
    type: str
    icon_uri: str = ""
    owner_managed_access: bool = False
    scopes: list[Scope] = []
    _id: str = ""


obj = MyResourceBase[LORA_SENSOR]()

print(obj)
print("123")
