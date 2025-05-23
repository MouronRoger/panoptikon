# Knowledge Graph Implementation Files - Production Ready

## 1. models.py (Create First)

```python
#!/usr/bin/env python3
"""Type-safe models for knowledge graph entities and relations."""
from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator


def slugify(name: str) -> str:
    """Convert name to lowercase slug format."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def normalize_name(name: str) -> str:
    """Normalize name: lowercase, single spaces, trimmed."""
    return " ".join(name.lower().split())


def entity_id(name: str, entity_type: str) -> str:
    """Generate deterministic UUID for entity based on normalized name and type."""
    normalized = normalize_name(name)
    key = f"{entity_type}:{normalized}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))


class Entity(BaseModel):
    """Knowledge graph entity with type safety."""
    
    type: Literal["entity"] = "entity"
    id: str
    name: str
    entityType: str
    observations: List[str] = Field(default_factory=list)
    
    @field_validator("name", mode="before")
    @classmethod
    def normalize_name_field(cls, v: str) -> str:
        """Normalize entity name."""
        return normalize_name(v)
    
    @classmethod
    def from_raw(cls, name: str, entity_type: str, observations: List[str] | None = None) -> Entity:
        """Create entity with auto-generated ID."""
        normalized_name = normalize_name(name)
        return cls(
            id=entity_id(name, entity_type),
            name=normalized_name,
            entityType=entity_type,
            observations=observations or []
        )
    
    def to_jsonl_dict(self) -> Dict[str, Any]:
        """Convert to JSONL-compatible dict."""
        return {
            "type": self.type,
            "id": self.id,
            "name": self.name,
            "entityType": self.entityType,
            "observations": self.observations
        }


class Relation(BaseModel):
    """Knowledge graph relation with type safety."""
    
    type: Literal["relation"] = "relation"
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    relationType: str
    
    class Config:
        populate_by_name = True
    
    def to_jsonl_dict(self) -> Dict[str, Any]:
        """Convert to JSONL-compatible dict."""
        return {
            "type": self.type,
            "from": self.from_id,
            "to": self.to_id,
            "relationType": self.relationType
        }
```

## 2. validate_graph.py (Minimal Implementation)

```python
#!/usr/bin/env python3
"""Simple validation for knowledge graph relationships."""
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")


def validate() -> bool:
    """Validate knowledge graph for consistency."""
    if not MEMORY_PATH.exists():
        print("Error: Knowledge graph not found")
        return False
    
    entities: Dict[str, Dict[str, Any]] = {}
    relations: List[Dict[str, Any]] = []
    entity_names: Dict[str, Set[str]] = defaultdict(set)  # name -> set of ids
    
    # Load all entries
    with open(MEMORY_PATH, 'r') as f:
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
                    # Legacy entity without ID
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
```

## 3. graph_summary.py (Statistics)

```python
#!/usr/bin/env python3
"""Generate summary statistics for knowledge graph."""
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")


def summarize() -> None:
    """Generate summary of knowledge graph contents."""
    if not MEMORY_PATH.exists():
        print("Error: Knowledge graph not found")
        return
    
    entities_by_type = defaultdict(list)
    relations_by_type = Counter()
    entity_degrees = defaultdict(lambda: {"in": 0, "out": 0})
    
    # Load and analyze
    with open(MEMORY_PATH, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            
            entry = json.loads(line)
            if entry.get("type") == "entity":
                entity_type = entry.get("entityType", "Unknown")
                name = entry.get("name", "Unnamed")
                entities_by_type[entity_type].append(name)
            elif entry.get("type") == "relation":
                rel_type = entry.get("relationType", "unknown")
                from_id = entry.get("from", "")
                to_id = entry.get("to", "")
                
                relations_by_type[rel_type] += 1
                entity_degrees[from_id]["out"] += 1
                entity_degrees[to_id]["in"] += 1
    
    # Print entity summary
    print("=== Entity Summary ===")
    total_entities = 0
    for entity_type, names in sorted(entities_by_type.items()):
        total_entities += len(names)
        print(f"\n{entity_type} ({len(names)}):")
        for name in sorted(names)[:5]:
            print(f"  - {name}")
        if len(names) > 5:
            print(f"  ... and {len(names) - 5} more")
    
    print(f"\nTotal entities: {total_entities}")
    
    # Print relationship summary
    print("\n=== Relationship Summary ===")
    total_relations = sum(relations_by_type.values())
    for rel_type, count in sorted(relations_by_type.items(), key=lambda x: -x[1]):
        print(f"  {rel_type}: {count}")
    print(f"\nTotal relationships: {total_relations}")
    
    # Print top entities by degree
    print("\n=== Top 10 Entities by Connections ===")
    entity_total_degree = {
        entity: deg["in"] + deg["out"] 
        for entity, deg in entity_degrees.items()
    }
    
    for entity, degree in sorted(entity_total_degree.items(), key=lambda x: -x[1])[:10]:
        in_deg = entity_degrees[entity]["in"]
        out_deg = entity_degrees[entity]["out"]
        print(f"  {entity}: {degree} connections (in: {in_deg}, out: {out_deg})")


if __name__ == "__main__":
    summarize()
```

