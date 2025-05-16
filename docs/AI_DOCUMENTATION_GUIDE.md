# AI Documentation Guide - Panoptikon

**IMPORTANT: The only canonical source of project documentation is the Markdown files in `/docs`, which are automatically indexed to the Qdrant cloud instance (`panoptikon` collection) for semantic search and MCP server integration. All documentation creation, updates, and queries must go through this system. Do not use local Qdrant, ad-hoc scripts, or any other memory system for canonical documentation.**

This guide provides comprehensive information about the Panoptikon documentation system, which uses Qdrant for semantic search and integrates with the MCP server.

## System Overview

The Panoptikon project uses a unified Qdrant-based documentation system for all documentation storage, indexing, and retrieval.

### Key Components

1. **Qdrant Cloud Instance**
   - **Collection Name**: `panoptikon` (unified for all documentation)
   - **Vector Model**: all-MiniLM-L6-v2 (384 dimensions)
   - **Vector Name** (for MCP): `fast-all-minilm-l6-v2`
   - **URL**: Configured in scripts

2. **Documentation Scripts**
   - **Primary Interface**: `/scripts/documentation/ai_docs.py`
     - Main AI-accessible interface for documentation
     - Automatically creates markdown files and indexes them in Qdrant
     - Provides functions for creating, updating, searching documentation
   
   - **Utility Scripts**: `/scripts/qdrant/`
     - `index_docs_mcp.py` - MCP-compatible indexing with named vectors (cloud only)
     - `test_mcp.py` - Test MCP integration
     - `qdrant.sh` - Wrapper script for all MCP-compatible operations

3. **MCP Server Integration**
   - Uses the `panoptikon` collection
   - Provides semantic search capabilities
   - Requires `document` field in payload
   - Syncs automatically when documents are created/updated

## Usage Examples

```python
# Import the documentation system
from scripts.documentation.ai_docs import *

# Create new documentation
create_documentation(
    category="components",
    title="Event Bus",
    content="# Event Bus\n\nThe event bus provides pub/sub communication...",
    tags=["core", "messaging"],
    status="completed"
)

# Read existing documentation
doc = read_documentation("components", "Event Bus")
print(doc['content'])

# Update documentation
update_documentation(
    category="components",
    title="Event Bus",
    updates={
        'content': "# Event Bus\n\nUpdated content...",
        'metadata': {'status': 'updated', 'version': '2.0'}
    }
)

# Search documentation using Qdrant semantic search
results = search_documentation("database connection pooling")
for result in results:
    print(f"{result['title']} - {result['score']}")

# Document a component
document_component(
    "ServiceContainer",
    overview="Dependency injection container",
    purpose="Manage service lifecycles",
    implementation="Uses singleton pattern",
    status="Completed",
    coverage="94%"
)

# Document a phase
document_phase(
    "Stage 4 - Database Implementation",
    objectives="Implement SQLite database layer",
    components=["Schema", "Connection Pool", "Migration System"],
    status="In Progress",
    progress="Stage 4.1 complete, 4.2 needs testing"
)

# Record an architecture decision
record_decision(
    "Use SQLite for Storage",
    status="Accepted",
    context="Need fast, embedded database",
    decision="Use SQLite with WAL mode",
    consequences="Single writer limitation",
    alternatives=["PostgreSQL", "LevelDB"]
)

# Update progress
update_phase_progress(
    "Stage 4",
    status="In Progress",
    completed=["Schema implementation", "Connection pool"],
    issues=["Missing test coverage"],
    next=["Write tests", "Start migration system"]
)
```

## Available Functions

All functions automatically sync with the Qdrant cloud instance:

1. `create_documentation(category, title, content, **metadata)` - Creates and indexes new docs
2. `read_documentation(category, title)` - Reads from local files
3. `update_documentation(category, title, updates)` - Updates and re-indexes docs
4. `search_documentation(query, limit=5)` - Semantic search via Qdrant
5. `document_component(name, **details)` - Create component documentation
6. `document_phase(name, **details)` - Create stage documentation
7. `record_decision(title, **decision_details)` - Create ADR (Architecture Decision Record)
8. `update_phase_progress(phase, **updates)` - Update stage progress tracking

