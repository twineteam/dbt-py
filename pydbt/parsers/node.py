import typing as T

from dbt.contracts.results import NodeResult
from dbt.contracts.graph.nodes import (
    ParsedNode,
    SourceDefinition,
    GenericTestNode,
    SeedNode,
    SnapshotNode,
)

from dbt.contracts.graph.model_config import (
    SeedConfig,
    TestConfig,
    NodeConfig,
    SnapshotConfig,
)

from ..logger import GLOBAL_LOGGER as log


def _parse_node(node: ParsedNode) -> T.Dict[str, str]:
    parsed = dict(
        database=node.database.lower() if node.database is not None else "",
        schema=node.schema.lower(),
        path=node.path.lower(),
        name=node.name.lower(),
        resource_type=node.resource_type.lower(),
        package_name=node.package_name.lower(),
    )

    # only add tags when they exist
    if node.tags:
        parsed["tags"] = ", ".join(node.tags).lower()

    return parsed


def _parse_parsed_node(node: ParsedNode) -> T.Dict[str, str]:
    parsed = _parse_node(node)
    parsed["filename"] = node.original_file_path
    parsed["abs_path"] = f"{node.build_path}/{node.original_file_path}"
    return parsed


def _parse_parsed_source_node(node: SourceDefinition) -> T.Dict[str, str]:
    parsed = dict(
        database=node.database.lower() if node.database is not None else "",
        schema=node.schema.lower(),
        path=node.path.lower(),
        name=node.name.lower(),
        resource_type=node.resource_type.lower(),
        package_name=node.package_name.lower(),
    )
    parsed["filename"] = node.original_file_path
    parsed["abs_path"] = f"{node.path}/{node.original_file_path}"
    return parsed


# TO DO, not important
def _parse_seed_node_config(config: SeedConfig) -> T.Dict[str, str]:
    return {}


def _parse_test_node_config(config: TestConfig) -> T.Dict[str, str]:
    return dict(
        materialized=config.materialized.lower(),
    )


def _parse_snapshot_node_config(
    config: SnapshotConfig,
) -> T.Dict[str, str]:
    node_config = _parse_node_config(config)
    snapshot_config = dict(
        strategy=config.strategy.lower() if config.strategy is not None else "",
        unique_key=config.unique_key.lower() if config.unique_key is not None else "",
        updated_at=config.updated_at.lower() if config.updated_at is not None else "",
    )

    return {**node_config, **snapshot_config}


def _parse_node_config(config: NodeConfig) -> T.Dict[str, str]:
    return dict(
        materialized=config.materialized.lower(),
    )


def parse_node(result: NodeResult) -> T.Dict[str, str]:
    node = result.node
    config = {}

    log.info(type(node))
    # currently each config function returns the entire config
    # as dict, they are seperated out so we can omit unnecessary
    # values in the future
    if isinstance(node, SourceDefinition):
        log.info("parsing source definition node")
        parsed_node = _parse_parsed_source_node(node)
        return parsed_node

    parsed_node = _parse_parsed_node(node)
    if isinstance(node, SeedNode):
        log.debug("parsing seed node config")
        config = _parse_seed_node_config(node.config)
    elif isinstance(node, GenericTestNode):
        log.debug("parsing test node config")
        config = _parse_test_node_config(node.config)
    elif isinstance(node, SnapshotNode):
        log.debug("parsing snapshot node config")
        config = _parse_snapshot_node_config(node.config)
    else:
        log.debug("parsing default node config")
        config = _parse_node_config(node.config)

    return {**parsed_node, **config}
