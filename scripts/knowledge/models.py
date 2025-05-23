"""Type-safe Pydantic models, helpers and utilities for the Panoptikon knowledge
graph system.

The module centralises the following concerns:
1. Name normalisation and slug/UUID generation helpers.
2. `Entity` and `Relation` models with strict typing that round-trip to the
   NDJSON format expected by the MCP knowledge-graph server.
3. Convenience constructors (`from_raw`) and serialisers (`to_jsonl_dict`).

The implementation adheres to the project's formatting and linting rules:
• Black 88-column line length.
• isort "black" profile.
• Ruff clean under `ruff --fix`.
• mypy passes in `--strict` mode.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional
import uuid

from pydantic import BaseModel, Field, field_validator

__all__ = [
    "slugify",
    "normalize_name",
    "entity_id",
    "Entity",
    "Relation",
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def slugify(name: str) -> str:
    """Return a lowercase, hyphen-separated slug derived from *name*."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def normalize_name(name: str) -> str:
    """Normalise *name* by lower-casing and collapsing whitespace."""
    return " ".join(name.lower().split())


def entity_id(name: str, entity_type: str) -> str:
    """Return a deterministic UUID5 for an entity.

    The UUID is derived from the *entity_type* and *normalize_name(name)* so
    that entities with the same semantic identity always share the same ID.
    """
    normalised = normalize_name(name)
    key = f"{entity_type}:{normalised}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class Entity(BaseModel):
    """Knowledge-graph entity description."""

    type: Literal["entity"] = "entity"
    id: str
    name: str
    entityType: str
    observations: List[str] = Field(default_factory=list)

    # ------------------------------- Validators ---------------------------

    @field_validator("name", mode="before")
    @classmethod
    def _normalise_name_field(cls, value: str) -> str:  # noqa: D401
        """Ensure *name* is normalised consistently."""
        return normalize_name(value)

    # ------------------------- Convenience helpers ------------------------

    @classmethod
    def from_raw(
        cls, name: str, entity_type: str, observations: Optional[List[str]] = None
    ) -> Entity:
        """Create a new *Entity* instance from raw parameters."""
        obs = observations or []
        return cls(
            id=entity_id(name, entity_type),
            name=normalize_name(name),
            entityType=entity_type,
            observations=obs,
        )

    def to_jsonl_dict(self) -> Dict[str, Any]:
        """Serialise the entity to the JSONL structure used by MCP."""
        return {
            "type": self.type,
            "id": self.id,
            "name": self.name,
            "entityType": self.entityType,
            "observations": self.observations,
        }


class Relation(BaseModel):
    """Directional relationship between two entities."""

    type: Literal["relation"] = "relation"
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    relationType: str

    model_config = {
        "populate_by_name": True,
    }

    # ------------------------- Convenience helpers ------------------------

    def to_jsonl_dict(self) -> Dict[str, Any]:
        """Serialise the relation to the JSONL structure used by MCP."""
        return {
            "type": self.type,
            "from": self.from_id,
            "to": self.to_id,
            "relationType": self.relationType,
        }
