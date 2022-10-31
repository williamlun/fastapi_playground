"""Device Class Module"""
from typing import Dict, Tuple
from loguru import logger

import internal_schema
import stores.chirpstack.base
import stores.chirpstack.application
import stores.chirpstack.device_profile
import stores.chirpstack.rest_schema.device
import exception

import requests


class Device(stores.chirpstack.base.IdBasedResource[internal_schema.Device]):
    """Implementation of Device"""

    _RESOURCE_NAME_IN_URL = "devices"
    _RESOURCE_NAME_IN_REQ = "device"

    @classmethod
    def _excel_to_rest_format(
        cls, item: internal_schema.Device
    ) -> Tuple[Dict, Dict, Dict]:
        assert item.chirpstack
        app_store = stores.chirpstack.application.Application()
        app_id = app_store.get_id_by_name(item.chirpstack.application)
        device_store = stores.chirpstack.device_profile.DeviceProfile()
        device_profile_id = device_store.get_id_by_name(item.deviceProfile)

        device_dict = {
            "applicationID": app_id,
            "description": item.chirpstack.description,
            "devEUI": item.chirpstack.devEUI,
            "deviceProfileID": device_profile_id,
            "name": item.name,
            "variables": item.chirpstack.variables,
        }

        device_otaa = {
            "devEUI": item.chirpstack.devEUI,
            "nwkKey": item.chirpstack.OTAAkey,
            "appKey": "",
            "genAppKey": "",
        }

        device_abp = {
            "devEUI": item.chirpstack.devEUI,
            "devAddr": item.chirpstack.DeviceAddress,
            "appSKey": item.chirpstack.ApplicationSessionKey,
            "nwkSEncKey": item.chirpstack.NetworkSessionEncryptionKey,
            "sNwkSIntKey": item.chirpstack.ServingNetworkSessionIntegrityKey,
            "fNwkSIntKey": item.chirpstack.ForwardingNetworkSessionIntegrityKey,
        }

        return device_dict, device_otaa, device_abp

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.Device:

        otaa_dict = self.get_otaa(item["devEUI"])
        abp_dict = self.get_abp(item["devEUI"])

        item.update(
            {
                "application": item["applicationID"],
                "deviceProfile": item["deviceProfileID"],
                "OTAAkey": otaa_dict.nwkKey,
                "DeviceAddress": abp_dict.devAddr,
                "encryptionKey": abp_dict.nwkSEncKey,
                "ServingKey": abp_dict.sNwkSIntKey,
                "ForwardingKey": abp_dict.fNwkSIntKey,
                "sessionKey": abp_dict.appSKey,
            }
        )

        name = item.pop("name")
        return internal_schema.Device(name=name, chirpstack=item)

    def add_otaa(self, device_otaa: dict):
        url = self._svc_url + "/" + device_otaa["devEUI"] + "/keys"
        response = requests.post(
            url,
            headers=self._req_header,
            json={"deviceKeys": device_otaa},
        )
        return response.json()

    def get_otaa(self, eui: str) -> stores.chirpstack.rest_schema.device.DeviceOTAAKeys:
        url = self._svc_url + "/" + eui + "/keys"
        response = requests.get(
            url,
            headers=self._req_header,
        )
        if response.status_code != 200:
            return stores.chirpstack.rest_schema.device.DeviceOTAAKeys()
        return stores.chirpstack.rest_schema.device.DeviceOTAAKeys(
            **(response.json()["deviceKeys"])
        )

    def update_otaa(self, device_otaa: dict):
        url = self._svc_url + "/" + device_otaa["devEUI"] + "/keys"
        response = requests.put(
            url,
            headers=self._req_header,
            json={"deviceKeys": device_otaa},
        )
        return response.json()

    def add_abp(self, device_abp: dict):
        url = self._svc_url + "/" + device_abp["devEUI"] + "/activate"
        response = requests.post(
            url,
            headers=self._req_header,
            json={"deviceActivation": device_abp},
        )
        return response.json()

    def get_abp(self, eui: str) -> stores.chirpstack.rest_schema.device.DeviceABPKeys:
        url = self._svc_url + "/" + eui + "/activation"
        response = requests.get(
            url,
            headers=self._req_header,
        )
        if response.status_code != 200:
            return stores.chirpstack.rest_schema.device.DeviceABPKeys()
        return stores.chirpstack.rest_schema.device.DeviceABPKeys(
            **(response.json()["deviceActivation"])
        )

    def _create(self, item: Dict) -> str:
        response = requests.post(
            self._svc_url,
            headers=self._req_header,
            json={self._RESOURCE_NAME_IN_REQ: item},
        )
        return response.json()

    def create(self, item: internal_schema.Device) -> str:
        assert item.chirpstack
        if item.deviceProfile == "default":
            return "skip for device profile: default"
        if item.deviceProfile == "Manthink-GDOx11":
            return "skip for device profile: Manthink-GDOx11"
        result = self.read_by_id(item.chirpstack.get_id())
        if result:
            logger.info(
                f"{self.__class__.__name__} with ID {item.chirpstack.get_id()} existed"
            )
            raise exception.ResourceAlreadyExistsError(
                f"{self.__class__.__name__} with ID {item.chirpstack.get_id()} existed"
            )
        logger.info(f"Creating {item.name}")
        device_dict, device_otaa, device_abp = self._excel_to_rest_format(item)
        return_id = self._create(device_dict)
        if item.chirpstack.OTAAkey != "":
            self.add_otaa(device_otaa)
        if item.chirpstack.DeviceAddress != "":
            self.add_abp(device_abp)

        return return_id

    def update(self, item: internal_schema.Device):
        assert item.chirpstack
        result = self.read_by_id(item.chirpstack.get_id())
        if result is None:
            raise ValueError(
                f"{self.__class__.__name__} with ID {item.chirpstack.get_id()} not existed"
            )
        logger.info(f"Updating {item.name}")
        device_dict, device_otaa, device_abp = self._excel_to_rest_format(item)
        self._update_by_id(item.chirpstack.get_id(), device_dict)
        if item.chirpstack.OTAAkey != "":
            self.update_otaa(device_otaa)
        if item.chirpstack.DeviceAddress != "":
            self.add_abp(device_abp)
