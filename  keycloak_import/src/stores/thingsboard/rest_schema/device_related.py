"""Device Profile RESTful Schema"""
# pylint: disable=invalid-name

from typing import Any, List, Optional

import pydantic
import time

from stores.thingsboard.rest_schema.general import GeneralId


class DeviceProfileTypeDefault(pydantic.BaseModel):
    type: str = "DEFAULT"


class ProvisionConfigDefault(pydantic.BaseModel):
    type: str = "DISABLED"
    provisionDeviceSecret: Optional[Any] = None


class DeviceProfileData(pydantic.BaseModel):
    """Device Profile's Data Schema

    This should be a must otherwise the response
    with status_code 500 will be returned
    """

    configuration: DeviceProfileTypeDefault = DeviceProfileTypeDefault()
    transportConfiguration: DeviceProfileTypeDefault = DeviceProfileTypeDefault()
    provisionConfiguration: ProvisionConfigDefault = ProvisionConfigDefault()
    alarms: List[dict] = []

    @pydantic.validator("alarms", pre=True)
    def alarms_none_to_empty_list(  # pylint: disable=no-self-argument
        cls, v
    ) -> Optional[List[dict]]:
        if v is None:
            return []
        return v


class DeviceProfile(DeviceProfileTypeDefault):
    id: Optional[GeneralId]
    tenantId: Optional[GeneralId]
    createdTime: int = int(time.time())
    name: str
    description: Optional[str]
    transportType: str = "DEFAULT"
    defaultRuleChainId: Optional[GeneralId]
    profileData: DeviceProfileData


class DeviceRelation(pydantic.BaseModel):
    """Device relation"""

    from_: GeneralId
    to: GeneralId
    type_: str
    typeGroup: str = "COMMON"
    additionalInfo: dict = {}

    @pydantic.root_validator()
    def rename_field(cls, values):  # pylint: disable=no-self-argument
        if "from_" in values:
            values["from"] = values["from_"]
            del values["from_"]
        if "type_" in values:
            values["type"] = values["type_"]
            del values["type_"]
        return values


class DeviceAttribute(pydantic.BaseModel):
    alarmAttribute: dict
    ruleChainAttribute: dict


class Device(pydantic.BaseModel):
    id: Optional[GeneralId]
    name: str
    label: Optional[str]
    deviceProfileId: Optional[GeneralId]
    createdTime: int = int(time.time())
    additionalInfo: Optional[dict] = {}
