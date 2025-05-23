"""Type-safe relationship extractor for Panoptikon documentation.

Parses markdown files, registers entities and relations in the MCP knowledge
graph NDJSON store while guaranteeing:
• Deterministic UUID-based entity identity.
• Normalised names (lower-cased, collapsed whitespace) to avoid duplicates.
• Idempotency – duplicate inserts are skipped.
• Dry-run mode for CI validation.

Usage:
    python relationship_extractor_typed.py <file1.md> <file2.md> ...
    python relationship_extractor_typed.py docs/**/*.md --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Optional

# Ensure the scripts package is importable when the script is executed directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # noqa: E402

from scripts.knowledge.models import (  # noqa: E402
    Entity,
    Relation,
    entity_id,
    normalize_name,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MEMORY_PATH = Path(
    os.getenv(
        "PANOPTIKON_MCP_MEMORY",
        "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl",
    )
)

RELATION_TYPES: dict[str, str] = {
    "Contains": "contains",
    "Belongs To": "belongs_to",
    "Depends On": "depends_on",
    "Used By": "used_by",
    "Implements": "implements",
    "Affects": "affects",
    "Precedes": "precedes",
    "Follows": "follows",
}


# ---------------------------------------------------------------------------
# Knowledge-graph manager
# ---------------------------------------------------------------------------


class KnowledgeGraphManager:
    """Wrapper around the NDJSON store providing caching & integrity checks."""

    def __init__(self, memory_path: Optional[Path] = None) -> None:
        self.memory_path = memory_path or DEFAULT_MEMORY_PATH
        self._entity_cache: dict[str, Entity] = {}
        self._relation_cache: set[tuple[str, str, str]] = set()
        self._entity_type_by_name: dict[str, str] = {}
        self._load_existing()

    # ------------------------------ Internals -----------------------------

    def _load_existing(self) -> None:
        """Load entities/relations from the NDJSON store into memory."""
        if not self.memory_path.exists():
            return

        with self.memory_path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("type") == "entity":
                    entity = (
                        Entity(**data)
                        if "id" in data
                        else Entity.from_raw(
                            data["name"],
                            data["entityType"],
                            data.get("observations", []),
                        )
                    )
                    self._entity_cache[entity.id] = entity
                    self._entity_type_by_name[entity.name] = entity.entityType
                elif data.get("type") == "relation":
                    self._relation_cache.add(
                        (
                            data.get("from", ""),
                            data.get("to", ""),
                            data.get("relationType", ""),
                        )
                    )

    # ---------------------------- Public helpers ---------------------------

    # Entities

    def add_entity(
        self,
        name: str,
        entity_type: str,
        observation: Optional[str] = None,
        *,
        dry_run: bool = False,
    ) -> None:
        """Insert an entity if it does not yet exist."""
        eid = entity_id(name, entity_type)
        if eid in self._entity_cache:
            print(f"  [Skip] Entity exists: {normalize_name(name)} ({entity_type})")
            return

        entity = Entity.from_raw(
            name, entity_type, [observation] if observation else []
        )
        if dry_run:
            print(f"  [DRY] Would add entity: {entity.name} ({entity.entityType})")
            return

        self._entity_cache[eid] = entity
        self._entity_type_by_name[entity.name] = entity.entityType
        with self.memory_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entity.to_jsonl_dict()) + "\n")
        print(f"  [Add] Entity: {entity.name} ({entity.entityType})")

    # Relations

    def add_relation(
        self,
        from_name: str,
        from_type: str,
        to_name: str,
        to_type: str,
        relation_type: str,
        *,
        dry_run: bool = False,
    ) -> None:
        """Insert a relation if not present (checks both ID- and name-level)."""
        from_id = entity_id(from_name, from_type)
        to_id = entity_id(to_name, to_type)
        key = (from_id, to_id, relation_type)
        key_legacy = (normalize_name(from_name), normalize_name(to_name), relation_type)

        if key in self._relation_cache or key_legacy in self._relation_cache:
            print(
                f"  [Skip] Relation exists: {normalize_name(from_name)} -[{relation_type}]-> "
                f"{normalize_name(to_name)}"
            )
            return

        relation = Relation(  # type: ignore[call-arg]
            from_id=from_id,
            to_id=to_id,
            relationType=relation_type,
        )
        if dry_run:
            print(
                f"  [DRY] Would add relation: {normalize_name(from_name)} -[{relation_type}]-> "
                f"{normalize_name(to_name)}"
            )
            return

        self._relation_cache.add(key)
        with self.memory_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(relation.to_jsonl_dict()) + "\n")
        print(
            f"  [Add] Relation: {normalize_name(from_name)} -[{relation_type}]-> "
            f"{normalize_name(to_name)}"
        )

    # Type inference for targets

    def infer_type(self, name: str) -> str:
        """Best-effort guess of entity type based on cache and heuristics."""
        normalised = normalize_name(name)
        if normalised in self._entity_type_by_name:
            return self._entity_type_by_name[normalised]
        if "phase" in normalised:
            return "Phase"
        if "decision" in normalised:
            return "Decision"
        return "Component"


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def path_entity_type(path: Path) -> str:
    """Infer entity type from documentation directory path."""
    parts = path.parts
    if "components" in parts:
        return "Component"
    if "decisions" in parts:
        return "Decision"
    if "phases" in parts:
        return "Phase"
    return "Unknown"


def extract_first_header(content: str, fallback: str) -> str:
    """Return the first level-1 markdown header as entity name (or fallback)."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else fallback.strip()


