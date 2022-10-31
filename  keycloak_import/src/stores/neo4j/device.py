"""graph DB Node related module"""

import neo4j.graph

import stores.neo4j.base
import graphdb_schema
from loguru import logger


class Device(stores.neo4j.base.ResourceBase[graphdb_schema.Device]):
    """Device resource store class"""

    def _node_to_internal_format(self, node: neo4j.graph.Node) -> graphdb_schema.Device:

        pass

    def merge_create(self, item: graphdb_schema.Device) -> neo4j.graph.Node:
        # TODO: error handling of resource already exists
        logger.info(f"Creating resource: {item.name}")
        device_prop = item.to_dict(exclude={"relations"})
        response = self._run(
            f"MERGE (n:{item.node_type.value} "
            f"{self._dict_to_keys(device_prop)}) RETURN id(n) AS node_id",
            device_prop,
        )
        if len(response) != 1 and len(response[0]) != 1:
            raise RuntimeError("Create single must have exactly one item")
        device_id = response[0][0]

        for relation in item.relations:
            response = self._run(
                f"MATCH (f) WHERE id(f) = {device_id} "
                f"MATCH (t: {relation.to_node.node_type.value}) WHERE t.name = '{relation.to_node.name}' "
                f"MERGE (f)-[r:{relation.node_type.value} ]->(t) "
                f"RETURN r",
                {},
            )
            if len(response) != 1 and len(response[0]) != 1:
                raise RuntimeError("Create single must have exactly one item")
