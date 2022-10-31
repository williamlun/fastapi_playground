"""General Base Model of Schema"""
import abc
from typing import Dict, Optional, TypeVar, Generic, List
import requests
from loguru import logger

import internal_schema
import stores.chirpstack.conn_config
import exception

T = TypeVar("T", bound=internal_schema.ResourceBaseModel)
S = TypeVar("S", bound=internal_schema.IdBasedResourceModel)


class Resource(Generic[T], abc.ABC):
    """Resource Base Model"""

    _RESOURCE_NAME_IN_URL = ""
    _RESOURCE_NAME_IN_REQ = ""
    _limit = 999999999

    def __init__(self):
        self._conn_config = (
            stores.chirpstack.conn_config.ConnectionConfig.get_instance()
        )
        self._svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        jwt_token = self._conn_config.get_token()
        self._req_header = {
            "Accept": "application/json",
            "Grpc-Metadata-Authorization": f"Bearer {jwt_token}",
        }

    @abc.abstractmethod
    def create(self, item: T) -> str:
        pass

    @abc.abstractmethod
    def read(self) -> List[T]:
        pass

    def read_by_id(self, id_: str) -> Optional[T]:
        payload = self._read_by_id(id_)
        if payload is None:
            return None

        return self._rest_to_excel_format(payload)

    @abc.abstractmethod
    def update(self, item: T):
        pass

    def delete(self, name_or_id: str):
        pass

    @classmethod
    @abc.abstractmethod
    def _excel_to_rest_format(cls, item: T):
        pass

    @abc.abstractmethod
    def _rest_to_excel_format(self, item: Dict) -> T:
        pass

    def _create(self, item: Dict) -> str:
        response = requests.post(
            self._svc_url,
            headers=self._req_header,
            json={self._RESOURCE_NAME_IN_REQ: item},
        )
        return response.json()

    def _read_by_id(self, id_: str) -> Optional[Dict]:
        response = requests.get(
            f"{self._svc_url}/{id_}",
            headers=self._req_header,
        ).json()
        return response.get(self._RESOURCE_NAME_IN_REQ, None)

    def _read(self) -> Optional[List[Dict]]:
        response = requests.get(
            self._svc_url,
            headers=self._req_header,
            params={"limit": self._limit},
        ).json()
        return response["result"]

    def _update_by_id(self, id_: str, item: Dict):
        response = requests.put(
            f"{self._svc_url}/{id_}",
            headers=self._req_header,
            json={self._RESOURCE_NAME_IN_REQ: item},
        )
        if response.status_code >= 300:
            raise ValueError("Update Failed")

    def _delete_by_id(self, id_: str):
        response = requests.delete(f"{self._svc_url}/{id_}", headers=self._req_header)
        if response.status_code >= 300:
            raise ValueError("Delete Failed")


class IdBasedResource(Resource[S], abc.ABC):
    """Resource Model for ID Based Schema"""

    def create(self, item: S) -> str:
        result = self.read_by_id(item.get_id())
        if result:
            logger.info(f"{self.__class__.__name__} with ID {item.get_id()} existed")
            raise exception.ResourceAlreadyExistsError(
                f"{self.__class__.__name__} with ID {item.get_id()} existed"
            )
        logger.info(f"Creating {item.get_id()}")
        payload = self._excel_to_rest_format(item)
        return self._create(payload)

    def read(self) -> List[S]:
        result_list_dict = self._read()
        if result_list_dict is None:
            return []
        excel_schema_list = [
            self._rest_to_excel_format(result) for result in result_list_dict
        ]
        return excel_schema_list

    def update(self, item: S):
        result = self.read_by_id(item.get_id())
        if result is None:
            raise exception.ResourceNotFoundError(
                f"{self.__class__.__name__} with name {item.get_id()} not found"
            )
        logger.info(f"Updating {item.name}")
        payload = self._excel_to_rest_format(item)
        self._update_by_id(item.get_id(), payload)

    def delete(self, id_: str):  # pylint: disable=arguments-renamed
        self._delete_by_id(id_)


class NameBasedResource(Resource[T], abc.ABC):
    """Resource Model for Name Based Schema"""

    def create(self, item: T):
        result = self.read_by_name(item.name)
        if result:
            logger.info(f"{self.__class__.__name__} with ID {item.name} existed")
            raise exception.ResourceAlreadyExistsError(
                f"{self.__class__.__name__} with ID {item.name} existed"
            )
        logger.info(f"Creating {item.name}")
        payload = self._excel_to_rest_format(item)
        return self._create(payload)

    def read_by_name(self, name: str) -> Optional[T]:
        try:
            id_ = self.get_id_by_name(name)
            return self.read_by_id(id_)
        except exception.ResourceNotFoundError:
            return None

    def read(self) -> List[T]:
        result_list_dict = self._read()
        if result_list_dict is None:
            return []
        excel_schema_list = [
            self._rest_to_excel_format(result) for result in result_list_dict
        ]
        return excel_schema_list

    def update(self, item: T):
        logger.info(f"Updating {item.name}")
        id_ = self.get_id_by_name(item.name)
        payload = self._excel_to_rest_format(item)
        return self._update_by_id(id_, payload)

    def delete(self, name: str):  # pylint: disable=arguments-renamed
        id_ = self.get_id_by_name(name)
        return self._delete_by_id(id_)

    def get_id_by_name(self, name: str) -> str:
        response = requests.get(
            f"{self._svc_url}",
            headers=self._req_header,
            params={"limit": self._limit},
        ).json()
        for result in response["result"]:
            if result["name"] == name:
                return result["id"]

        raise exception.ResourceNotFoundError(
            f"{self.__class__.__name__} with name {name} not found"
        )