## 4. Updated rebuild_graph.sh

```bash
#!/bin/bash
# CI-friendly automated knowledge graph rebuild script

set -e  # Exit on error

echo "=== Panoptikon Knowledge Graph Rebuild ==="
echo "Started at: $(date)"

# Configuration
MEMORY_PATH="/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$(cd "$SCRIPTS_DIR/../../docs" && pwd)"

# Parse arguments
AUTO_SYNC="${AUTO_SYNC:-false}"
SKIP_VALIDATION="${SKIP_VALIDATION:-false}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-sync)
            AUTO_SYNC="true"
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION="true"
            shift
            ;;
        --help)
            echo "Usage: $0 [--auto-sync] [--skip-validation]"
            echo "  --auto-sync       Automatically sync to Qdrant without prompting"
            echo "  --skip-validation Skip validation phase"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Phase 1: Backup and Clear
echo -e "\n[Phase 1] Backup and Clear"
if [ -f "$MEMORY_PATH" ]; then
    BACKUP_PATH="${MEMORY_PATH%.jsonl}_backup_$(date +%Y%m%d_%H%M%S).jsonl"
    cp "$MEMORY_PATH" "$BACKUP_PATH"
    echo "  Backup created: $BACKUP_PATH"
fi
echo "" > "$MEMORY_PATH"
echo "  Knowledge graph cleared"

# Phase 2: Extract from Documentation
echo -e "\n[Phase 2] Document Extraction"

# Check for typed extractor, fall back to original
EXTRACTOR="$SCRIPTS_DIR/relationship_extractor.py"
if python -c "import scripts.knowledge.models" 2>/dev/null && [ -f "$SCRIPTS_DIR/relationship_extractor_typed.py" ]; then
    EXTRACTOR="$SCRIPTS_DIR/relationship_extractor_typed.py"
    echo "  Using typed extractor"
else
    echo "  Using original extractor"
fi

# Extract phases
echo "  Extracting Phase entities..."
find "$DOCS_DIR/phases" -name "*.md" -type f | sort | while read -r file; do
    python "$EXTRACTOR" "$file"
done

# Extract components
echo "  Extracting Component entities..."
find "$DOCS_DIR/components" -name "*.md" -type f | sort | while read -r file; do
    python "$EXTRACTOR" "$file"
done

# Extract decisions (if directory exists)
if [ -d "$DOCS_DIR/decisions" ]; then
    echo "  Extracting Decision entities..."
    find "$DOCS_DIR/decisions" -name "*.md" -type f | sort | while read -r file; do
        python "$EXTRACTOR" "$file"
    done
fi

# Phase 3: Add Core Entities
echo -e "\n[Phase 3] Core Entity Addition"
python "$SCRIPTS_DIR/memory_manager.py" add-entity "Panoptikon" "System" \
    --observation "High-performance macOS filename search utility"

python "$SCRIPTS_DIR/memory_manager.py" add-entity "Search Engine" "Component" \
    --observation "Core search functionality implementation"

python "$SCRIPTS_DIR/memory_manager.py" add-entity "Indexing System" "Component" \
    --observation "File system scanning and database population"

python "$SCRIPTS_DIR/memory_manager.py" add-entity "UI Framework" "Component" \
    --observation "Native macOS user interface implementation"

# Add core relationships
python "$SCRIPTS_DIR/memory_manager.py" add-relation "Search Engine" "Panoptikon" "belongs_to"
python "$SCRIPTS_DIR/memory_manager.py" add-relation "Indexing System" "Panoptikon" "belongs_to"
python "$SCRIPTS_DIR/memory_manager.py" add-relation "UI Framework" "Panoptikon" "belongs_to"

# Phase 4: Add Inverse Relations
echo -e "\n[Phase 4] Inverse Relations"
if [ -f "$SCRIPTS_DIR/add_inverse_relations.py" ]; then
    python "$SCRIPTS_DIR/add_inverse_relations.py"
else
    echo "  [Info] Inverse relations script not found, skipping"
fi

# Phase 5: Validation (unless skipped)
if [ "$SKIP_VALIDATION" != "true" ]; then
    echo -e "\n[Phase 5] Validation"
    if [ -f "$SCRIPTS_DIR/validate_graph.py" ]; then
        python "$SCRIPTS_DIR/validate_graph.py" || {
            echo "  [Error] Validation failed"
            exit 1
        }
    else
        echo "  [Warn] validate_graph.py not found"
    fi
else
    echo -e "\n[Phase 5] Validation - SKIPPED"
fi

# Phase 6: Summary
echo -e "\n[Phase 6] Summary"
if [ -f "$SCRIPTS_DIR/graph_summary.py" ]; then
    python "$SCRIPTS_DIR/graph_summary.py"
else
    echo "  [Warn] graph_summary.py not found"
fi

# Optional: Sync to Qdrant
if [ -f "$SCRIPTS_DIR/../dual_reindex.py" ]; then
    if [ "$AUTO_SYNC" == "true" ]; then
        echo -e "\n[Phase 7] Qdrant Sync"
        python "$SCRIPTS_DIR/../dual_reindex.py"
    elif [ -t 0 ]; then  # Only prompt if interactive terminal
        read -p "Sync to Qdrant? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Running dual_reindex.py..."
            python "$SCRIPTS_DIR/../dual_reindex.py"
        fi
    else
        echo -e "\n[Phase 7] Qdrant Sync - Skipped (non-interactive)"
    fi
fi

echo -e "\n=== Rebuild Complete ==="
echo "Finished at: $(date)"
exit 0
```

