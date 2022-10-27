import pydantic
import enum
from typing import Generic, TypeVar


class Type(str):
    class Scope(str):
        pass

    name: str


class LORA(Type):
    class Scope(str):
        DATA_READ = "data-read"
        DATA_WRITE = "data-write"

    name = "LORA"


class ALARM(Type):
    class Scope(str):
        ALARM_READ = "ALARM-read"
        ALARM_WRITE = "ALARM-write"

    name = "Alarm"


T = TypeVar("T", bound=Type)


class Resource(Generic[T], pydantic.BaseModel):

    name: str
    type: T.name
    icon_uri: str = ""
    owner_managed_access: bool = False
    scopes: set[T.Scope] = set()
    _id: str = ""


objA = Resource[LORA](
    name="name",
    type=LORA.name,
    scopes=[LORA.Scope.DATA_WRITE, ALARM.Scope.ALARM_READ, "sdaffasd"],
)


print(objA)
print("123")
