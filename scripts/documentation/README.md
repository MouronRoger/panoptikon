# Panoptikon Documentation System

## Overview

The Panoptikon project uses a unified documentation system that integrates with Qdrant for semantic search and the MCP server for AI access.

## Directory Structure

```
scripts/
├── documentation/         # AI documentation tools
│   ├── ai_docs.py        # Main AI documentation interface
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
