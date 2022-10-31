"""Common General Schema"""
import enum
import pydantic

# pylint: disable=invalid-name
class GeneralId(pydantic.BaseModel):

    """Schema General Id Module"""

    class EntityType(enum.Enum):
        CUSTOMER = "CUSTOMER"
        DEVICE = "DEVICE"
        DEVICE_PROFILE = "DEVICE_PROFILE"
        RULE_CHAIN = "RULE_CHAIN"
        RULE_NODE = "RULE_NODE"
        TENANT = "TENANT"

    id: str
    entityType: EntityType

    class Config:
        use_enum_values = True
