"""Gateway Class Module"""
from typing import Dict

import internal_schema
import stores.chirpstack.base
import stores.chirpstack.gateway_profile
import stores.chirpstack.network_server
import stores.chirpstack.organization
import stores.chirpstack.service_profile
import exception


class Gateway(stores.chirpstack.base.IdBasedResource[internal_schema.Gateway]):
    """Implementation of Gateway"""

    _RESOURCE_NAME_IN_URL = "gateways"
    _RESOURCE_NAME_IN_REQ = "gateway"

    @classmethod
    def _excel_to_rest_format(cls, item: internal_schema.Gateway) -> Dict:
        payload = item.dict()
        gw_store = stores.chirpstack.gateway_profile.GatewayProfile()
        gw_id = gw_store.get_id_by_name(item.gatewayProfile)
        ns_store = stores.chirpstack.network_server.NetworkServer()
        ns_id = ns_store.get_id_by_name(item.networkServer)
        org_store = stores.chirpstack.organization.Organization()
        org_id = org_store.get_id_by_name(item.organization)
        svc_store = stores.chirpstack.service_profile.ServiceProfile()
        svc_id = svc_store.get_id_by_name(item.serviceProfile)

        payload.update(
            {
                "gatewayProfileID": gw_id,
                "networkServerID": ns_id,
                "organizationID": org_id,
                "serviceProfileID": svc_id,
            }
        )
        payload["location"] = {}
        payload.pop("gatewayProfile")
        payload.pop("networkServer")
        payload.pop("organization")
        payload.pop("serviceProfile")
        return payload

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.Gateway:
        gw = stores.chirpstack.gateway_profile.GatewayProfile().read_by_id(
            item["gatewayProfileID"]
        )
        ns = stores.chirpstack.network_server.NetworkServer().read_by_id(
            item["networkServerID"]
        )
        org = stores.chirpstack.organization.Organization().read_by_id(
            item["organizationID"]
        )
        svc = stores.chirpstack.service_profile.ServiceProfile().read_by_id(
            item["serviceProfileID"]
        )

        if gw is None:
            raise exception.ResourceNotFoundError("Gateway Profile not found")
        if ns is None:
            raise exception.ResourceNotFoundError("Network Server not found")
        if org is None:
            raise exception.ResourceNotFoundError("Organization not found")
        if svc is None:
            raise exception.ResourceNotFoundError("Service Profile not found")

        item.update(
            {
                "gatewayProfile": gw.name,
                "networkServer": ns.name,
                "organization": org.name,
                "serviceProfile": svc.name,
            }
        )
        return internal_schema.Gateway(**item)
