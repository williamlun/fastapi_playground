import pydantic
import enum
from typing import Generic, TypeVar


class Resource(pydantic.BaseModel):
    class KeycloakResourceType:
        LORA = "LORA"
        ALARM = "Alarm"
        BACNET = "BACNET"

    class Scope:
        pass

    class LoraScope(Scope):
        DATA_READ = "data-read"
        DATA_WRITE = "data-write"

    class AlarmScope(Scope):
        ALARM_READ = "ALARM-read"
        ALARM_WRITE = "ALARM-write"

    name: str
    type: KeycloakResourceType
    icon_uri: str = ""
    owner_managed_access: bool = False
    scopes: set[Scope] = set()
    _id: str = ""


objA = Resource(
    name="name",
    type=Resource.KeycloakResourceType.ALARM,
    scopes=[Resource.LoraScope.DATA_READ, Resource.AlarmScope.ALARM_WRITE],
)


print(objA)
print("123")
