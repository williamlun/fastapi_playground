import pydantic
import uuid
import enum


class ResourceType(enum.Enum):
    REALMS = "realms"
    USERGROUP = "user_group"
    USER = "user"
    CLIENT = "client"
    SCPOES = "scpoes"
    POLICY = "policy"
    RESOURCE = "resource"
    PERMISSION = "permission"


def to_camel(string: str) -> str:
    splitted_string = string.split("_")
    return splitted_string[0] + "".join(
        word.capitalize() for word in splitted_string[1:]
    )


class ImportModel(pydantic.BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class UserAction(str):
    UPDATE_PASSWORD = "UPDATE_PASSWORD"
    TERMS_AND_CONDITIONS = "terms_and_conditions"
    UPDATE_PROFILE = "UPDATE_PROFILE"
    VERIFY_EMAIL = "VERIFY_EMAIL"


class Realm(ImportModel):
    enabled: bool = True
    name: str


class User(ImportModel):
    class Credentials(pydantic.BaseModel):
        type: str = "password"
        value: str = "password"

    id: str = ""
    username: str
    email: str = ""
    email_verified: bool = True
    enabled: bool = True
    first_name: str = ""
    last_name: str = ""
    credentials: list[Credentials] = [Credentials()]
    groups: list[str] = ""
    required_actions: list[UserAction] = [UserAction.UPDATE_PASSWORD]


class Group(ImportModel):
    name: str
    id: str = ""
    path: str = ""


class ClinetAuthorizationSettings(pydantic.BaseModel):
    decisionStrategy: str = "AFFIRMATIVE"


class ClientBase(ImportModel):
    clientId: str


class KeyCloakClient(ClientBase):
    id: str = ""
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


class ResourceScope(ClientBase):
    displayName: str = ""
    iconUri: str = ""
    id: str = ""


class Scope(ResourceScope):
    name: str


class Resource(ClientBase):
    name: str
    type: str = ""
    icon_uri: str = ""
    ownerManagedAccess: bool = False
    scopes: list[str] = []
    _id: str = ""


class GroupBasePolicy(ClientBase):
    name: str
    id: str = ""
    description: str = ""
    groupsClaim: str = ""
    logic: str = "POSITIVE"
    groups: list[str] = []


class ScopeBasePermission(ClientBase):
    name: str
    id: str = ""
    description: str = ""
    resourceType: str = ""
    decisionStrategy: str = "AFFIRMATIVE"
    resources: str
    policies: list[str]
    scopes: list[str]
