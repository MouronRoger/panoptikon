# Documentation System Scripts

This directory contains scripts for managing the Panoptikon knowledge system.

## 🎯 Knowledge System Architecture

**Core Components (in order of authority):**
1. **📄 Markdown Files** (`/docs/*`) - The canonical source of truth
2. **🧠 MCP Knowledge Graph** (`memory.jsonl`) - Relational knowledge from documentation
3. **📝 Session Logs** (`ai_docs.md`) - Project history and decisions

**Supporting Tool:**
- **🔍 Qdrant** - Semantic search index (NOT the source of truth!)

## Main AI Documentation System

- **ai_docs.py**: The main entry point for the AI-accessible documentation system.
  - Creates and updates Markdown files (the actual knowledge)
  - Automatically triggers Qdrant indexing for search
  - Provides all documentation management functions

  Example usage:
  ```python
  from scripts.documentation.ai_docs import *
  
  # Read from Markdown files (the truth)
  doc = read_documentation("components", "MyComponent")
  
  # Search using Qdrant (just helps find docs)
  results = search_documentation("current phase status")
  
  # Update Markdown documentation
  update_phase_progress("Phase 4", status="In Progress", ...)
  ```

## Migration and Utility Scripts

- `migrate_kg_to_docs.py`: Migrate knowledge graph data to documentation format.
- `simple_migrate.py`, `migrate_complete.py`: Additional migration utilities.
- `record_transition.py`: Log and record phase/stage transitions.

## Notes

- **Markdown files in `/docs` are the canonical source** - everything else derives from them
- **MCP Knowledge Graph** is built from the Relationships sections in documentation
- **Qdrant is just for search** - never treat search results as authoritative
- Always read the actual Markdown files for truth

## Directory Structure

```
scripts/
├── documentation/         # AI documentation tools
│   ├── ai_docs.py        # Main AI documentation interface
│   ├── dual_reindex.py   # Dual re-index: Qdrant (semantic search) + KG (JSON-LD export)
│   ├── record_transition.py
│   ├── migrate_kg_to_docs.py
│   ├── migrate_complete.py
│   └── simple_migrate.py
│
└── qdrant/               # Qdrant indexing tools
    ├── index_docs.py     # Index documents
    ├── search_docs.py    # Search interface
    ├── manage.py         # Collection management
    └── test_mcp.py       # MCP testing

docs.py                   # Main CLI interface
```

## Quick Start

Use the main CLI interface for all documentation operations:

```bash
# Index all documentation
python docs.py index

# Search documentation
python docs.py search "connection pool"

# Check status
python docs.py status

# Migrate from knowledge graph
python docs.py migrate
```

## AI Documentation Interface

For AI/programmatic access:

```python
from scripts.documentation.ai_docs import *

# Create documentation
create_documentation(
    category="components",
    title="MyComponent",
    content="# Component Documentation...",
    tags=["core", "feature"]
)

# Search
results = search_documentation("database query")

# Update progress
update_phase_progress("Phase 4", status="Complete")
```

## Qdrant Integration

- **Collection**: `panoptikon`
- **Cloud Instance**: Configured automatically
- **Vector Model**: all-MiniLM-L6-v2
- **Dimensions**: 384

## Manual Operations

For advanced operations, use the scripts directly:

```bash
# Using the Qdrant wrapper
cd scripts/qdrant
./qdrant.sh index
./qdrant.sh search "query"
./qdrant.sh manage info

# Direct script usage
python scripts/documentation/ai_docs.py
python scripts/qdrant/index_docs.py
```

## Key Features

1. **Unified Collection**: All docs use `panoptikon` collection
2. **Automatic Indexing**: AI docs automatically index on create/update
3. **MCP Compatible**: Full integration with MCP server
4. **Semantic Search**: Powered by Qdrant cloud instance

## Documentation Categories & Enforcement

All documentation is organized into the following categories, which are strictly enforced by the documentation system (`ai_docs.py`). Any attempt to use an invalid category will result in an error.

| Category      | Directory         | Description                                      |
|--------------|-------------------|--------------------------------------------------|
| architecture  | docs/architecture | System and software architecture docs            |
| components    | docs/components   | Documentation for individual components/modules   |
| phases        | docs/phases       | Project phase and subphase documentation         |
| testing       | docs/testing      | Test plans, coverage, and testing docs           |
| api           | docs/api          | API documentation and references                 |
| guides        | docs/guides       | How-to guides and tutorials                      |
| decisions     | docs/decisions    | Architecture Decision Records (ADRs)             |
| progress      | docs/progress     | Progress tracking and milestone documentation    |

See `docs/README.md` for a full mapping and onboarding guide.

## Onboarding for New Contributors

- Always use a valid category when creating or updating documentation.
- Place new documentation files in the correct subdirectory under `docs/`.
- Use the provided Python API or CLI for all documentation operations.
- If unsure, use the `list_valid_categories()` function or consult the AI assistant.

## Dual System Updates

- **dual_reindex.py**: Updates BOTH systems from documentation:
  - Rebuilds Qdrant search index from Markdown files
  - Exports knowledge graph (JSON-LD) from documentation relationships
  - Run after major documentation updates to sync both systems

## Knowledge Graph Management

See `/scripts/knowledge/` for MCP knowledge graph tools:
- **memory_manager.py** - Direct knowledge graph manipulation
- **relationship_extractor.py** - Extract relationships from docs
- **doc_lint.py** - Ensure docs have proper relationship sections

## Metadata Audit & Fix

- `audit_fix_metadata.py`: Audits the Qdrant collection for points missing required metadata (title, path, document). Attempts to fix them by re-parsing the corresponding markdown file and updating the point. Ensures all entries are MCP-compatible. Run this script after major doc changes or re-indexing to guarantee MCP compatibility.
