# MCP Knowledge Graph Reference Guide for Panoptikon

## Executive Summary

The Model Context Protocol (MCP) is an open standard developed by Anthropic that enables standardized communication between AI models and external tools/data sources. The `@itseasy21/mcp-knowledge-graph` server provides persistent memory capabilities through a local knowledge graph structure, allowing AI assistants to remember information across conversations.

**🚨 CRITICAL**: This is a living system requiring continuous maintenance. All timestamps MUST be system-generated - AI cannot accurately generate dates/times.

## 1. Understanding MCP (Model Context Protocol)

### 1.1 What is MCP?

MCP is like a "USB-C port for AI applications" - a universal standard that allows AI models to:
- Connect to external data sources and tools
- Maintain context across different systems
- Execute operations in a standardized way
- Replace fragmented integrations with a single protocol

### 1.2 Core Architecture

MCP follows a **client-server architecture** with three main components:

1. **MCP Host**: The main application (e.g., Claude Desktop, Cursor)
2. **MCP Client**: Protocol client embedded in the host, maintains 1:1 connections with servers
3. **MCP Server**: Lightweight programs exposing specific capabilities through MCP

### 1.3 How MCP Works

1. **Initialization**: Host creates MCP clients that handshake with servers
2. **Discovery**: Clients request available capabilities (tools, resources, prompts)
3. **Context Provision**: Host makes resources available to the user/LLM
4. **Invocation**: When needed, the LLM requests tool execution
5. **Execution**: Server performs the requested operation
6. **Response**: Results are returned and integrated into the LLM's context

### 1.4 Transport Methods

- **STDIO (Standard Input/Output)**: For local integrations on the same machine
- **HTTP+SSE (Server-Sent Events)**: For remote connections

### 1.5 Key Benefits

- **Standardization**: One protocol instead of N×M custom integrations
- **Security**: Built-in permission controls and user approval requirements
- **Ecosystem**: Growing library of pre-built servers (GitHub, Slack, databases, etc.)
- **Language Agnostic**: SDKs available for Python, TypeScript, Java, C#, and more
- **No External Dependencies**: Local JSONL storage, no cloud requirements

## 2. Knowledge Graph Server (`@itseasy21/mcp-knowledge-graph`)

### 2.1 Overview

This MCP server implements persistent memory using a local knowledge graph with customizable storage paths. It's specifically designed for:
- Remembering project structure and progress across chats
- Maintaining continuous project context
- Building relationship networks between components
- Storing timestamped observations and facts

### 2.2 Core Components

#### Entities
Primary nodes in the knowledge graph representing:
- **Phases/Stages**: Development milestones (e.g., `Phase 5.1`, `Stage 10`)
- **Components**: Software modules (e.g., `Query_Parser`, `Search_Engine`)
- **Decisions**: Architecture choices (e.g., `Decision_2024-05-24`)
- **Technologies**: Tools and frameworks
- Each entity has:
  - Unique name (identifier - case-sensitive)
  - Entity type
  - List of observations
  - Version tracking

#### Relations
Directed connections between entities:
- Always stored in active voice
- Describe how entities interact
- Include source, target, and relationship type
- Common types: `depends_on`, `implements`, `used_by`, `contains`

#### Observations
Discrete pieces of information about entities:
- **MUST** have system-generated timestamps
- Stored as atomic facts (one per observation)
- Format: `[YYYY-MM-DD HH:MM] Fact`
- Attached to specific entities
- Can be added/removed independently

### 2.3 Available Tools

1. **create_entities**: Create new entities with observations
2. **create_relations**: Establish relationships between entities
3. **add_observations**: Add new facts to existing entities
4. **delete_entities**: Remove entities and their relations
5. **delete_observations**: Remove specific observations
6. **delete_relations**: Remove specific relationships
7. **read_graph**: Retrieve the entire knowledge graph
8. **search_nodes**: Search based on names, types, or content
9. **open_nodes**: Retrieve specific nodes by name
10. **update_entities**: Modify existing entities

## 3. Two-Document Architecture

### 3.1 System Overview

The Panoptikon knowledge system uses a simplified two-document architecture:

1. **panoptikon_roadmap.md** - Project Structure
   - All phases, stages, and components
   - All relationships and dependencies (MCP-compliant format)
   - Updated manually when architecture changes
   - Single source of truth for "what should exist"
   - Must include relationship sections for MCP parsing

2. **ai_docs.md** - Project Progress (Living Document)
   - All implementation status and milestones
   - All decisions and rationale
   - **Updated continuously as work progresses**
   - Single source of truth for "what has been done"
   - **MUST use system timestamps**: `## [YYYY-MM-DD HH:MM]`
   - **Synchronized to knowledge graph via rebuild_graph.sh**

### 3.2 Configuration for Panoptikon

Your configuration in the MCP settings:
```json
{
  "memory": {
    "command": "npx",
    "args": [
      "-y",
      "@itseasy21/mcp-knowledge-graph"
    ],
    "env": {
      "MEMORY_FILE_PATH": "Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
    }
  }
}
```

