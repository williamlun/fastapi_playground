"schema for graphDB data"
# pylint: disable=invalid-name
import enum
import pydantic
import uuid
import json
import pydantic.generics


def to_camel(string: str) -> str:
    string_split = string.split("_")
    return string_split[0] + "".join(word.capitalize() for word in string_split[1:])


class ResourceType(enum.Enum):
    """Resource type definition of graphDB"""

    TENANT = "Tenant"
    SITE = "Site"
    DEVICE = "Device"
    FIELD = "Field"
    HAS_LOCATION = "hasLocation"
    HAS_POINT = "hasPoint"

    class Config:
        use_enum_values = True


class BaseNode(pydantic.BaseModel):
    """Base Class of nodes"""

    def to_dict(self, **kwargs) -> dict:
        return json.loads(self.json(by_alias=True, **kwargs))

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

    node_type: ResourceType
    name: str


class ResourceBaseNode(BaseNode):
    node_type: ResourceType


class Relation(pydantic.BaseModel):
    node_type: ResourceType
    to_node: ResourceBaseNode


class Tenant(ResourceBaseNode):
    node_type = pydantic.Field(ResourceType.TENANT, exclude=True)
    id: uuid.UUID
    display_name: str


class Site(ResourceBaseNode):
    node_type = pydantic.Field(ResourceType.SITE, exclude=True)
    id: uuid.UUID
    display_name: str


class Field(ResourceBaseNode):
    node_type = pydantic.Field(ResourceType.FIELD, exclude=True)


class Device(ResourceBaseNode):
    node_type = pydantic.Field(ResourceType.DEVICE, exclude=True)
    id: uuid.UUID
    display_name: str
    relations: list[Relation]
