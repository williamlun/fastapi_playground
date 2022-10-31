"""Application Class Module"""
from typing import Dict, List

import internal_schema
import stores.chirpstack.base
import stores.chirpstack.organization
import stores.chirpstack.service_profile
import exception
from loguru import logger


class Application(
    stores.chirpstack.base.NameBasedResource[internal_schema.Application]
):
    """Implementation of Application"""

    _RESOURCE_NAME_IN_URL = "applications"
    _RESOURCE_NAME_IN_REQ = "application"

    def create(self, item: internal_schema.Application):
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
    def _excel_to_rest_format(cls, item: internal_schema.Application) -> Dict:
        payload = item.dict()
        org_store = stores.chirpstack.organization.Organization()
        org_id = org_store.get_id_by_name(item.organization)
        svc_store = stores.chirpstack.service_profile.ServiceProfile()
        svc_id = svc_store.get_id_by_name(item.serviceProfile)

        payload.update(
            {
                "organizationID": org_id,
                "serviceProfileID": svc_id,
            }
        )
        payload.pop("organization")
        payload.pop("serviceProfile")
        return payload

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.Application:
        org = stores.chirpstack.organization.Organization().read_by_id(
            item["organizationID"]
        )
        svc = stores.chirpstack.service_profile.ServiceProfile().read_by_id(
            item["serviceProfileID"]
        )

        if org is None:
            raise exception.ResourceNotFoundError("Organization not found")
        if svc is None:
            raise exception.ResourceNotFoundError("ServiceProfile not found")

        item.update({"organization": org.name, "serviceProfile": svc.name})

        return internal_schema.Application(**item)

    def raw_read(self) -> List[Dict]:
        result = self._read()
        if result is None:
            raise exception.ResourceNotFoundError("Application not found")
        return result
