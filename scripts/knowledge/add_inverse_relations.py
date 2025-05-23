"""Add missing inverse relationships to the knowledge-graph NDJSON store.

The mapping between a relation and its inverse is defined in *INVERSE_MAP*.
The script is idempotent – it reads the current store, determines which
inverse edges are absent and appends only those.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Set, Tuple

from scripts.knowledge.models import Relation

MEMORY_PATH = Path(
    "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
)

INVERSE_MAP = {
    "belongs_to": "contains",
    "contains": "belongs_to",
    "depends_on": "used_by",
    "used_by": "depends_on",
    "precedes": "follows",
    "follows": "precedes",
    "implements": "implemented_by",
    "implemented_by": "implements",
    "affects": "affected_by",
    "affected_by": "affects",
}


def add_inverses(memory_path: Path = MEMORY_PATH) -> None:  # noqa: D401
    """Append inverse relations to *memory_path* NDJSON store if missing."""
    if not memory_path.exists():
        print("Error: knowledge-graph memory file not found")
        return

    entries = [
        json.loads(line) for line in memory_path.read_text().splitlines() if line
    ]
    existing_rel: Set[Tuple[str, str, str]] = set()
    for e in entries:
        if e.get("type") == "relation":
            existing_rel.add(
                (e.get("from", ""), e.get("to", ""), e.get("relationType", ""))
            )

    new_relations: List[Relation] = []
    for src, tgt, rtype in existing_rel:
        inv_type = INVERSE_MAP.get(rtype)
        if not inv_type:
            continue
        if (tgt, src, inv_type) in existing_rel:
            continue
        new_relations.append(
            Relation(  # type: ignore[call-arg]
                from_id=tgt,
                to_id=src,
                relationType=inv_type,
            )
        )

    if not new_relations:
        print("No inverse relationships needed.")
        return

    with memory_path.open("a", encoding="utf-8") as fh:
        for rel in new_relations:
            fh.write(json.dumps(rel.to_jsonl_dict()) + "\n")

    print(f"Added {len(new_relations)} inverse relationships.")


if __name__ == "__main__":
    add_inverses()
