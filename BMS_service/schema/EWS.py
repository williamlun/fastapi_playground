import pydantic
import enum
import datetime
from typing import Optional


class DataModelType(enum.Enum):
    ContainerItem = 0
    ValueItem = 1
    HistroyItem = 2
    AlarmItem = 3


class ContainerType(enum.Enum):
    Folder = "folder"
    Server = "server"
    Device = "device"
    Structure = "structure"
    Service = "service"


class Metadata(pydantic.BaseModel):
    class MetadataCaotegoryType(pydantic.BaseModel):
        class MetadataPropertyType(pydantic.BaseModel):
            name: str
            value: str

        name: str
        property: list[MetadataPropertyType]

    id: str
    version: str
    category: list[MetadataCaotegoryType]


class ContainerItem(pydantic.BaseModel):
    id: str
    name: str
    description: str
    type: ContainerType
    items: list[str]
    metadata: Optional[list]


class ContainerItemSimpleType(pydantic.BaseModel):
    id: str
    name: str
    description: str
    type: str


class ValueItemType(enum.Enum):
    DateTime = "datetime"
    Boolean = "boolean"
    String = "string"
    Double = "double"
    Long = "long"
    Integer = "integer"
    Duration = "duration"


class ValueItemState(enum.Enum):
    good = 0
    uncertain = 1
    Forced = 2
    Offline = 3
    Error = 4


class ValueItem(pydantic.BaseModel):
    id: str
    name: str
    description: str
    type: ValueItemType
    value: str
    unit: str
    writeable: int  # 0: read only, 1: read and write
    state: ValueItemState
    focrceable: int  # 0 : not forceable, 1: forceable
    enum_id: Optional[str]
    metadata: Optional[list]


class AlarmItemState(enum.Enum):
    Normal = 0
    Active = 1
    Acknowledged = 2
    Reset = 3
    Disasbled = 4


class AlarmItem(pydantic.BaseModel):
    id: str
    name: str
    description: str
    state: AlarmItemState
    value_item_id: Optional[str]
    metadata: Optional[list]


class HistoryItem(pydantic.BaseModel):
    id: str
    name: str
    description: str
    type: str
    unit: str
    value_item_id: str
    metadata: Optional[list]


class HistoryRecordType(pydantic.BaseModel):
    value: str
    state: ValueItemState
    timestamp: datetime.datetime


class HistoryRecords(pydantic.BaseModel):
    value_item_id: str
    unit: str
    type: str
    list: HistoryRecordType
    metadata: Optional[list]


class AlarmEventAcknowledgeableEnum(enum.Enum):
    no = 0
    yes = 1
    required = 2


class AlarmEvent(pydantic.BaseModel):
    id: str
    source_id: Optional[str]
    source_name: Optional[str]
    acknowledgeable: int
    time_stamp_occurence: datetime.datetime
    time_stamp_transition: datetime.datetime
    priority: int
    state: int
    type: str
    message: str