### 3.3 Memory File Location

The knowledge graph is stored as a JSONL file at:
`Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl`

This file persists all entities, relations, and observations between sessions.

## 4. Critical Timestamp Requirements

### 4.1 System-Generated Only

**🚨 NEVER use AI-generated timestamps**. AI models cannot accurately estimate times and will hallucinate dates.

### 4.2 Correct Timestamp Generation

```bash
# Shell script - CORRECT
echo "## [$(date +"%Y-%m-%d %H:%M")] Progress update" >> docs/ai_docs.md

# Python - CORRECT
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
entry = f"## [{timestamp}] Progress update"
```

### 4.3 What NOT to Do

```markdown
## [2024-05-24 14:30] Progress update  # WRONG - AI estimated
## [yesterday afternoon] Progress update # WRONG - vague
## [May 2024] Progress update           # WRONG - imprecise
```

## 5. MCP Naming Conventions

### 5.1 Entity Naming Standards

- **Components**: Use underscores (e.g., `Query_Parser`, `Search_Engine`, `Database_Schema`)
- **Phases/Stages**: Use spaces (e.g., `Phase 5.1`, `Stage 10`)
- **Decisions**: Format `Decision_YYYY-MM-DD` (using system date)
- **Features**: Format `Feature_Name` (e.g., `Folder_Size_Feature`)
- **Consistency is critical** - entities are identified by normalized names

### 5.2 Entity Types (MCP Standard)

- `Phase` - Development phases
- `Stage` - Implementation stages
- `Component` - Software modules
- `decision` - Architecture decisions (lowercase per MCP)
- `issue` - Problems/blockers
- `technology` - Tools/frameworks
- `requirement` - Specifications

### 5.3 Relationship Types

- `implements`: Component implements feature
- `depends_on`: Technical dependencies
- `responsible_for`: Ownership assignments
- `blocks`: Issue blocking relationships
- `uses`: Technology usage
- `decided_by`: Decision ownership
- `contains`: Parent-child relationships
- `precedes`: Sequential dependencies

## 6. Ongoing Maintenance Protocol

### 6.1 Daily/Weekly Workflow

1. **Update ai_docs.md** with progress as work happens
   ```bash
   # Use system timestamps
   echo "## [$(date +"%Y-%m-%d %H:%M")] #phase5 #wip" >> docs/ai_docs.md
   echo "- **Summary:** Implemented Query_Parser optimization" >> docs/ai_docs.md
   echo "- **Details:** Reduced parsing time by 40%" >> docs/ai_docs.md
   ```

2. **Synchronize Knowledge Graph** regularly
   ```bash
   cd scripts/knowledge
   ./rebuild_graph.sh
   ```
   - Run after significant progress updates
   - Run before starting new work sessions
   - Creates cumulative view of all progress

3. **MCP Knowledge Graph Usage**
   - Start sessions with: "Remembering Panoptikon context..."
   - Query current state before making decisions
   - Update graph after important milestones

### 6.2 Synchronization Schedule

- **After each work session**: Update ai_docs.md
- **Daily**: Run rebuild_graph.sh if any updates made
- **Before planning**: Always sync to ensure accurate state
- **After architectural changes**: Update roadmap, then sync

### 6.3 Why Continuous Sync Matters

- Knowledge graph is only as current as last sync
- AI assistant needs current state for good advice
- Progress tracking enables accurate project status
- Historical record supports decision-making

## 7. Parser Specifications

### 7.1 AI Docs Parser Requirements

1. **Timestamp Extraction**
   - Extract ONLY existing timestamps from entries
   - NEVER generate new timestamps
   - Format: `[YYYY-MM-DD HH:MM]`
   - Skip entries without valid timestamps

2. **Progress Tracking**
   - Extract tags: `#phase`, `#stage`, `#done`, `#wip`, `#todo`
   - Determine status: Complete, In Progress, Planned
   - Create atomic observations

3. **Observation Format**
   - `[YYYY-MM-DD HH:MM] Status: {status}`
   - `[YYYY-MM-DD HH:MM] Implemented: {feature}`
   - `[YYYY-MM-DD HH:MM] Fixed: {issue}`
   - One fact per observation

4. **Entity Management**
   - Search before create (prevent duplicates)
   - Use normalized name matching
   - Add observations to existing entities
   - Create new entities only when needed

## 8. Best Practices for Panoptikon

### 8.1 Effective Observations

Good observations are:
- **Atomic**: One fact per observation
- **Timestamped**: System-generated timestamp prefix
- **Specific**: Include concrete details
- **Actionable**: Focus on information that aids decision-making

Examples:
- `[2024-05-20 14:32] Status: Complete`
- `[2024-05-20 14:32] Implemented: Query optimization reducing parse time by 40%`
- `[2024-05-20 14:32] Fixed: Memory leak in connection pool`

### 8.2 Memory Retrieval Strategy

When starting a conversation:
1. Always begin with "Remembering Panoptikon context..."
2. Search for relevant entities based on the topic
3. Open specific nodes for detailed information
4. Check latest observations for current status
5. Update the graph after significant new information

