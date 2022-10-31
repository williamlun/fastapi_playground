"""Excel resource model"""
# pylint: disable=invalid-name
import enum
import pydantic
from typing import Union


class ResourceType(enum.Enum):
    GATEWAY = "gateway"
    DEVICE_PROFILE = "device_profile"
    DEVICE = "device"
    DEFAULT_ALARMS_SETTING = "default_alarms_setting"
    ALARMS_SETTING = "alarms_setting"
    SENSOR_READING_TO_BACNET = "SENSOR_READING_TO_BACNET"
    GENERIC_DEVICE = "generic_device"
    SENSOR_CALIBRATION = "sensor_calibration"


class SiteName(pydantic.BaseModel):
    name: str


class Gateaway(pydantic.BaseModel):
    id: str
    gatewayProfile: str


class DeviceProfile(pydantic.BaseModel):
    """Schema of Device Profile"""

    name: str
    macVersion: str
    supportsClassC: bool
    uplinkInterval: str
    ruleEngine: str


class Device(pydantic.BaseModel):
    """Deivce schmea of excel"""

    id: str
    deviceProfile: str
    description: str
    OTAAkey: str
    DeviceAddress: str
    NetworkSessionEncryptionKey: str
    ServingNetworkSessionIntegrityKey: str
    ForwardingNetworkSessionIntegrityKey: str
    ApplicationSessionKey: str
    uplinkInterval: str

    def get_id(self):
        return self.id


class DefaultAlarmsSetting(pydantic.BaseModel):
    deviceProfile: str
    conditionType: str
    operator: str
    field: str
    attrubute: str
    value: Union[bool, int]


class SENSOR_READING_TO_BACNET(pydantic.BaseModel):
    fromDevice: str
    field: str
    toDevice: str
    object: str


class GenericDevice(pydantic.BaseModel):
    id: str
    boject: str
    fieldName: str


class SensorCalibration(pydantic.BaseModel):
    id: str
    fieldName: str
    scale: str
    offset: str


class Config(pydantic.BaseModel):
    """model for config yaml file"""

    class Thingsboard(pydantic.BaseModel):
        """schema for thingsboard config"""

        class KafkaConnection(pydantic.BaseModel):
            url: str
            security_protocol: str
            sasl_mechanism: str
            username: str
            password: str

        host: str
        port: str
        mqtt_port: str
        username: str
        password: str
        kafka: KafkaConnection

    class Chirpstack(pydantic.BaseModel):
        host: str
        port: str
        mqtt_port: str
        username: str
        password: str
        mqtt_username: str
        mqtt_password: str

    class Neo4j(pydantic.BaseModel):
        host: str
        port: str
        username: str
        password: str

    excel_path: str
    export_path: str = "../configfile/"
    thingsboard: Thingsboard
    chirpstack: Chirpstack
    neo4j: Neo4j

    @pydantic.root_validator(pre=True)
    def form_full_excel_path(cls, values):  # pylint: disable=no-self-argument
        values["excel_path"] = "../configfile/" + values.get("excel_name")
        return values
