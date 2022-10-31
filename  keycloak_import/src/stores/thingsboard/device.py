"""Thingsboard Device Related Module"""
# pylint: disable=invalid-name
from typing import Optional
from loguru import logger

import requests

import exception
import internal_schema
import stores.thingsboard.conn_config
import stores.thingsboard.rest_schema
import stores.thingsboard.device_profile


class Device(stores.thingsboard.base.Resource[internal_schema.Device]):
    """Device resource store class"""

    _RESOURCE_NAME_IN_URL = "device"
    _RESOURCE_NAME_IN_URL_READ = "tenant/devices"

    def create(self, item: internal_schema.Device) -> None:
        device = self.read_by_name(item.name)
        if device is not None:
            logger.info(f"Device with name {item.name} already exists")
            raise exception.ResourceAlreadyExistsError(
                f"Device with name {item.name} already exists"
            )
        logger.info(f"Creating device {item.name}")
        attribute_list = {}
        if item.thingsboard.alarms_attribute is not None:
            attribute_list.update(item.thingsboard.alarms_attribute)
        attribute_list["ruleChainAttribute"] = item.thingsboard.rule_chain_attribute
        self._create_or_update_device(item)
        self._create_or_update_relations(item.thingsboard.relations)
        general_id = self.get_id_by_name(item.name)
        self._create_or_update_attribute(general_id.id, attribute_list)

    def read_by_id(self, entity_id: str) -> Optional[internal_schema.Device]:
        device = self._read_device(entity_id)
        if device is None or device.deviceProfileId is None:
            return None

        relations = self._read_relations(entity_id)
        attributes = self._read_attributes(entity_id)
        relations_list = []
        for item in relations:
            relations_list.append(
                internal_schema.Device.InThingsboard.Relation(
                    from_device=self._read_device(getattr(item, "from").id).name,
                    to_device=self._read_device(getattr(item, "to").id).name,
                    type=getattr(item, "type"),
                )
            )

        if attributes["ruleChainAttribute"] is None:
            attributes["ruleChainAttribute"] = {}
        thingsboard_device = internal_schema.Device.InThingsboard(
            alarms_attribute=attributes,
            rule_chain_attribute=attributes["ruleChainAttribute"],
            relations=relations_list,
        )

        device_profile = stores.thingsboard.device_profile.DeviceProfile().read_by_id(
            device.deviceProfileId.id
        )
        if device_profile is None:
            raise exception.ResourceNotFoundError(
                f"Device profile with id {device.deviceProfileId.id} not found but it links to device {device.name}."
            )
        return internal_schema.Device(
            name=device.name,
            device_profile=device_profile.name,
            thingsboard=thingsboard_device,
        )

    def read_by_name(self, name: str) -> Optional[internal_schema.Device]:
        try:
            general_id = self.get_id_by_name(name)
            return self.read_by_id(general_id.id)
        except exception.ResourceNotFoundError:
            return None

    def update(self, item: internal_schema.Device) -> None:
        logger.info(f"Updating device {item.name}")

        general_id = self.get_id_by_name(item.name)
        attribute_list = {}
        for (
            attribute_key,
            attribute_value,
        ) in item.thingsboard.alarms_attribute.items():
            attribute_list[attribute_key] = attribute_value
        attribute_list["ruleChainAttribute"] = item.thingsboard.rule_chain_attribute

        self._create_or_update_device(item)
        self._delete_relations(general_id.id)
        self._create_or_update_relations(item.thingsboard.relations)
        self._create_or_update_attribute(general_id.id, attribute_list)

    def delete(self, entity_id: str) -> None:
        raise NotImplementedError

    def get_id_by_name(
        self, name: str
    ) -> stores.thingsboard.rest_schema.general.GeneralId:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL_READ)
        response = requests.get(
            svc_url,
            headers=self._req_header,
            params={"deviceName": name},
        )
        if response.status_code == 404:
            raise exception.ResourceNotFoundError(f"Device with name {name} not found")
        elif response.status_code != 200:
            raise exception.StoresError(response.text)
        if response.status_code == 200:
            item = response.json()

        if item["name"] == name:
            return stores.thingsboard.rest_schema.general.GeneralId(**item["id"])
        raise exception.ResourceNotFoundError(f"Device with name {name} not found")

    def _create_or_update_device(self, item: internal_schema.Device):
        device = stores.thingsboard.rest_schema.device_related.Device(
            name=item.name,
            deviceProfileId=stores.thingsboard.device_profile.DeviceProfile().get_id_by_name(
                item.deviceProfile
            ),
            additionalInfo=item.thingsboard.additionalInfo,
        )
        try:
            # do update
            general_id = self.get_id_by_name(item.name)
            original_device = self._read_device(general_id.id)
            original_device.name = device.name
            original_device.deviceProfileId = device.deviceProfileId
        except exception.ResourceNotFoundError:
            # do create
            logger.info(f"Create device {item.name}")
            pass

        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        requests.post(svc_url, headers=self._req_header, json=device.dict())

    def _read_device(
        self, entity_id: str
    ) -> stores.thingsboard.rest_schema.device_related.Device:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.get(
            f"{svc_url}/{entity_id}", headers=self._req_header
        ).json()

        if "status" in response and response["status"] >= 300:
            raise exception.StoresError(response.text)

        return stores.thingsboard.rest_schema.device_related.Device(**response)

    def _delete_device(self, entity_id: str):
        pass

    def _create_or_update_relations(
        self, relations: list[internal_schema.Device.InThingsboard.Relation]
    ):
        url = self._conn_config.get_url("relation")
        for relation in relations:
            src = self.get_id_by_name(relation.from_device).id
            trg = self.get_id_by_name(relation.to_device).id

            req_body = stores.thingsboard.rest_schema.device_related.DeviceRelation(
                from_=stores.thingsboard.rest_schema.general.GeneralId(
                    id=src,
                    entityType=stores.thingsboard.rest_schema.general.GeneralId.EntityType.DEVICE,
                ),
                to=stores.thingsboard.rest_schema.general.GeneralId(
                    id=trg,
                    entityType=stores.thingsboard.rest_schema.general.GeneralId.EntityType.DEVICE,
                ),
                type_=relation.type,
            )
            response = requests.post(
                url, headers=self._req_header, json=req_body.dict()
            )

            try:
                if "status" in response and response["status"] >= 300:
                    raise exception.StoresError(response["message"])
            except requests.exceptions.JSONDecodeError:
                pass

    def _read_relations(
        self, entity_id: str
    ) -> list[stores.thingsboard.rest_schema.device_related.DeviceRelation]:
        url = self._conn_config.get_url("relations")
        req_body = {
            "filters": [{"entityTypes": ["DEVICE"]}],
            "parameters": {
                "rootId": entity_id,
                "rootType": "DEVICE",
                "direction": "FROM",
                "relationTypeGroup": "COMMON",
                "maxLevel": 0,
                "fetchLastLevelOnly": False,
            },
        }
        response = requests.post(url, headers=self._req_header, json=req_body).json()

        if "status" in response and response["status"] >= 300:
            raise exception.StoresError(response["message"])

        for item in response:
            if "from" in item:
                item["from_"] = item["from"]
                del item["from"]
            if "type" in item:
                item["type_"] = item["type"]
                del item["type"]
        relations = response

        return [
            stores.thingsboard.rest_schema.device_related.DeviceRelation(**relation)
            for relation in relations
        ]

    def _delete_relations(self, entity_id: str):
        url = self._conn_config.get_url("relations")
        response = requests.delete(
            url,
            headers=self._req_header,
            params={"entityId": entity_id, "entityType": "DEVICE"},
        )

        try:
            if "status" in response and response["status"] >= 300:
                raise exception.StoresError(response.json()["message"])
        except requests.exceptions.JSONDecodeError:
            pass

    def _create_or_update_attribute(self, entity_id: str, attributes: dict):
        url = self._conn_config.get_url("plugins/telemetry")
        response = requests.post(
            f"{url}/{entity_id}/SERVER_SCOPE",
            headers=self._req_header,
            json=attributes,
        )

        try:
            if "status" in response and response["status"] >= 300:
                raise exception.StoresError(response.text)
        except requests.exceptions.JSONDecodeError:
            pass

    def _read_attributes(self, entity_id: str) -> dict:
        url = self._conn_config.get_url("plugins/telemetry")
        response = requests.get(
            f"{url}/DEVICE/{entity_id}/values/attributes/SERVER_SCOPE",
            headers=self._req_header,
        ).json()

        if "status" in response and response["status"] >= 300:
            raise exception.StoresError(response.text)

        attribute_in_dict = {item["key"]: item["value"] for item in response}

        if "ruleChainAttribute" not in attribute_in_dict:
            attribute_in_dict["ruleChainAttribute"] = None

        return attribute_in_dict

    def _update_attribute(self, item_id: str, attr: dict):
        svc_url = self._conn_config.get_url("plugins/telemetry")
        response = requests.post(
            f"{svc_url}/{item_id}/SERVER_SCOPE",
            headers=self._req_header,
            json=attr,
        ).json()

        if "status" in response and response["status"] >= 300:
            raise exception.StoresError(response.text)

    def _delete_attribute(self, entity_id: str, keys: list[str]):
        pass

    def read_credentials_by_id(self, id_: str):
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.get(
            f"{svc_url}/{id_}/credentials", headers=self._req_header
        )
        if response.status_code >= 300:
            raise exception.StoresError(response.text)
        response = response.json()
        if response["credentialsType"] == "ACCESS_TOKEN":
            return response["credentialsId"]
        raise exception.ResourceNotFoundError(f"credentials of {id_} not found")
