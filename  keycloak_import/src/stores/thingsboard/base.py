"""General Base Model"""

import abc
from typing import Generic, TypeVar, Optional

import pydantic

import stores.thingsboard.conn_config
import stores.thingsboard.rest_schema
import stores.thingsboard.rest_schema.general

T = TypeVar("T", bound=pydantic.BaseModel)


class Resource(abc.ABC, Generic[T]):
    """Base class of resource store class"""

    _RESOURCE_NAME_IN_URL = ""
    _RESOURCE_NAME_IN_URL_READ = ""

    def __init__(self):
        super().__init__()
        self._conn_config = (
            stores.thingsboard.conn_config.ConnectionConfig.get_instance()
        )
        token = self._conn_config.get_token()
        self._req_header = {
            "accept": "application/json",
            "X-Authorization": f"Bearer {token}",
        }

    @abc.abstractmethod
    def create(self, item: T):
        pass

    @abc.abstractmethod
    def read_by_id(self, entity_id: str) -> Optional[T]:
        pass

    @abc.abstractmethod
    def read_by_name(self, name: str) -> Optional[T]:
        pass

    @abc.abstractmethod
    def update(self, item: T):
        pass

    @abc.abstractmethod
    def delete(self, entity_id: str):
        pass

    @abc.abstractmethod
    def get_id_by_name(
        self, name: str
    ) -> stores.thingsboard.rest_schema.general.GeneralId:
        pass
