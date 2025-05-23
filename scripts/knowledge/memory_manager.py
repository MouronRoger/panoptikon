#!/usr/bin/env python3
"""CLI utility for direct memory manipulation: add/list/prune entities & relations."""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Optional

MEMORY_PATH = Path(
    os.getenv(
        "PANOPTIKON_MCP_MEMORY",
        "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl",
    )
)


def load_memory() -> list[dict[str, Any]]:
    """Load memory from the JSONL file."""
    if not MEMORY_PATH.exists():
        return []
    with open(MEMORY_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_memory(memory: list[dict[str, Any]]) -> None:
    """Save memory to the JSONL file."""
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        for entry in memory:
            f.write(json.dumps(entry) + "\n")


def add_entity(name: str, entity_type: str, observation: Optional[str] = None) -> None:
    """Add an entity to memory."""
    memory = load_memory()
    entity = {
        "type": "entity",
        "name": name,
        "entityType": entity_type,
        "observations": [observation] if observation else [],
    }
    memory.append(entity)
    save_memory(memory)
    print(f"Added entity: {name} ({entity_type})")


def add_relation(from_entity: str, to_entity: str, relation_type: str) -> None:
    """Add a relation to memory."""
    memory = load_memory()
    relation = {
        "type": "relation",
        "from": from_entity,
        "to": to_entity,
        "relationType": relation_type,
    }
    memory.append(relation)
    save_memory(memory)
    print(f"Added relation: {from_entity} -[{relation_type}]-> {to_entity}")


def list_entities() -> None:
    """List all entities in memory."""
    memory = load_memory()
    for entry in memory:
        if entry.get("type") == "entity":
            print(entry)


def list_relations() -> None:
    """List all relations in memory."""
    memory = load_memory()
    for entry in memory:
        if entry.get("type") == "relation":
            print(entry)


def prune_entity(name: str) -> None:
    """Remove an entity and its relations from memory."""
    memory = load_memory()
    new_memory = [
        e for e in memory if not (e.get("type") == "entity" and e.get("name") == name)
    ]
    new_memory = [
        e
        for e in new_memory
        if not (
            e.get("type") == "relation"
            and (e.get("from") == name or e.get("to") == name)
        )
    ]
    save_memory(new_memory)
    print(f"Pruned entity and relations: {name}")


def prune_relation(from_entity: str, to_entity: str, relation_type: str) -> None:
    """Remove a specific relation from memory."""
    memory = load_memory()
    new_memory = [
        e
        for e in memory
        if not (
            e.get("type") == "relation"
            and e.get("from") == from_entity
            and e.get("to") == to_entity
            and e.get("relationType") == relation_type
        )
    ]
    save_memory(new_memory)
    print(f"Pruned relation: {from_entity} -[{relation_type}]-> {to_entity}")


def main() -> None:
    """Parse CLI arguments and execute commands."""
    parser = argparse.ArgumentParser(description="Memory Manager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_entity_parser = subparsers.add_parser("add-entity")
    add_entity_parser.add_argument("name")
    add_entity_parser.add_argument("entity_type")
    add_entity_parser.add_argument("--observation", default=None)

    add_relation_parser = subparsers.add_parser("add-relation")
    add_relation_parser.add_argument("from_entity")
    add_relation_parser.add_argument("to_entity")
    add_relation_parser.add_argument("relation_type")

    subparsers.add_parser("list-entities")
    subparsers.add_parser("list-relations")

    prune_entity_parser = subparsers.add_parser("prune-entity")
    prune_entity_parser.add_argument("name")

    prune_relation_parser = subparsers.add_parser("prune-relation")
    prune_relation_parser.add_argument("from_entity")
    prune_relation_parser.add_argument("to_entity")
    prune_relation_parser.add_argument("relation_type")

    args = parser.parse_args()
    if args.command == "add-entity":
        add_entity(args.name, args.entity_type, args.observation)
    elif args.command == "add-relation":
        add_relation(args.from_entity, args.to_entity, args.relation_type)
    elif args.command == "list-entities":
        list_entities()
    elif args.command == "list-relations":
        list_relations()
    elif args.command == "prune-entity":
        prune_entity(args.name)
    elif args.command == "prune-relation":
        prune_relation(args.from_entity, args.to_entity, args.relation_type)


if __name__ == "__main__":
    main()
