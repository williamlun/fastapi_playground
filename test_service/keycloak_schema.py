import pydantic
import uuid


def to_camel(string: str) -> str:
    splitted_string = string.split("_")
    return splitted_string[0] + "".join(
        word.capitalize() for word in splitted_string[1:]
    )


class ImportModel(pydantic.BaseModel):
    pass
    # class Config:
    #     alias_generator = to_camel
    #     allow_population_by_field_name = True


class Customer(pydantic.BaseModel):
    id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""


class User(ImportModel):
    class Credentials(pydantic.BaseModel):
        type: str = "password"
        value: str

    username: str
    email: str = ""
    emailVerified: bool = True
    enabled: bool = True
    firstName: str = ""
    lastName: str = ""
    credentials: list[Credentials]
    groups: list[str]


class Group(ImportModel):
    name: str
    subGroups: list["Group"]


class Realm(ImportModel):
    realm: str
    enabled: bool = True
    users: list[User]
    groups: list[Group]


class ClinetAuthorizationSettings(pydantic.BaseModel):
    decisionStrategy: str = "AFFIRMATIVE"


class KeyCloakClient(pydantic.BaseModel):
    clientId: str
    name: str = ""
    description: str = ""
    rootUrl: str = ""
    adminUrl: str = ""
    baseUrl: str = ""
    surrogateAuthRequired: bool = False
    enabled: bool = True
    alwaysDisplayInConsole: bool = False
    clientAuthenticatorType: str = "client-secret"
    redirectUris: list[str] = []
    webOrigins: list[str] = []
    notBefore: int = 0
    bearerOnly: bool = False
    consentRequired: bool = False
    standardFlowEnabled: bool = True
    implicitFlowEnabled: bool = False
    directAccessGrantsEnabled: bool = True
    serviceAccountsEnabled: bool = True
    authorizationServicesEnabled: bool = True
    publicClient: bool = False
    frontchannelLogout: bool = True
    protocol: str = "openid-connect"
    attributes: dict = {"client_credentials.use_refresh_token": "true"}
    authorizationSettings: ClinetAuthorizationSettings = ClinetAuthorizationSettings()


class BaseScope(pydantic.BaseModel):
    displayName: str = ""
    iconUri: str = ""
    id: str = ""


class Scope(BaseScope):
    name: str


class Resource(pydantic.BaseModel):
    name: str
    type: str = ""
    icon_uri: str = ""
    ownerManagedAccess: bool = False
    scopes: list[BaseScope] = []
    _id: str = ""


class GroupBasePolicy(pydantic.BaseModel):
    class UserGroup(pydantic.BaseModel):
        id: uuid.UUID
        extenChildren: bool = False

    name: str
    id: str = ""
    description: str = ""
    groupsClaim: str = ""
    logic: str = "POSITIVE"
    scopes: list[UserGroup] = []


class ScopeBasePermission(pydantic.BaseModel):
    name: str
    id: str = ""
    description: str = ""
    resourceType: str = ""
    decisionStrategy: str = "AFFIRMATIVE"
    resources: list[uuid.UUID]
    policies: list[uuid.UUID]
    scopes: list[uuid.UUID]


class GetGroupResponse(pydantic.BaseModel):
    id: str
    name: str
    path: str
    subGroups: list["GetGroupResponse"]
