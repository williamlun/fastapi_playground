"""Thingsboard Rule Chain Module"""
import json
from string import Template
from typing import Optional, Tuple
from loguru import logger

import exception
import internal_schema
import requests

import stores.thingsboard.base
import stores.thingsboard.conn_config
import stores.thingsboard.rest_schema


class RuleChain(stores.thingsboard.base.Resource[internal_schema.RuleChain]):
    """Rule chain resource store class

    Rule Chain will only import/export with its `Name`.

    Rule Chain will be created with loading relevant metadata
    when it does not exist in Thingsboard, and updated with
    loading and updating relevant metadata only.
    """

    _RESOURCE_NAME_IN_URL = "ruleChain"
    _RESOURCE_NAME_IN_URL_READ = "ruleChains"
    _ROOT_RULE_CHAIN_TYPE = "org.thingsboard.rule.engine.flow.TbRuleChainInputNode"

    def create(self, item: internal_schema.RuleChain):

        rule_chain = self.read_by_name(str(item.name))
        if rule_chain is not None:
            logger.info(f"Rule chain with name {item.name} already exists")
            raise exception.ResourceAlreadyExistsError(
                f"Rule chain with name {item.name} already exists"
            )

        (
            rule_chain_rest,
            rule_chain_metadata_rest,
        ) = self._internal_to_rest_format_create(item)
        logger.info(f"Creating rule chain {item.name}")
        rule_chain_id = self._create_or_update_rule_chain(rule_chain_rest)
        rule_chain_metadata_rest.ruleChainId = rule_chain_id
        self._create_or_update_rule_chain_metadata(rule_chain_metadata_rest)

    def read_by_id(self, entity_id: str) -> Optional[internal_schema.RuleChain]:
        try:
            rule_chain_rest = self._read_rule_chain(entity_id)
            return internal_schema.RuleChain(name=rule_chain_rest.name)
        except exception.StoresError:
            logger.info(f"Rule Chain with id {entity_id} does not exist.")
            return None

    def read_by_name(self, name: str) -> Optional[internal_schema.RuleChain]:
        try:
            general_id = self.get_id_by_name(name)
            return self.read_by_id(general_id.id)
        except (LookupError, exception.StoresError):
            logger.info(f"Rule Chain with name {name} does not exist.")
            return None

    def update(self, item: internal_schema.RuleChain):
        logger.info(f"Updating rule chain {item.name}")
        result = self.read_by_name(str(item.name))
        if result is None:
            raise exception.ResourceNotFoundError(
                f"Rule chain with name {item.name} does not exist."
            )

        rule_chain_metadata_rest = self._internal_to_rest_format_update(item)
        self._create_or_update_rule_chain_metadata(rule_chain_metadata_rest)

    def delete(self, entity_id: str):
        try:
            self._delete_rule_chain(entity_id)
        except (LookupError, exception.ResourceNotFoundError) as exc:
            raise ValueError(
                f"Failed to delete Rule Chain with id {entity_id}"
            ) from exc

    def get_id_by_name(
        self, name: str
    ) -> stores.thingsboard.rest_schema.general.GeneralId:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL_READ)
        response = requests.get(
            svc_url,
            headers=self._req_header,
            params={"pageSize": 100, "page": 0, "textSearch": name},
        ).json()

        for rule_chain in response["data"]:
            if rule_chain["name"] == name:
                return stores.thingsboard.rest_schema.general.GeneralId(
                    **rule_chain["id"]
                )

        raise LookupError(f"Rule Chain with name {name} not found")

    def set_default_rule_chain(self, entity_id: str):
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.post(
            f"{svc_url}/{entity_id}/root",
            headers=self._req_header,
        )
        if response.status_code != 200:
            raise exception.StoresError(response.json())

    def _create_or_update_rule_chain(
        self, item: stores.thingsboard.rest_schema.rule_chain.RuleChain
    ) -> stores.thingsboard.rest_schema.general.GeneralId:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.post(
            svc_url, headers=self._req_header, json=item.dict(by_alias=True)
        ).json()

        if "status" in response and response["status"] >= 300:
            raise ValueError(response["message"])

        return stores.thingsboard.rest_schema.general.GeneralId(**response["id"])

    def _read_rule_chain(
        self, entity_id: str
    ) -> stores.thingsboard.rest_schema.rule_chain.RuleChain:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.get(
            f"{svc_url}/{entity_id}", headers=self._req_header
        ).json()

        if "status" in response and response["status"] == 404:
            raise exception.ResourceNotFoundError(response["message"])
        elif "status" in response and response["status"] >= 300:
            raise exception.StoresError(response["message"])

        return stores.thingsboard.rest_schema.rule_chain.RuleChain(**response)

    def _delete_rule_chain(self, entity_id: str):
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.delete(
            f"{svc_url}/{entity_id}", headers=self._req_header
        ).json()

        if "status" in response and response["status"] == 404:
            raise LookupError(response["message"])
        if "status" in response and response["status"] >= 300:
            raise exception.ResourceNotFoundError(response["message"])

    def _create_or_update_rule_chain_metadata(
        self, item: stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata
    ):
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        _ = requests.post(
            f"{svc_url}/metadata",
            headers=self._req_header,
            json=item.dict(by_alias=True),
        )

    def _read_rule_chain_metadata(
        self, item_id: str
    ) -> stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata:
        svc_url = self._conn_config.get_url(self._RESOURCE_NAME_IN_URL)
        response = requests.get(
            f"{svc_url}/{item_id}/metadata", headers=self._req_header
        ).json()

        if "status" in response and response["status"] >= 300:
            raise exception.StoresError(response["message"])
        return stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata(**response)

    def _delete_rule_chain_metadata(self, entity_id: str):
        return self._delete_rule_chain(entity_id)

    def _internal_to_rest_format_create(
        self, item: internal_schema.RuleChain
    ) -> Tuple[
        stores.thingsboard.rest_schema.rule_chain.RuleChain,
        stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata,
    ]:
        rule_chain_rest = stores.thingsboard.rest_schema.rule_chain.RuleChain(
            name=item.name,
            id=None,
            tenantId=None,
            configuration=None,
            firstRuleNodeId=None,
        )

        root_rule_chain_id = self.get_id_by_name(
            "SEND_EVENTS_TO_KAFKA"
            if item.name != "SEND_EVENTS_TO_KAFKA"
            else "Root Rule Chain"
        ).id

        with open(
            f"templates/rule_chains/{item.name}.json",
            encoding="utf-8",
        ) as f:
            substitute_args = {"root_rule_chain_id": root_rule_chain_id}

            if item.additional_config is not None:
                substitute_args.update(item.additional_config.dict())

            rule_chain_template = Template(f.read())
            template_string = rule_chain_template.safe_substitute(**substitute_args)

            metadata_template = json.loads(template_string)

            rule_chain_metadata_rest = stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata(
                ruleChainId=None,
                firstNodeIndex=metadata_template["firstNodeIndex"],
                ruleChainConnections=metadata_template["ruleChainConnections"],
                nodes=[
                    stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata.RuleChainNodes(
                        **node
                    )
                    for node in metadata_template["nodes"]
                ],
                connections=[
                    stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata.NodeConnection(
                        **connection
                    )
                    for connection in metadata_template["connections"]
                ],
            )

            return rule_chain_rest, rule_chain_metadata_rest

    def _internal_to_rest_format_update(
        self, item: internal_schema.RuleChain
    ) -> stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata:
        rule_chain_id_entity = self.get_id_by_name(str(item.name))
        root_rule_chain_id = self.get_id_by_name(
            "SEND_EVENTS_TO_KAFKA"
            if item.name != "SEND_EVENTS_TO_KAFKA"
            else "Root Rule Chain"
        ).id
        with open(
            f"./templates/rule_chains/{item.name}.json",
            encoding="utf-8",
        ) as f:
            substitute_args = {
                "root_rule_chain_id": root_rule_chain_id,
                "rule_chain_id": rule_chain_id_entity.id,
            }
            if item.additional_config is not None:
                substitute_args.update(item.additional_config.dict())

            rule_chain_template = Template(f.read())
            template_string = rule_chain_template.safe_substitute(**substitute_args)
            metadata_template = json.loads(template_string)

            rule_chain_metadata_rest = stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata(
                ruleChainId=rule_chain_id_entity,
                firstNodeIndex=metadata_template["firstNodeIndex"],
                ruleChainConnections=metadata_template["ruleChainConnections"],
                nodes=[
                    stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata.RuleChainNodes(
                        **node
                    )
                    for node in metadata_template["nodes"]
                ],
                connections=[
                    stores.thingsboard.rest_schema.rule_chain.RuleChainMetadata.NodeConnection(
                        **connection
                    )
                    for connection in metadata_template["connections"]
                ],
            )

        return rule_chain_metadata_rest
