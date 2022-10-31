"""graphdb client"""

from typing import Optional
import neo4j
import neo4j.exceptions
import neo4j.graph


class GdbClient:
    """Client"""

    _instance: Optional["GdbClient"] = None

    def __init__(self, uri: str, username: str, password: str):
        self.driver: Optional[neo4j.Driver] = neo4j.GraphDatabase.driver(
            uri, auth=(username, password)
        )
        GdbClient._instance = self

    @classmethod
    def get_instance(cls) -> "GdbClient":
        if cls._instance is None:
            raise Exception("GdbClient is not initialized!")
        return cls._instance

    def __enter__(self):
        self.session = self.driver.session()
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self.session.close()

    def __del__(self):
        self.driver.close()
