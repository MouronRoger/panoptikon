import tempfile
from pathlib import Path
from typing import Any

from relationship_extractor import (
    extract_relationships_from_file,
    get_entity_type,
    standardize_relation_type,
)


def test_extracts_relations(monkeypatch: Any) -> None:
    """Test that relationship extraction works as expected."""
    test_content = """# TestComponent

## Overview
Test content

## Relationships
- **Contains**: ComponentX, ComponentY
- **Depends On**: ComponentZ

## Status
Active
"""
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as tmp:
        tmp.write(test_content)
        tmp.flush()
        relations = []

        def mock_add_entity(
            name: str, entity_type: str, observation: Any = None
        ) -> None:
            pass

        def mock_add_relation(
            from_entity: str, to_entity: str, relation_type: str
        ) -> None:
            relations.append((from_entity, to_entity, relation_type))

        monkeypatch.setattr("relationship_extractor.add_entity", mock_add_entity)
        monkeypatch.setattr("relationship_extractor.add_relation", mock_add_relation)
        extract_relationships_from_file(tmp.name)
        assert len(relations) == 3
        assert ("TestComponent", "ComponentX", "contains") in relations
        assert ("TestComponent", "ComponentY", "contains") in relations
        assert ("TestComponent", "ComponentZ", "depends_on") in relations


def test_get_entity_type() -> None:
    """Test that entity type detection works correctly."""
    assert get_entity_type(Path("/docs/components/test.md")) == "Component"
    assert get_entity_type(Path("/docs/decisions/test.md")) == "Decision"


def test_standardize_relation_type() -> None:
    """Test that relation type standardization works correctly."""
    assert standardize_relation_type("Contains") == "contains"
    assert standardize_relation_type("Depends On") == "depends_on"
    assert standardize_relation_type("Unknown") is None
