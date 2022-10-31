"""graph DB Node related module"""

import neo4j.graph

import stores.neo4j.base
import graphdb_schema


class Field(stores.neo4j.base.ResourceBase[graphdb_schema.Field]):
    """Field resource store class"""

    def _node_to_internal_format(self, node: neo4j.graph.Node) -> graphdb_schema.Field:

        pass
