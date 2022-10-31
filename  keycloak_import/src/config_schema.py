"""Schema for gateawy config file."""
# pylint: disable=invalid-name
from typing import Optional

import pydantic


class BACnetConfig(pydantic.BaseModel):
    """
    This class contains the configuration for the BACnet gateway
    """

    class General(pydantic.BaseModel):
        """
        This class contains the configuration for the BACnet gateway
        """

        objectName: str
        address: str
        objectIdentifier: int
        maxApduLengthAccepted: int = 1476
        segmentationSupported: str = "segmentedBoth"
        vendorIdentifier: int = 15

    class Device(pydantic.BaseModel):
        """This class contains the configuration for the BACnet gateway"""

        class ValueMapper(pydantic.BaseModel):
            key: str
            type: str
            objectId: str
            propertyId: str = "presentValue"

        class ServerSideRpcUnit(pydantic.BaseModel):
            method: str
            objectId: str
            propertyId: str = "presentValue"
            requestType: str = "writeProperty"
            requestTimeout: int = 10000

        deviceName: str
        deviceType: str = "default"
        address: str
        pollPeriod: int = 10000
        attributes: list[ValueMapper] = []
        timeseries: list[ValueMapper] = []
        serverSideRpc: list[ServerSideRpcUnit] = []

    general: General
    devices: list[Device] = []


class MqttConfig(pydantic.BaseModel):
    """This class contains the configuration for the MQTT gateway."""

    class Broker(pydantic.BaseModel):
        """This class contains the configuration for the MQTT gateway."""

        class Security(pydantic.BaseModel):
            type: str = "basic"
            username: str
            password: str

        name: str
        host: str
        port: int
        clientId: str
        security: Security
        maxMessageNumberPerWorker: int = 10
        maxNumberOfWorkers: int = 100

    class MappingUnit(pydantic.BaseModel):
        """This class contains the configuration for the MQTT gateway."""

        class Converter(pydantic.BaseModel):
            """This class contains the configuration for the MQTT gateway."""

            class ValueMapper(pydantic.BaseModel):
                type: str
                key: str
                value: str

            type: str = "json"
            deviceNameJsonExpression: Optional[str] = None
            deviceNameTopicExpression: Optional[str] = None
            deviceTypeJsonExpression: Optional[str] = None
            deviceTypeTopicExpression: Optional[str] = None
            timeout: int = 60000
            attributes: list[ValueMapper] = []
            timeseries: list[ValueMapper] = []

        topicFilter: str
        converter: Converter

    broker: Broker
    mapping: list[MappingUnit]
    connectRequests: list[dict] = []
    disconnectRequests: list[dict] = []
    attributeRequests: list[dict] = []
    attributeUpdates: list[dict] = []
    serverSideRpc: list[dict] = []


class GatewayGeneralConfig(pydantic.BaseModel):
    """This class contains the configuration for the IoT gateway."""

    class ThingsBoard(pydantic.BaseModel):
        """This class contains the configuration for the IoT gateway."""

        class CheckingDeviceActivity(pydantic.BaseModel):
            checkDeviceInactivity: bool = False
            inactivityTimeoutSeconds: int = 120
            inactivityCheckPeriodSeconds: int = 10

        class Security(pydantic.BaseModel):
            accessToken: str

        host: str
        port: int
        remoteShell: bool = False
        remoteConfiguration: bool = False
        statsSendPeriodInSeconds: int = 3600
        minPackSendDelayMS: int = 0
        checkConnectorsConfigurationInSeconds: int = 60
        handleDeviceRenaming: bool = True
        checkingDeviceActivity: CheckingDeviceActivity = CheckingDeviceActivity()
        security: Security
        qos: int = 1

    class Storage(pydantic.BaseModel):
        type: str = "memory"
        read_records_count: int = 100
        max_record_count: int = 100000

    class Grpc(pydantic.BaseModel):
        enabled: bool = False
        serverPort: int = 9595
        keepaliveTimeMs: int = 10000
        keepaliveTimeoutMs: int = 5000
        keepalivePermitWithoutCalls: bool = True
        maxPingsWithoutData: int = 0
        minTimeBetweenPingsMs: int = 10000
        minPingIntervalWithoutDataMs: int = 5000

    class Connector(pydantic.BaseModel):
        name: str
        type: str
        configuration: str

    thingsboard: ThingsBoard
    storage: Storage = Storage()
    grpc: Grpc = Grpc()
    connectors: list[Connector] = []
