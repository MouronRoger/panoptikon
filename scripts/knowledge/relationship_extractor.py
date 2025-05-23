#!/usr/bin/env python3
"""Regex-based documentation extractor for relationships.

- Extracts the entity name from the first Markdown header (# ...).
- Adds entities and relations to the memory file.
- Skips relationship targets that are HTML comments (<!-- ... -->) or empty.
"""

import json
import os
from pathlib import Path
import re
from typing import Optional

MEMORY_PATH = Path(
    os.getenv(
        "PANOPTIKON_MCP_MEMORY",
        "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl",
    )
)

RELATION_TYPES = {
    "Contains": "contains",
    "Belongs To": "belongs_to",
    "Depends On": "depends_on",
    "Used By": "used_by",
    "Implements": "implements",
    "Affects": "affects",
    "Precedes": "precedes",
    "Follows": "follows",
}


def add_entity(name: str, entity_type: str, observation: Optional[str] = None) -> None:
    """Add an entity to memory."""
    entry = {
        "type": "entity",
        "name": name,
        "entityType": entity_type,
        "observations": [observation] if observation else [],
    }
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def add_relation(from_entity: str, to_entity: str, relation_type: str) -> None:
    """Add a relation to memory."""
    entry = {
        "type": "relation",
        "from": from_entity,
        "to": to_entity,
        "relationType": relation_type,
    }
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_entity_type(path: Path) -> str:
    """Infer entity type from file path."""
    if "components" in path.parts:
        return "Component"
    if "decisions" in path.parts:
        return "Decision"
    if "phases" in path.parts:
        return "Phase"
    return "Unknown"


def standardize_relation_type(rel_type: str) -> Optional[str]:
    """Standardize relation type string."""
    return RELATION_TYPES.get(rel_type.strip())


def extract_entity_name_from_content(content: str, fallback: str) -> str:
    """Extract the entity name from the first Markdown header (# ...), fallback to provided value."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback


def is_real_entity_name(target: str) -> bool:
    """Return True if the target is not an HTML comment, not empty, and not just dashes."""
    target = target.strip()
    if not target:
        return False
    # Match HTML comments with optional leading/trailing whitespace
    if re.fullmatch(r"\s*<!--.*-->\s*", target):
        return False
    # Skip targets that are just dashes (e.g., '--')
    if re.fullmatch(r"-+", target):
        return False
    return True


def extract_relationships_from_file(filepath: str) -> None:
    """Extract relationships from a markdown file and add to memory."""
    path = Path(filepath)
    entity_type = get_entity_type(path)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    entity_name = extract_entity_name_from_content(
        content, path.stem.replace("-", " ").title()
    )
    add_entity(entity_name, entity_type)
    rel_section = re.search(
        r"## Relationships.*?(?=^##|\Z)", content, re.DOTALL | re.MULTILINE
    )
    if not rel_section:
        return
    rel_lines = re.findall(
        r"^\s*-\s*\*\*(.*?)\*\*:\s*(.*)$", rel_section.group(0), re.MULTILINE
    )
    for rel_type, targets in rel_lines:
        std_type = standardize_relation_type(rel_type)
        if not std_type:
            continue
        for target in re.split(r",\s*", targets):
            if is_real_entity_name(target):
                add_relation(entity_name, target, std_type)


def main() -> None:
    """Extract relationships from all markdown files passed as arguments."""
    import sys

    for filepath in sys.argv[1:]:
        if filepath.endswith(".md"):
            extract_relationships_from_file(filepath)


if __name__ == "__main__":
    main()
