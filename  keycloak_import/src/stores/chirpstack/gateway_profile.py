"""Gateway Profile Class Module"""
from typing import Dict

import internal_schema
import stores.chirpstack.base
import stores.chirpstack.network_server
import exception


class GatewayProfile(
    stores.chirpstack.base.NameBasedResource[internal_schema.GatewayProfile]
):
    """Implementation of GatewayProfile"""

    _RESOURCE_NAME_IN_URL = "gateway-profiles"
    _RESOURCE_NAME_IN_REQ = "gatewayProfile"

    @classmethod
    def _excel_to_rest_format(cls, item: internal_schema.GatewayProfile) -> Dict:
        payload = item.dict()
        network_server_store = stores.chirpstack.network_server.NetworkServer()
        network_server_id = network_server_store.get_id_by_name(item.networkServer)

        payload["networkServerID"] = network_server_id
        payload.pop("networkServer")
        return payload

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.GatewayProfile:
        network_server = stores.chirpstack.network_server.NetworkServer().read_by_id(
            item["networkServerID"]
        )

        if network_server is None:
            raise exception.ResourceNotFoundError("Network Server not found")

        item["networkServer"] = network_server.name
        return internal_schema.GatewayProfile(**item)
