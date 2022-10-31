"""Service Profile Class Module"""
from typing import Dict

import internal_schema
import stores.chirpstack.base
import stores.chirpstack.network_server
import stores.chirpstack.organization
import exception


class ServiceProfile(
    stores.chirpstack.base.NameBasedResource[internal_schema.ServiceProfile]
):
    """Implementation of ServiceProfile"""

    _RESOURCE_NAME_IN_URL = "service-profiles"
    _RESOURCE_NAME_IN_REQ = "serviceProfile"

    @classmethod
    def _excel_to_rest_format(cls, item: internal_schema.ServiceProfile) -> Dict:
        payload = item.dict()
        ns_store = stores.chirpstack.network_server.NetworkServer()
        ns_id = ns_store.get_id_by_name(item.networkServer)
        org_store = stores.chirpstack.organization.Organization()
        org_id = org_store.get_id_by_name(item.organization)

        payload.update(
            {
                "networkServerID": ns_id,
                "organizationID": org_id,
            }
        )
        payload.pop("networkServer")
        payload.pop("organization")
        return payload

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.ServiceProfile:
        ns = stores.chirpstack.network_server.NetworkServer().read_by_id(
            item["networkServerID"]
        )
        org = stores.chirpstack.organization.Organization().read_by_id(
            item["organizationID"]
        )

        if ns is None:
            raise exception.ResourceNotFoundError("Network Server not found")
        if org is None:
            raise exception.ResourceNotFoundError("Organization not found")

        item.update({"networkServer": ns.name, "organization": org.name})
        return internal_schema.ServiceProfile(**item)