## Document Categories

All documents are organized in these directories and indexed in Qdrant:

- `architecture` - System design documentation
- `components` - Individual component docs
- `phases` - Project phase documentation
- `testing` - Test plans and coverage
- `api` - API documentation
- `guides` - How-to guides
- `decisions` - Architecture Decision Records
- `progress` - Progress tracking

## Technical Configuration

### Qdrant Integration
- **Collection**: `panoptikon`
- **Cloud Instance**: Configured in scripts/documentation/ai_docs.py
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Automatic Indexing**: All documentation is automatically indexed on creation/update
- **Vector Configuration**: Named vectors for MCP compatibility

### Manual Operations

For manual operations, use the scripts in `scripts/qdrant/`:

```bash
# Index all documentation (MCP-compatible, cloud only)
cd scripts/qdrant
./qdrant.sh index

# Test MCP integration
./qdrant.sh test
```

## Important Notes

1. **Single Collection**: Everything uses the `panoptikon` collection
2. **No Local Qdrant**: Always use the cloud instance
3. **Automatic Indexing**: The ai_docs.py system automatically indexes on create/update
4. **MCP Compatible**: The system is fully integrated with the MCP server
5. **Document Field**: All indexed documents include a `document` field for MCP compatibility

## Migration Status

- ✅ All scripts updated to use `panoptikon` collection
- ✅ AI documentation interface updated
- ✅ Cursor rules updated
- ✅ Old references to `panoptikon_docs` removed
- ✅ Scripts consolidated in `/scripts/documentation/` and `/scripts/qdrant/`
- ✅ MCP integration working with proper `document` field

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
    ├── index_docs_mcp.py # MCP-compatible indexing
    ├── test_mcp.py       # MCP testing
    └── qdrant.sh         # Wrapper script
```

## Packaging for Other Projects

To use this documentation system in other projects:

1. Copy the `scripts/documentation/` and `scripts/qdrant/` directories
2. Update the Qdrant credentials and collection name in the scripts
3. Create the necessary documentation directories (`docs/architecture`, etc.)
4. Run `./qdrant.sh index` to start indexing documentation

The system is designed to be self-contained and easily portable to other repositories.

## Cleanup of Old Directories

After the migration to the unified system, these old directories can be removed:

```bash
# Remove old directories (manual action required)
rm -rf scripts/qdrant-utils/
rm -rf qdrant_storage/
```

## System Consolidation and Cleanup

The Panoptikon documentation system has undergone a full consolidation and migration to a unified, Qdrant-backed architecture. This section summarizes the actions taken, deprecated files, and next steps. This section supersedes the previous `CONSOLIDATION_SUMMARY.md` file.

### Actions Taken
- All documentation scripts and interfaces are now located in `scripts/documentation/` and `scripts/qdrant/`.
- The Qdrant collection name is standardized as `panoptikon`.
- All documentation is indexed and accessed via the unified Qdrant cloud instance.
- Redundant scripts and files have been removed or replaced by the new system.

### Deprecated/Removed Files
- `migrate_docs.py` (root) — replaced by new workflow
- `scripts/docs_pipeline.py` — replaced by new workflow
- `CONSOLIDATION_SUMMARY.md` — content merged here

### Next Steps
- Delete any remaining deprecated files listed above if present.
- Ensure `.DS_Store` and other OS metadata files are removed and ignored via `.gitignore`.
- Move technical notes (e.g., PyObjC typing) to `docs/guides/` or merge into onboarding documentation.
- Normalize filenames (e.g., remove leading `#` from `# Panoptikon Code Error Priority List.md`).

The system is now fully consolidated with a single approach to documentation management. Refer to this guide for all future documentation system questions.