def valid_target(token: str) -> bool:
    """Whether *token* is a real target (non-empty, not comment, not dashes)."""
    token = token.strip()
    if not token:
        return False
    if re.fullmatch(r"\s*<!--.*-->\s*", token):
        return False
    if re.fullmatch(r"-+", token):
        return False
    return True


# ---------------------------------------------------------------------------
# Extraction driver
# ---------------------------------------------------------------------------


def process_file(
    path: Path, km: KnowledgeGraphManager, *, dry_run: bool = False
) -> None:
    """Extract entity + relations from a single markdown *path*."""
    print(f"\nProcessing: {path.relative_to(Path.cwd())}")
    if dry_run:
        print("  [DRY RUN]")

    entity_type = path_entity_type(path)
    content = path.read_text(encoding="utf-8")
    entity_name = extract_first_header(content, path.stem.replace("-", " "))

    # 1. Entity
    km.add_entity(entity_name, entity_type, dry_run=dry_run)

    # 2. Relationships section
    match_section = re.search(
        r"## Relationships.*?(?=^##|\Z)", content, re.DOTALL | re.MULTILINE
    )
    if not match_section:
        print("  [Info] No Relationships section found")
        return

    pairs = re.findall(
        r"^\s*-\s*\*\*(.*?)\*\*: \s*(.*)$", match_section.group(0), re.MULTILINE
    )
    for rel_type_raw, targets in pairs:
        rel_type = RELATION_TYPES.get(rel_type_raw.strip())
        if not rel_type:
            print(f"  [Warn] Unknown relation type: {rel_type_raw}")
            continue
        for target in re.split(r",\s*", targets):
            if not valid_target(target):
                continue
            target_type = km.infer_type(target)
            km.add_relation(
                entity_name,
                entity_type,
                target.strip(),
                target_type,
                rel_type,
                dry_run=dry_run,
            )


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main() -> None:  # noqa: D401
    """CLI wrapper around :pyfunc:`process_file`."""
    parser = argparse.ArgumentParser(description="Type-safe relationship extractor")
    parser.add_argument("files", nargs="+", help="Markdown files to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writes")
    args = parser.parse_args()

    km = KnowledgeGraphManager()
    for file_path in args.files:
        if file_path.endswith(".md"):
            process_file(Path(file_path), km, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