### 8.3 Search-Before-Create Pattern

Always search for existing entities before creating new ones:
```python
# Check if entity exists
if search_nodes("Query_Parser"):
    add_observations([{
        "entityName": "Query_Parser",
        "contents": [f"[{timestamp}] New optimization applied"]
    }])
else:
    create_entities([{
        "name": "Query_Parser",
        "entityType": "Component",
        "observations": [f"[{timestamp}] Initial implementation"]
    }])
```

## 9. Handling Architectural Changes

### 9.1 Change Process

When architectural changes are needed:

1. **Update panoptikon_roadmap.md**
   ```bash
   # Add system timestamp to change log
   echo "## [$(date +"%Y-%m-%d %H:%M")] Architectural Change" >> docs/panoptikon_roadmap.md
   echo "- Added new Stage 5.6 - Performance Monitoring" >> docs/panoptikon_roadmap.md
   echo "- Updated relationships section" >> docs/panoptikon_roadmap.md
   ```

2. **Record in ai_docs.md**
   ```bash
   echo "## [$(date +"%Y-%m-%d %H:%M")] #architecture #change" >> docs/ai_docs.md
   echo "- **Summary:** Added Stage 5.6 for performance monitoring" >> docs/ai_docs.md
   ```

3. **Synchronize immediately**
   ```bash
   cd scripts/knowledge
   ./rebuild_graph.sh
   ```

### 9.2 Manual Process Benefits

- Forces careful consideration
- Maintains consistency
- Creates audit trail with accurate timestamps
- Prevents automated cascading errors

## 10. Troubleshooting

### 10.1 Common Issues

1. **Memory not persisting**
   - Check file path permissions
   - Verify MEMORY_FILE_PATH in MCP config
   - Ensure rebuild_graph.sh completes successfully

2. **Can't find entities**
   - Verify exact naming (case-sensitive)
   - Check normalization: spaces vs underscores
   - Use search_nodes before assuming entity doesn't exist

3. **Duplicate entities**
   - Always use search before creating
   - Check for naming variations
   - Review parser logic for entity creation

4. **Missing timestamps**
   - Entries without valid timestamps are skipped
   - Check ai_docs.md format
   - Ensure system timestamp generation

### 10.2 Timestamp Validation

Check for AI-generated timestamps:
```python
import re
from collections import Counter

# Find suspicious patterns
timestamps = re.findall(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]', content)
minute_endings = Counter(ts.split(':')[1] for ts in timestamps)

# Too many :00 or :30 endings indicate AI generation
for minute, count in minute_endings.most_common():
    if minute in ['00', '30'] and count > 20% of total:
        print(f"⚠️ Suspicious timestamp pattern detected")
```

### 10.3 Memory File Inspection

```bash
# View current graph state
cat "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl" | tail -10

# Count entities
cat "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl" | wc -l

# Search for specific entity
grep "Query_Parser" "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
```

## 11. Quick Reference

### 11.1 Essential Daily Commands

```bash
# 1. Start work session
cd /Users/james/Documents/GitHub/panoptikon
echo "## [$(date +"%Y-%m-%d %H:%M")] #phase5 #wip Starting work on Query_Parser" >> docs/ai_docs.md

# 2. After completing work
echo "## [$(date +"%Y-%m-%d %H:%M")] #phase5 #done" >> docs/ai_docs.md
echo "- **Summary:** Completed Query_Parser optimization" >> docs/ai_docs.md
echo "- **Performance:** 40% faster parsing" >> docs/ai_docs.md

# 3. Sync to knowledge graph
cd scripts/knowledge
./rebuild_graph.sh

# 4. From AI assistant
# "Search for Query_Parser progress"
# "What's the current status of Phase 5?"
```

### 11.2 Key Points to Remember

- **Living System**: Requires continuous updates, not one-time setup
- **System Timestamps Only**: Never manually type or estimate times
- **Two Documents**: roadmap (structure) + ai_docs (progress)
- **Regular Syncs**: Knowledge graph must be rebuilt frequently
- **MCP Naming**: Components use underscores, phases/stages use spaces
- **Atomic Observations**: One timestamped fact per observation
- **Search First**: Always check if entity exists before creating

## 12. Success Metrics

After proper implementation and maintenance:

1. **Complete Knowledge Graph**
   - 100+ entities (vs ~30 before cleanup)
   - All phases and stages represented
   - All progress tracked with system timestamps
   - All relationships mapped

2. **Data Integrity**
   - Zero AI-generated timestamps
   - Consistent entity naming
   - No duplicate entities
   - Atomic, timestamped observations

3. **Performance**
   - Rebuild takes <5 seconds
   - No network dependencies
   - Local JSONL processing only
   - Instant entity searches

4. **Living Documentation**
   - ai_docs.md updated after each work session
   - Knowledge graph synced daily
   - AI assistant has current project state
   - Complete audit trail maintained

---

*This is a living document. Update it as new patterns emerge or capabilities are added. Remember: the value of this system comes from keeping it current through regular updates and synchronization.*