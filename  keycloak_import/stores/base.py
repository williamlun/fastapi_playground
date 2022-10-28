"""Base resource class"""

import abc
from typing import Optional, TypeVar, Generic
import requests
from loguru import logger
import json

import internal_schema
import stores.conn_config


T = TypeVar("T", bound=internal_schema.ImportModel)
S = TypeVar("S", bound=internal_schema.ClientBase)


class Resource(Generic[T], abc.ABC):
    """Base resource class"""

    _realm_ = ""

    def __init__(self):
        self._conn_config = stores.conn_config.ConnectionConfig.get_instance()
        self._svc_url = self._conn_config.get_url(self._realm_)
        jwt_token = self._conn_config.get_token()
        self._req_header = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def set_realm(cls, realm: str):
        cls._realm_ = realm

    @abc.abstractmethod
    def create(self, item: T) -> str:
        pass

    @abc.abstractmethod
    def read(self) -> list[T]:
        pass

    @abc.abstractmethod
    def update(self, item: T) -> str:
        pass

    @abc.abstractmethod
    def delete(self, identifier: str):
        pass

    def _create(self, item: dict) -> str:
        response = requests.post(
            self._svc_url, headers=self._req_header, data=json.dumps(item)
        )
        return response.status_code

    def _read(self, condition: dict) -> Optional[list[dict]]:
        response = requests.get(
            self._svc_url, headers=self._req_header, params=condition
        )
        return response.json()

    def _update_by_id(self, id_: str, item: dict) -> str:
        response = requests.put(
            f"{self._svc_url}/{id_}", headers=self._req_header, data=json.dumps(item)
        )
        if response.status_code >= 300:
            raise ValueError("Update Failed")
        return response.status_code

    def _delete_by_id(self, id_: str) -> str:
        response = requests.delete(f"{self._svc_url}/{id_}", headers=self._req_header)
        if response.status_code >= 300:
            raise ValueError("Delete Failed")
        return response.status_code


class RealmResource(Resource[T], abc.ABC):
    """a"""
