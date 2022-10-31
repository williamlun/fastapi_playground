"""Base model for graph DB"""
from typing import Any, Optional, TypeVar, Generic
import abc
import neo4j
import neo4j.exceptions
import neo4j.graph
import graphdb_schema
import stores.neo4j.gdb_client
from loguru import logger
import json

T = TypeVar("T", bound=graphdb_schema.BaseNode)


class Resource(Generic[T], abc.ABC):
    """Resource Class for graph DB"""

    def __init__(self):
        pass

    @staticmethod
    def _dict_to_keys(input_obj: dict[str, Any]) -> str:
        """
        >>> Resource._dict_to_keys({"field_a": "a", "fieldB": "B", "field_c": None})
        '{field_a: $field_a, fieldB: $fieldB}'
        >>> Resource._dict_to_keys({})
        ''
        """
        param_dict = {k: f"${k}" for k, v in input_obj.items() if v is not None}
        if not param_dict:
            return ""

        return json.dumps(param_dict).replace('"', "")

    def _run(self, query: str, item: Optional[dict] = None):
        with stores.neo4j.gdb_client.GdbClient.get_instance() as client:
            results = client.session.run(query, parameters=item)
            return results.values()

    @abc.abstractmethod
    def create(self, item: T):
        pass

    @abc.abstractmethod
    def merge_create(self, item: T):
        pass

    @abc.abstractmethod
    def read(self, item: T):
        pass

    @abc.abstractmethod
    def read_id(self, item: T) -> str:
        pass

    @abc.abstractmethod
    def update(self, cur_item: T, new_item: T):
        pass

    @abc.abstractmethod
    def delete(self, item: T):
        pass

    @abc.abstractmethod
    def _node_to_internal_format(self, node: neo4j.graph.Node) -> T:
        pass


class ResourceBase(Resource[T], abc.ABC):
    """Resource Base Class"""

    def create(self, item: T) -> neo4j.graph.Node:
        response = self._run(
            f"CREATE (n:{item.node_type}) {self._dict_to_keys(item.to_dict())}) RETURN id(n) AS node_id",
            item.to_dict(),
        )
        if len(response) != 1 and len(response[0]) != 1:
            raise RuntimeError("Create single must have exactly one item")
        return response[0][0]

    def merge_create(self, item: T) -> neo4j.graph.Node:
        # TODO: error handling of resource already exists
        logger.info(f"Creating resource: {item.name}")
        response = self._run(
            f"MERGE (n:{item.node_type.value} {self._dict_to_keys(item.to_dict())}) RETURN id(n) AS node_id",
            item.to_dict(),
        )
        if len(response) != 1 and len(response[0]) != 1:
            raise RuntimeError("Create single must have exactly one item")
        return response[0][0]

    def read(self, item: T) -> list[neo4j.graph.Node]:
        response = self._run(
            f"MATCH (n:{item.node_type.value} {self._dict_to_keys(item.to_dict())}) RETURN n",
            item.to_dict(),
        )
        return response

    def read_id(self, item: T) -> str:
        response = self._run(
            f"MATCH (n:{item.node_type.value} {self._dict_to_keys(item.to_dict())}) RETURN id(n) AS node_id",
            item.to_dict(),
        )
        if len(response) != 1 and len(response[0]) != 1:
            raise RuntimeError("Create single must have exactly one item")
        return response[0][0]

    def update(self, cur_item: T, new_item: T) -> neo4j.graph.Node:
        with stores.neo4j.gdb_client.GdbClient.get_instance() as client:
            node_id = self.read_id(cur_item)
        response = client.session.run(
            f"MATCH (n: {new_item.node_type.value}) WHERE id(n) = {node_id} SET n = $props RETURN n",
            props=new_item.to_dict(),
        )
        if len(response) != 1 and len(response[0]) != 1:
            raise RuntimeError("Create single must have exactly one item")
        return response[0][0]

    def delete(self, item: T):
        with stores.neo4j.gdb_client.GdbClient.get_instance() as client:
            client.session.run(
                f"MATCH (n:{item.node_type.value} {self._dict_to_keys(item.to_dict())}) DETACH DELETE n",
                item.to_dict(),
            )
