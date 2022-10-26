from abc import update_abstractmethods
import pydantic
import uuid
import enum


class ResourceType(enum.Enum):
    REALMS = "realms"
    USERGROUP = "user_group"


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
    credentials: list[Credentials]
    groups: list[str]
    required_actions: list[UserAction] = [UserAction.UPDATE_PASSWORD]


class PolicyGroup(ImportModel):
    id: str = ""


class Group(PolicyGroup):
    path: str = ""
    name: str


class ClinetAuthorizationSettings(pydantic.BaseModel):
    decisionStrategy: str = "AFFIRMATIVE"


class KeyCloakClient(ImportModel):
    id: str = ""
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


class ResourceScope(ImportModel):
    displayName: str = ""
    iconUri: str = ""
    id: str = ""


class Scope(ResourceScope):
    name: str


class Resource(ImportModel):
    name: str
    type: str = ""
    icon_uri: str = ""
    ownerManagedAccess: bool = False
    scopes: list[ResourceScope] = []
    _id: str = ""


class GroupBasePolicy(ImportModel):
    class UserGroup(PolicyGroup):
        extenChildren: bool = False

    name: str
    id: str = ""
    description: str = ""
    groupsClaim: str = ""
    logic: str = "POSITIVE"
    scopes: list[UserGroup] = []


class ScopeBasePermission(ImportModel):
    name: str
    id: str = ""
    description: str = ""
    resourceType: str = ""
    decisionStrategy: str = "AFFIRMATIVE"
    resources: Resource
    policies: list[GroupBasePolicy]
    scopes: Scope
