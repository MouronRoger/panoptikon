"""Typed CLI wrapper for knowledge-graph manipulation.

Offers the same UX as the legacy *memory_manager.py* but relies on the
:pyclass:`scripts.knowledge.relationship_extractor_typed.KnowledgeGraphManager`
for all operations, ensuring we use UUID-based identities and name
normalisation everywhere.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Ensure scripts package importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.knowledge.relationship_extractor_typed import (  # noqa: E402
    KnowledgeGraphManager,
)


def main() -> None:  # noqa: D401
    """CLI entry-point."""
    parser = argparse.ArgumentParser(description="Type-safe Memory Manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ----------------------------- add-entity -----------------------------
    add_ent = sub.add_parser("add-entity", help="Add an entity")
    add_ent.add_argument("name")
    add_ent.add_argument("entity_type")
    add_ent.add_argument("--observation", default=None)

    # ----------------------------- add-relation ---------------------------
    add_rel = sub.add_parser("add-relation", help="Add a relation")
    add_rel.add_argument("from_entity")
    add_rel.add_argument("to_entity")
    add_rel.add_argument("relation_type")
    add_rel.add_argument("--from-type", dest="from_type", default=None)
    add_rel.add_argument("--to-type", dest="to_type", default=None)

    sub.add_parser("list-entities", help="Print entities")
    sub.add_parser("list-relations", help="Print relations")

    args = parser.parse_args()
    km = KnowledgeGraphManager()

    if args.cmd == "add-entity":
        km.add_entity(args.name, args.entity_type, args.observation)
    elif args.cmd == "add-relation":
        src_type = args.from_type or km.infer_type(args.from_entity)
        tgt_type = args.to_type or km.infer_type(args.to_entity)
        km.add_relation(
            args.from_entity,
            src_type,
            args.to_entity,
            tgt_type,
            args.relation_type,
        )
    elif args.cmd == "list-entities":
        for ent in km._entity_cache.values():  # noqa: SLF001
            print(f"{ent.name} ({ent.entityType}) – {ent.id}")
    elif args.cmd == "list-relations":
        for fid, tid, rtype in km._relation_cache:  # noqa: SLF001
            print(f"{fid} -[{rtype}]-> {tid}")


if __name__ == "__main__":
    main()
