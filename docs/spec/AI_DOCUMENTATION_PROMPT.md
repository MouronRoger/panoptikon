# AI Documentation System Prompt

## 🎯 Core Knowledge System Hierarchy

**The Panoptikon knowledge system has THREE core components (in order of authority):**

1. **📄 Markdown Documentation** (`/docs/*`) - The canonical source of truth
   - All project documentation lives here
   - Version controlled in Git
   - This is what you read for authoritative information

2. **🧠 MCP Knowledge Graph** (`memory.jsonl`) - The relational knowledge system
   - Tracks relationships between components (contains, depends on, etc.)
   - Built from the Relationships sections in documentation
   - Primary system for understanding project structure

3. **📝 Session Logs** (`docs/ai_docs.md`) - The project history
   - Chronicles all decisions, progress, and rationale
   - Tagged entries tracking evolution
   - Living record of development

**🔍 Qdrant is NOT part of the core system!**
- It's just a search tool to help find documentation
- Never treat Qdrant results as authoritative
- Always read the actual Markdown files

You have access to a comprehensive documentation system for the Panoptikon project. Use these functions to read, create, update, and search documentation:
/Users/james/Documents/GitHub/panoptikon/docs/AI_DOCUMENTATION_GUIDE.md
## Available Functions

```python
from scripts.documentation.ai_docs import *

# Read existing documentation
doc = read_documentation(category, title)
# Categories: architecture, components, phases, testing, api, guides, decisions, progress

# Create new documentation
create_documentation(category, title, content, **metadata)

# Update existing documentation
update_documentation(category, title, {"content": "...", "metadata": {...}})

# Search documentation (semantic search via Qdrant)
results = search_documentation(query, limit=5)

# Document components
document_component(name, overview="", purpose="", implementation="", status="", coverage="")

# Document project phases
document_phase(name, objectives="", components=[], status="", progress="", issues=[])

# Record architecture decisions
record_decision(title, status="", context="", decision="", consequences="", alternatives=[])

# Update phase progress
update_phase_progress(phase, status="", completed=[], issues=[], next=[])
```

## Usage Guidelines

1. **Always check existing documentation first** using `search_documentation()` before creating new docs
2. **Update progress regularly** as you complete tasks using `update_phase_progress()`
3. **Document new components** as you create them with `document_component()`
4. **Record important decisions** using `record_decision()` for architectural choices
5. **Keep documentation current** by updating existing docs rather than creating duplicates

## Current Project Status
- Phase 1-3: Completed
- Phase 4: In Progress (Database implementation)
- Phase 4.2: Completed (Connection pool tested)
- Phase 4.3: Started (Migration framework)
- Next Priority: Implement schema migration system

## Example Usage

```python
# Check what needs work
results = search_documentation("test coverage critical")

# Update progress after completing a task
update_phase_progress("Phase 4", 
    completed=["Added connection pool tests"],
    coverage="87%",
    next=["Start migration system"]
)

# Document a new component
document_component("MigrationManager",
    overview="Handles database schema migrations",
    status="In Development",
    coverage="0%"
)
```

Always maintain documentation as you work. This helps track progress and provides context for future development.

# AI Documentation Prompt

## Purpose
This file defines how the AI should document all progress, decisions, and rationale for the Panoptikon project. The AI should use this as a guide for writing and updating docs/ai_docs.md and for session context management.

## Session Workflow
- **At session start:**
  - Read the current phase/subphase from docs/spec/phases (Markdown files are truth!)
  - Read the latest entries from docs/ai_docs.md to understand history
  - Query the MCP knowledge graph to understand relationships
  - Use Qdrant search ONLY to find relevant docs, then read the actual files
- **During session:**
  - For every major action, decision, or milestone, prepare notes for ai_docs.md
  - Update Markdown documentation as the source of truth
  - Keep relationship sections current for the knowledge graph
- **At session end:**
  - Append a summary to docs/ai_docs.md using the template below
  - Ensure all documentation changes are in Markdown files
  - The knowledge graph will be updated from the documentation

## Entry Template
```
## [SYSTEM_TIMESTAMP] #phase4.2 #connection-pool #decision #todo
<!-- WARNING: Use actual system time, not AI-generated timestamp -->
<!-- Get timestamp with: from scripts.documentation.ai_docs import get_system_timestamp -->
- **Phase:** 4.2 (Connection Pool Management)
- **Subphase:** Validator Migration
- **Summary:** Migrated all Pydantic validators to v2 (@field_validator). Updated all tests and docs. No breaking changes.
- **Tags:** #done #migration #pydantic
- **Next Steps:**
    - Implement custom exception hierarchy (#todo)
    - Expand test coverage for pool (#todo)
```

## Tag List
- `#phaseX.Y` — Current phase/subphase (e.g., #phase4.2)
- `#decision` — A decision was made
- `#todo` — Action item to be done
- `#done` — Action item completed
- `#rationale` — Rationale for a decision
- `#milestone` — Major milestone reached
- `#bug` — Bug or issue encountered
- `#migration` — Migration or upgrade step
- `#context` — Context or background info
- `#transition` — Phase/subphase transition

## Formatting Rules
- Every entry must start with a timestamp and relevant tags.
- Use bullet points for summary, rationale, and next steps.
- Reference the current phase/subphase in every entry.
- If a new phase/subphase is started, log the transition with #transition.
- Keep entries concise but clear; use multiple tags as needed.

## Example Entry
```
## [2025-05-24 14:30] #phase4.2 #connection-pool #decision #done
<!-- NOTE: This timestamp should be generated from system time, not hardcoded -->
- **Phase:** 4.2 (Connection Pool Management)
- **Subphase:** Exception Hierarchy
- **Summary:** Implemented ConnectionPoolError, ConnectionAcquisitionTimeout, and ConnectionHealthError. Updated all pool code and tests to use new exceptions.
- **Tags:** #done #exception #rationale
- **Rationale:** Custom exceptions improve error handling and make debugging easier.
- **Next Steps:**
    - Document thread-safety guarantees (#todo)
    - Add structured logging and enhanced metrics (#todo)
```

## Updating docs/ai_docs.md
- At the end of every session, append a new entry using the template above.
- If a phase/subphase is completed or started, log the transition.
- If a #todo is completed, mark it as #done in the next entry.

## Documentation System Notes

- **Markdown files are created/updated through the AI documentation system**
- **Qdrant indexing happens automatically** (but it's just for search!)
- **The MCP knowledge graph is built from documentation relationships**
- **Never confuse Qdrant with the actual knowledge source**

**Remember the hierarchy:**
1. Markdown = Truth
2. MCP Knowledge Graph = Relationships  
3. Session Logs = History
4. Qdrant = Just a search helper

**Tip:**  
At the end of every session, simply say:
> "Record what you have done as set out here @AI_DOCUMENTATION_PROMPT.md and update the documentation."

Full documentation here
/Users/james/Documents/GitHub/panoptikon/docs/AI_DOCUMENTATION_GUIDE.md 
