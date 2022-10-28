"""Internal schema for keycloak"""

import pydantic
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


class Realm(ImportModel):
    enabled: bool = True
    name: str


class User(ImportModel):
    """User model"""

    class UserAction(str):
        UPDATE_PASSWORD = "UPDATE_PASSWORD"
        TERMS_AND_CONDITIONS = "terms_and_conditions"
        UPDATE_PROFILE = "UPDATE_PROFILE"
        VERIFY_EMAIL = "VERIFY_EMAIL"

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


class ClientBase(ImportModel):
    client_id: str


class KeyCloakClient(ClientBase):
    """keyclock client model"""

    class ClinetAuthorizationSettings(pydantic.BaseModel):
        decision_strategy: str = "AFFIRMATIVE"

    id: str = ""
    name: str = ""
    description: str = ""
    root_url: str = ""
    admin_url: str = ""
    base_url: str = ""
    surrogate_auth_required: bool = False
    enabled: bool = True
    always_display_in_console: bool = False
    client_authenticator_type: str = "client-secret"
    redirect_uris: list[str] = []
    web_origins: list[str] = []
    not_before: int = 0
    bearer_only: bool = False
    consent_required: bool = False
    standard_flow_enabled: bool = True
    implicit_flow_enabled: bool = False
    direct_access_frants_enabled: bool = True
    service_accounts_enabled: bool = True
    authorization_services_enabled: bool = True
    public_client: bool = False
    frontchannel_logout: bool = True
    protocol: str = "openid-connect"
    attributes: dict = {"client_credentials.use_refresh_token": "true"}
    authorization_settings: ClinetAuthorizationSettings = ClinetAuthorizationSettings()


class KeyCloakResourceType(str):
    LORA = "LoRa Sensor"
    ALARM = "Alarm"
    BACNET = "BACnet"


class KeyCloakResourceBase(ClientBase):
    """resource base model"""

    class Scope(str):
        pass

    name: str
    icon_uri: str = ""
    owner_managed_access: bool = False
    _id: str = ""


class LoraResource(KeyCloakResourceBase):
    """Lora type resource"""

    class Scope(str):
        DATA_HISTORICAL = "data:historical"
        DATA_REALTIME = "data:realtime"

    scopes: list[Scope] = [Scope.DATA_HISTORICAL, Scope.DATA_REALTIME]
    type: str = KeyCloakResourceType.LORA


class AlarmResource(KeyCloakResourceBase):
    """Alarm type resource"""

    class Scope(str):
        ALARM_READ = "alarm:read"
        ALARM_ACK = "alarm:ack"

    scopes: list[Scope] = [Scope.ALARM_READ, Scope.ALARM_ACK]
    type: str = KeyCloakResourceType.ALARM


class BacnetResource(KeyCloakResourceBase):
    """Bacnet type resource"""

    class Scope(str):
        BACNET_READ = "bacnet:read"

    scopes: list[Scope] = [Scope.BACNET_READ]
    type: str = KeyCloakResourceType.BACNET


class GroupBasePolicy(ClientBase):
    name: str
    id: str = ""
    description: str = ""
    groups_claim: str = ""
    logic: str = "POSITIVE"
    groups: list[str] = []


class ScopeBasePermission(ClientBase):
    name: str
    id: str = ""
    description: str = ""
    resource_type: str = ""
    decision_strategy: str = "AFFIRMATIVE"
    resources: str
    policies: list[str]
    scopes: list[str]
