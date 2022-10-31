"""Network Server Class Module"""
from typing import Dict

import internal_schema
import stores.chirpstack.base


class NetworkServer(
    stores.chirpstack.base.NameBasedResource[internal_schema.NetworkServer]
):
    """Implementation of NetworkServer"""

    _RESOURCE_NAME_IN_URL = "network-servers"
    _RESOURCE_NAME_IN_REQ = "networkServer"

    @classmethod
    def _excel_to_rest_format(cls, item: internal_schema.NetworkServer) -> Dict:
        return {
            "name": item.name,
            "server": f"{item.server}:{item.port}",
        }

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.NetworkServer:
        item["server"], item["port"] = item["server"].split(":")
        return internal_schema.NetworkServer(**item)
