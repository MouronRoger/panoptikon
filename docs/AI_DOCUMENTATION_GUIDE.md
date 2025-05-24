# AI Documentation Guide - Panoptikon

## 🎯 Core Knowledge System Hierarchy

**The Panoptikon knowledge system consists of three core components:**

1. **📄 Markdown Documentation** (`/docs/*`) - The canonical source of truth
2. **🧠 MCP Knowledge Graph** (`memory.jsonl`) - The primary relational knowledge system
3. **📝 Session Logs** (`ai_docs.md`) - The project history and decision record

**Supporting Tools:**
- **🔍 Qdrant** - Semantic search index (helps find documentation, NOT the source of truth)
- **📊 Scripts** - Automation for indexing and relationship extraction

## ⚠️ CRITICAL: Understanding the System

**DO NOT confuse Qdrant with the core knowledge system!**
- Qdrant is ONLY for semantic search to help find relevant documentation
- The actual knowledge lives in the Markdown files and MCP knowledge graph
- Always treat `/docs/*` files as the canonical source
- The MCP knowledge graph tracks relationships between components
- Session logs track the evolution and decisions

## ⚠️ CRITICAL: Timestamp Requirements

**ALWAYS use system timestamps, NOT AI-generated timestamps!**

When recording documentation entries, session logs, or any dated entries:
- Use the actual system clock time
- Do NOT rely on AI's internal timestamp (which can hallucinate dates)
- Format: `[YYYY-MM-DD HH:MM]` using system time

Example:
```python
# CORRECT - uses system time
from datetime import datetime
timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M]")

# WRONG - AI might hallucinate this
timestamp = "[2025-05-24 14:30]"  # Don't hardcode!
```

This guide provides comprehensive information about the Panoptikon documentation system, which uses Qdrant for semantic search and integrates with the MCP server.

## System Overview

The Panoptikon project uses a multi-layered knowledge system:

### Primary Knowledge Layers

1. **Markdown Documentation** (`/docs/*`)
   - The canonical source of all project documentation
   - Organized by categories (architecture, components, phases, etc.)
   - Version controlled in Git
   - This is where the truth lives!

2. **MCP Knowledge Graph** 
   - Stores relationships between components (contains, depends on, etc.)
   - Built from the Relationships sections in documentation
   - Located at: `/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl`
   - Extracted and managed by scripts in `/scripts/knowledge/`

3. **Session Logs** (`docs/ai_docs.md`)
   - Chronicles all development decisions and progress
   - Tagged entries with phases, decisions, and rationale
   - The living history of the project

### Supporting Search Layer

**Qdrant Cloud Instance** (NOT the source of truth!)
- **Purpose**: Semantic search to help find relevant documentation
- **Collection**: `panoptikon` 
- **What it does**: Indexes documentation for AI-powered search
- **What it doesn't do**: Store the canonical knowledge (that's in Markdown files!)

### Key Components

1. **Documentation System** (`/scripts/documentation/`)
   - **ai_docs.py** - Main AI interface for creating/updating Markdown documentation
   - Creates files in `/docs/*` (the source of truth)
   - Automatically triggers Qdrant indexing for search
   
2. **Knowledge Graph System** (`/scripts/knowledge/`)
   - **memory_manager.py** - Manages the MCP knowledge graph (memory.jsonl)
   - **relationship_extractor.py** - Extracts relationships from docs to build the graph
   - **doc_lint.py** - Ensures documentation has proper relationship sections

3. **Search Support** (`/scripts/qdrant/`)
   - **dual_reindex.py** - Rebuilds both Qdrant search index AND exports knowledge graph
   - **qdrant.sh** - Wrapper for search operations
   - Remember: Qdrant is just for search, not storage!

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

These functions work with the core knowledge system:

### Documentation Management (Creates/Updates Markdown Files)
1. `create_documentation(category, title, content, **metadata)` - Creates new Markdown docs
2. `read_documentation(category, title)` - Reads from Markdown files (source of truth)
3. `update_documentation(category, title, updates)` - Updates Markdown files
4. `document_component(name, **details)` - Create component documentation
5. `document_phase(name, **details)` - Create stage documentation
6. `record_decision(title, **decision_details)` - Create ADR (Architecture Decision Record)
7. `update_phase_progress(phase, **updates)` - Update stage progress tracking

### Search Support (Uses Qdrant)
8. `search_documentation(query, limit=5)` - Semantic search to find relevant docs
   - This searches the Qdrant index, not the source files
   - Always verify results by reading the actual Markdown files

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
# Index all documentation and export KG (canonical, cloud only)
cd scripts/documentation
python dual_reindex.py
```

## Important Notes

### Core Knowledge System
1. **Markdown Files**: The only source of truth (`/docs/*`)
2. **MCP Knowledge Graph**: Primary relational knowledge (`memory.jsonl`)
3. **Session Logs**: Project history and decisions (`ai_docs.md`)

### Supporting Tools
4. **Qdrant Search**: Just helps find documentation (NOT authoritative)
5. **Automatic Indexing**: Creating/updating docs triggers search indexing
6. **Batch Operations**: `dual_reindex.py` rebuilds search AND exports knowledge graph

### Best Practices
- Always read from Markdown files for authoritative information
- Use search to find relevant docs, then read the actual files
- Keep relationship sections updated for the knowledge graph
- Use system timestamps (never AI-generated ones)
- The MCP knowledge graph is built from documentation relationships

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
- `index_docs_mcp.py` (scripts/qdrant/) — replaced by dual_reindex.py

### Next Steps
- Delete any remaining deprecated files listed above if present.
- Ensure `.DS_Store` and other OS metadata files are removed and ignored via `.gitignore`.
- Move technical notes (e.g., PyObjC typing) to `docs/guides/` or merge into onboarding documentation.
- Normalize filenames (e.g., remove leading `#` from `# Panoptikon Code Error Priority List.md`).

The system is now fully consolidated with a single approach to documentation management. Refer to this guide for all future documentation system questions.