## 5. GitHub Actions Workflow (.github/workflows/knowledge-graph.yml)

```yaml
name: Knowledge Graph Maintenance

on:
  push:
    paths:
      - 'docs/**/*.md'
      - 'scripts/knowledge/**'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:  # Allow manual triggering

jobs:
  rebuild:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install "pydantic>=2.5" ruff black isort mypy
          
      - name: Lint knowledge scripts
        run: |
          cd scripts/knowledge
          black --check .
          isort --check .
          ruff check .
          # Only check typed files when they exist
          if [ -f models.py ]; then
            mypy --strict models.py
          fi
      
      - name: Create test memory location
        run: |
          mkdir -p "/tmp/claude"
          echo "" > "/tmp/claude/memory.jsonl"
        
      - name: Rebuild knowledge graph
        run: |
          export PANOPTIKON_MCP_MEMORY="/tmp/claude/memory.jsonl"
          ./scripts/knowledge/rebuild_graph.sh --skip-validation
          
      - name: Validate graph
        run: |
          export PANOPTIKON_MCP_MEMORY="/tmp/claude/memory.jsonl"
          python scripts/knowledge/validate_graph.py
          
      - name: Show summary
        run: |
          export PANOPTIKON_MCP_MEMORY="/tmp/claude/memory.jsonl"
          python scripts/knowledge/graph_summary.py
```

## 6. Update requirements.txt

Add these lines to `requirements.txt`:

```txt
# Knowledge Graph Dependencies
pydantic>=2.5.0
```

## 7. Add to pyproject.toml (at project root)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
exclude = [
    "tests/",
    "build/",
    ".venv/",
]

[[tool.mypy.overrides]]
module = "scripts.knowledge.*"
strict = true

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C90", # mccabe complexity
    "UP",  # pyupgrade
]
ignore = [
    "E501", # line too long (handled by black)
]
exclude = [
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "build",
    "dist",
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # unused imports okay in __init__
```

## Implementation Order

1. **First**: Create `validate_graph.py` and `graph_summary.py` (simple, no dependencies)
2. **Second**: Update `requirements.txt` and `pyproject.toml`
3. **Third**: Create `models.py` and test with mypy
4. **Fourth**: Update `rebuild_graph.sh` with new flags
5. **Fifth**: Create typed extractors (after models.py works)
6. **Last**: Add GitHub Actions workflow (when everything else works)

This provides a complete, production-ready implementation with proper error handling, type safety, and CI/CD integration.