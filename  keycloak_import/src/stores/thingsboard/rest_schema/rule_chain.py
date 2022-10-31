"""Rule Chain RESTful Schema"""
# pylint: disable=invalid-name

import pydantic
from typing import List, Optional

from stores.thingsboard.rest_schema.general import GeneralId


class RuleChain(pydantic.BaseModel):
    id: Optional[GeneralId]
    tenantId: Optional[GeneralId]
    name: str
    configuration: Optional[dict]
    firstRuleNodeId: Optional[GeneralId]
    type: str = "CORE"
    root: bool = False
    debugMode: bool = True


class RuleChainMetadata(pydantic.BaseModel):
    """RuleChain Metadata Schema"""

    class RuleChainNodes(pydantic.BaseModel):
        additionalInfo: dict
        id: Optional[GeneralId]
        ruleChainId: Optional[GeneralId]
        type: str
        name: str
        configuration: Optional[dict]
        debugMode: bool = False

    class NodeConnection(pydantic.BaseModel):
        fromIndex: int
        toIndex: int
        type: str

    ruleChainId: Optional[GeneralId]
    firstNodeIndex: Optional[int]
    nodes: List[RuleChainNodes]
    connections: List[NodeConnection]
    ruleChainConnections: Optional[str]
