"""Thingsboard Device Profile Module"""
import json
import uuid
from loguru import logger
from string import Template
from typing import Optional

import exception
import internal_schema
import requests

import stores.thingsboard.base
import stores.thingsboard.conn_config
import stores.thingsboard.device_profile
import stores.thingsboard.rule_chain
import stores.thingsboard.rest_schema


class DeviceProfile(stores.thingsboard.base.Resource[internal_schema.DeviceProfile]):
    """Device profile resource store class"""

    _RESOURCE_NAME_IN_URL = "deviceProfile"
    _RESOURCE_NAME_IN_URL_READ = "deviceProfiles"

    def create(self, item: internal_schema.DeviceProfile) -> None:
        device_profile = self.read_by_name(item.name)
        if device_profile is not None:
            logger.info(f"Device profile with name {item.name} already exists")
            raise exception.ResourceAlreadyExistsError(
                f"Device profile with name {item.name} already exists"
            )
        logger.info(f"Creating device profile {item.name}")
        device_profile_rest = self._internal_to_rest_format_create(item)
        self._create_or_update_device_profile(device_profile_rest)

    def read_by_id(self, entity_id: str) -> Optional[internal_schema.DeviceProfile]:
        try:
            device_profile = self._read_device_profile(entity_id)
        except (exception.StoresError, exception.ResourceNotFoundError):
            logger.exception(f"Failed to read Device Profile with id {entity_id}")
            return None

        alarms_list = [
            internal_schema.Alarm(
                type=alarm["alarmType"],
                # NOTE Only one severity per alarm rules in this moment
                severity=list(alarm["createRules"].keys())[0],
            )
            for alarm in device_profile.profileData.alarms
        ]

        if device_profile.defaultRuleChainId is None:
            return internal_schema.DeviceProfile(
                name=device_profile.name,
                alarms=alarms_list,
            )

        return internal_schema.DeviceProfile(
            name=device_profile.name,
            rule_chain=stores.thingsboard.rule_chain.RuleChain().read_by_id(
                device_profile.defaultRuleChainId.id
            ),
            alarms=alarms_list,
        )

    def read_by_name(self, name: str) -> Optional[internal_schema.DeviceProfile]:
        try:
            general_id = self.get_id_by_name(name)
            return self.read_by_id(general_id.id)
        except (LookupError, exception.ResourceNotFoundError):
            return None

    def update(self, item: internal_schema.DeviceProfile) -> None:
        logger.info(f"Updating Device profile {item.name}")
        device_profile = self.read_by_name(item.name)
        if device_profile is None:
            raise ValueError(f"Device profile with name {item.name} does not exists")

        device_profile_rest = self._internal_to_rest_format_update(item)
        self._create_or_update_device_profile(device_profile_rest)

    def delete(self, entity_id: str) -> None:
        try:
            self._delete_device_profile(entity_id)
        except (LookupError, exception.ResourceNotFoundError) as exc:
            raise ValueError(
                f"Failed to delete Device Profile with id {entity_id}"
            ) from exc

    def get_id_by_name(
        self, name: str
    ) -> stores.thingsboard.rest_schema.general.GeneralId:
        svc_url = self._conn_config.get_url("deviceProfiles")
        response = requests.get(
            f"{svc_url}",
            headers=self._req_header,
            params={"pageSize": 1, "page": 0, "textSearch": name},
        ).json()

        for result in response["data"]:
            if result["name"] == name:
                return stores.thingsboard.rest_schema.general.GeneralId(**result["id"])

        raise LookupError(f"Device Profile with name {name} not found")

    def _create_or_update_device_profile(
        self, item: stores.thingsboard.rest_schema.device_related.DeviceProfile
    ):
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.post(
            f"{svc_url}", headers=self._req_header, json=item.dict()
        ).json()

        if "status" in response and response["status"] >= 300:
            raise ValueError(response["message"])

    def _read_device_profile(
        self, entity_id: str
    ) -> stores.thingsboard.rest_schema.device_related.DeviceProfile:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.get(
            f"{svc_url}/{entity_id}", headers=self._req_header
        ).json()

        if "status" in response and response["status"] == 404:
            raise exception.ResourceNotFoundError(response["message"])
        elif "status" in response and response["status"] >= 300:
            raise exception.StoresError(response["message"])

        return stores.thingsboard.rest_schema.device_related.DeviceProfile(**response)

    def _delete_device_profile(self, entity_id: str) -> None:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.delete(
            f"{svc_url}/{entity_id}", headers=self._req_header
        ).json()

        if "status" in response and response["status"] == 404:
            raise LookupError(response["message"])
        elif "status" in response and response["status"] >= 300:
            raise exception.ResourceNotFoundError(response["message"])

    def _internal_to_rest_format_create(
        self, item: internal_schema.DeviceProfile
    ) -> stores.thingsboard.rest_schema.device_related.DeviceProfile:
        alarms = [
            self._internal_to_rest_format_alarm_json(alarm)
            for alarm in item.thingsboard.alarms
        ]

        device_profile_data = stores.thingsboard.rest_schema.device_related.DeviceProfile(
            name=item.name,
            defaultRuleChainId=stores.thingsboard.rule_chain.RuleChain().get_id_by_name(
                item.thingsboard.rule_chain
            ),
            profileData=stores.thingsboard.rest_schema.device_related.DeviceProfileData(
                alarms=alarms
            ),
        )
        return device_profile_data

    def _internal_to_rest_format_alarm_json(
        self, alarm_type: internal_schema.Alarm
    ) -> dict:
        split = alarm_type.type.split("_")
        alarm_prefix = split[0]
        operator = {
            "HIGH": "GREATER",
            "LOW": "LESS",
        }[split[1]]
        timeseries = split[-1]
        with open(
            f"./templates/alarms_rule/{alarm_prefix}.json",
            encoding="utf-8",
        ) as f:
            alarm_id = uuid.uuid4()
            alarm_template = Template(f.read())
            alarm_configs = json.loads(
                alarm_template.safe_substitute(
                    alarm_id=alarm_id,
                    alarm_type=alarm_type.type,
                    key=timeseries.lower(),
                    alarm_type_threshold="_".join(
                        [alarm_prefix, operator, timeseries, "THRESHOLD"]
                    ),
                    alarm_type_enabled="_".join(
                        [alarm_prefix, operator, timeseries, "ENABLED"]
                    ),
                    operator=operator,
                )
            )
        return alarm_configs

    def _internal_to_rest_format_update(
        self, item: internal_schema.DeviceProfile
    ) -> stores.thingsboard.rest_schema.device_related.DeviceProfile:
        alarms = [
            self._internal_to_rest_format_alarm_json(alarm)
            for alarm in item.thingsboard.alarms
        ]

        device_profile_id = self.get_id_by_name(item.name)
        device_profile_data = self._read_device_profile(device_profile_id.id)

        device_profile_data.name = item.name
        device_profile_data.defaultRuleChainId = (
            stores.thingsboard.rule_chain.RuleChain().get_id_by_name(
                item.thingsboard.rule_chain
            )
        )
        device_profile_data.profileData.alarms = alarms

        return device_profile_data
