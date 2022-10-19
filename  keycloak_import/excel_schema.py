from ast import Str
import enum
import pydantic


class ResourceType(enum.Enum):
    GROUP = "group"
    USER = "user"
    CLIENT = "client"
    RESOURCE = "resource"
    SCPOES = "scpoes"
    PERMISSION = "permission"


class Group(pydantic.BaseModel):
    groupName: str
    groupPath: str


class User(pydantic.BaseModel):
    userName: str
    email: str
    lastName: str
    firstName: str
    password: str
    groups: str


class Client(pydantic.BaseModel):
    clientId: str
    displayName: str
    description: str
    rootUrl: str
    adminUrl: str
    baseUrl: str
    redirectUrls: str


class Resource(pydantic.BaseModel):
    resource: str
    resourceType: str
    owner: str
    uris: str


class Scpoes(pydantic.BaseModel):
    name: str
    owner: str


class Permission(pydantic.BaseModel):
    name: str
    description: str
    resourceOrResourceType: str
    scopes: str
    userGroup: str
    owner: str
