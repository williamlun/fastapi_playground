"""Device Profile Class Module"""
from typing import Dict

import os
import internal_schema
import stores.chirpstack.base
import stores.chirpstack.network_server
import stores.chirpstack.organization
import exception
from loguru import logger


class DeviceProfile(
    stores.chirpstack.base.NameBasedResource[internal_schema.DeviceProfile]
):
    """Implementation of DeviceProfile"""

    _RESOURCE_NAME_IN_URL = "device-profiles"
    _RESOURCE_NAME_IN_REQ = "deviceProfile"

    def create(self, item: internal_schema.DeviceProfile):
        if item.name == "Manthink-GDOx11":
            logger.info("skip for device profile: Manthink-GDOx11")
            return "skip for device profile: Manthink-GDOx11"
        result = self.read_by_name(item.name)
        if result:
            logger.info(f"{self.__class__.__name__} with ID {item.name} existed")
            raise exception.ResourceAlreadyExistsError(
                f"{self.__class__.__name__} with ID {item.name} existed"
            )
        logger.info(f"Creating {item.name}")
        payload = self._excel_to_rest_format(item)
        return self._create(payload)

    @classmethod
    def _excel_to_rest_format(cls, item: internal_schema.DeviceProfile) -> Dict:
        assert item.chirpstack
        payload = item.chirpstack.dict()
        payload["name"] = item.name
        ns_store = stores.chirpstack.network_server.NetworkServer()
        ns_id = ns_store.get_id_by_name(item.chirpstack.networkServer)
        org_store = stores.chirpstack.organization.Organization()
        org_id = org_store.get_id_by_name(item.chirpstack.organization)

        payload.update(
            {
                "networkServerID": ns_id,
                "organizationID": org_id,
            }
        )
        payload.pop("networkServer")
        payload.pop("organization")

        if payload["payloadCodec"] == "None":
            return payload

        # Load Codec Script
        for key, default_script_path in [
            ("payloadDecoderScript", "codex/BRAND-MODEL/decode.js"),
            ("payloadEncoderScript", "codex/BRAND-MODEL/encode.js"),
        ]:
            codec_script_path = "../" + payload[key]
            script_str = ""
            if not os.path.exists(codec_script_path):
                codec_script_path = "../" + default_script_path

            try:
                with open(codec_script_path, "r", encoding="utf8") as script:
                    for line in script:
                        if "module.exports = " in line:
                            break
                        script_str += line
                payload[key] = script_str
            except IOError as exc:
                raise exception.DecodingScriptNotFoundError(
                    f"{codec_script_path} not found"
                ) from exc

        return payload

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.DeviceProfile:
        ns = stores.chirpstack.network_server.NetworkServer().read_by_id(
            item["networkServerID"]
        )
        org = stores.chirpstack.organization.Organization().read_by_id(
            item["organizationID"]
        )

        if ns is None:
            raise exception.ResourceNotFoundError("Network Server not found")
        if org is None:
            raise exception.ResourceNotFoundError("Organzation not found")

        item.update({"networkServer": ns.name, "organization": org.name})
        device_name = item.pop("name")
        chirpstack_device = internal_schema.DeviceProfile.InChirpstack(**item)
        return internal_schema.DeviceProfile(
            name=device_name, chirpstack=chirpstack_device
        )
