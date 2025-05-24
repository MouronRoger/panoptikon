#!/usr/bin/env python3
"""Simple validation for knowledge graph relationships."""

from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any

MEMORY_PATH = Path(
    "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
)


def validate() -> bool:
    """Validate knowledge graph for consistency."""
    if not MEMORY_PATH.exists():
        print("Error: Knowledge graph not found")
        return False

    entities: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []
    entity_names: dict[str, set[str]] = defaultdict(set)  # name -> set of ids

    # Load all entries
    with open(MEMORY_PATH) as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                return False

            if entry.get("type") == "entity":
                eid = entry.get("id")
                name = entry.get("name")
                if eid:
                    entities[eid] = entry
                    if name:
                        entity_names[name].add(eid)
                else:
                    # Legacy entity without ID - use name as key
                    if name:
                        entities[name] = entry
            elif entry.get("type") == "relation":
                relations.append(entry)

    issues = []

    # Check for orphaned relationships
    for rel in relations:
        from_id = rel.get("from", "")
        to_id = rel.get("to", "")

        # Check if entities exist (by ID or name for legacy support)
        if from_id not in entities:
            issues.append(f"Orphaned relation: source '{from_id}' not found in {rel}")
        if to_id not in entities:
            issues.append(f"Orphaned relation: target '{to_id}' not found in {rel}")

    # Check for duplicate names with different IDs
    for name, ids in entity_names.items():
        if len(ids) > 1:
            issues.append(f"Duplicate entity name '{name}' with IDs: {ids}")

    # Report results
    print(f"Entities: {len(entities)}")
    print(f"Relations: {len(relations)}")

    if issues:
        print(f"\n❌ Validation failed with {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
        return False
    else:
        print("✅ All relationships valid")
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
