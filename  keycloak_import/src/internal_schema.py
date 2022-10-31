"""Internal Schema for progarmming"""
# pylint: disable=invalid-name
import enum
import pydantic
from typing import Dict, List, Optional, Union


Attributes = Dict[str, Union[bool, int, float, str, dict, None]]


class ResourceType(enum.Enum):
    NETWORK_SERVER = "network_server"
    ORGANIZATION = "organization"
    SERVICE_PROFILE = "service_profile"
    GATEWAY_PROFILE = "gateway_profile"
    GATEWAY = "gateway"
    DEVICE_PROFILE = "device_profile"
    APPLICATION = "application"
    DEVICE = "device"
    RULE_CHAIN = "Rule Chain"


class ResourceBaseModel(pydantic.BaseModel):
    name: str


class IdBasedResourceModel(ResourceBaseModel):
    def get_id(self):
        pass


class RelationType(enum.Enum):
    MANAGES = "Manages"
    CONTAINS = "Contains"


class Alarm(pydantic.BaseModel):
    """Alarm Schema"""

    class Severity(enum.Enum):
        CRITICAL = "CRITICAL"
        WARNING = "WARNING"

    type: str
    severity: Severity = Severity.CRITICAL

    class Config:
        use_enum_values = True


class RuleChain(ResourceBaseModel):
    """RuleChain Schema"""

    class Name(enum.Enum):
        DEFAULT = "Root Rule Chain"
        SENSOR_READING_TO_MODBUS = "SENSOR_READING_TO_MODBUS"
        SENSOR_READING_TO_BACNET = "SENSOR_READING_TO_BACNET"
        SEND_EVENTS_TO_KAFKA = "SEND_EVENTS_TO_KAFKA"

    class KafkaConfig(pydantic.BaseModel):
        kafka_cluster_url: str
        kafka_security_protocol: str
        kafka_sasl_mechanism: str
        kafka_username: str
        kafka_password: str

    name: str
    additional_config: Optional[KafkaConfig]

    @pydantic.validator("name", pre=True)
    def check_name(cls, name: str):  # pylint: disable=no-self-argument
        return RuleChain.Name(name).value

    class Config:
        use_enum_values = True


class Device(IdBasedResourceModel):
    """Device schema for internal"""

    class InThingsboard(pydantic.BaseModel):
        """data model for thingsboard devices"""

        class Relation(pydantic.BaseModel):
            from_device: str
            to_device: str
            type: RelationType

            class Config:
                use_enum_values = True

        alarms_attribute: Attributes = {}
        rule_chain_attribute: Attributes = {}
        relations: List[Relation] = []
        additionalInfo: dict = {}

    class InChirpstack(pydantic.BaseModel):
        """Device attribute for chirpstack only"""

        devEUI: str = ""
        application: str = ""

        description: str = ""
        OTAAkey: str = ""
        DeviceAddress: str = ""
        NetworkSessionEncryptionKey: str = ""
        ServingNetworkSessionIntegrityKey: str = ""
        ForwardingNetworkSessionIntegrityKey: str = ""
        ApplicationSessionKey: str = ""
        uplinkInterval: str = ""
        variables: dict = {}

        def get_id(self):
            return self.devEUI

    name: str = ""
    deviceProfile: str = ""
    thingsboard: InThingsboard = InThingsboard()
    chirpstack: Optional[InChirpstack]


class DeviceProfile(ResourceBaseModel):
    """Schema of Device Profile"""

    class InChirpstack(pydantic.BaseModel):
        """device profile attribute for chirpstack only"""

        networkServer: str = ""
        organization: str = ""
        macVersion: str = ""
        regParamsRevision: str = "A"
        adrAlgorithmID: str = "default"
        maxEIRP: int = 16
        uplinkInterval: str = ""
        supportsJoin: bool = True
        rxDelay1: int = 0
        rxDROffset1: int = 0
        rxDataRate2: int = 0
        rxFreq2: int = 0
        factoryPresetFreqs: List[int] = []
        supportsClassB: bool = False
        classBTimeout: str = "0"
        pingSlotPeriod: str = "0"
        pingSlotDR: str = "0"
        pingSlotFreq: int = 0
        supportsClassC: bool = True
        classCTimeout: int = 2
        payloadCodec: str = "CUSTOM_JS"
        payloadDecoderScript: str = ""
        payloadEncoderScript: str = ""

        @pydantic.validator("factoryPresetFreqs", pre=True)
        def factoryPresetFreqs_as_list(cls, v):  # pylint: disable=no-self-argument
            if isinstance(v, str) and "," in v:
                return v.split(",")
            return []

    class InThingsboard(pydantic.BaseModel):
        rule_chain: str = ""
        alarms: List[Alarm] = []

    name: str
    chirpstack: Optional[InChirpstack]
    thingsboard: InThingsboard = InThingsboard()

    class Config:
        use_enum_values = True


class Application(ResourceBaseModel):
    name: str
    serviceProfile: str
    organization: str
    description: str


class Gateway(IdBasedResourceModel):
    name: str
    id: str
    organization: str
    networkServer: str
    serviceProfile: str
    gatewayProfile: str

    def get_id(self):
        return self.id


class GatewayProfile(ResourceBaseModel):
    """Schema of Gateway Profile"""

    name: str
    channels: List[int] = [0, 1, 2, 3, 4, 5, 6, 7]
    networkServer: str
    statsInterval: str = "30s"

    @pydantic.validator("channels", pre=True)
    def channel_as_list(cls, v):  # pylint: disable=no-self-argument
        if isinstance(v, str) and "," in v:
            return v.split(",")
        return []


class NetworkServer(ResourceBaseModel):
    name: str
    server: str
    port: int


class Organization(ResourceBaseModel):
    name: str
    displayName: str
    maxDeviceCount: int = 0
    maxGatewayCount: int = 0
    canHaveGateways: bool = True


class ServiceProfile(ResourceBaseModel):
    name: str
    networkServer: str
    organization: str
    addGWMetaData: bool = True
