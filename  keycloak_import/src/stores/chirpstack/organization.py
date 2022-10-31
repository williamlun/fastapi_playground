"""Organization Class Module"""
from typing import Dict

import internal_schema
import stores.chirpstack.base


class Organization(
    stores.chirpstack.base.NameBasedResource[internal_schema.Organization]
):
    """Implementation of Organization"""

    _RESOURCE_NAME_IN_URL = "organizations"
    _RESOURCE_NAME_IN_REQ = "organization"

    @classmethod
    def _excel_to_rest_format(cls, item: internal_schema.Organization) -> Dict:
        return item.dict()

    def _rest_to_excel_format(self, item: Dict) -> internal_schema.Organization:
        return internal_schema.Organization(**item)
