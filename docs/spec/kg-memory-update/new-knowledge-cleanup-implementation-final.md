# Knowledge System Cleanup - Technical Implementation

**🚨 CRITICAL**: All timestamps MUST be system-generated. AI models cannot accurately generate timestamps and will hallucinate dates/times. This is non-negotiable for data integrity.

## Quick Reference - Ongoing Workflow

### After Each Work Session
```bash
# 1. Update progress in ai_docs.md
echo "## [$(date +"%Y-%m-%d %H:%M")] #phase5 #wip" >> docs/ai_docs.md
echo "- **Summary:** Implemented Query_Parser optimization" >> docs/ai_docs.md
echo "- **Details:** Reduced parsing time by 40%" >> docs/ai_docs.md

# 2. Sync to knowledge graph
cd scripts/knowledge
./rebuild_graph.sh

# 3. Verify in MCP (from AI assistant)
# "Search for Query_Parser updates"
```

### Weekly Maintenance
1. Review ai_docs.md for completeness
2. Run full knowledge graph rebuild
3. Check for any architectural changes needed in roadmap
4. Backup current knowledge graph

This is a **living system** - the value comes from keeping it current!

## Pre-Implementation Checklist

```bash
# 1. Backup current system WITH TIMESTAMP
cd /Users/james/Documents/GitHub/panoptikon
cp -r "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl" \
      "/Users/james/Library/Application Support/Claude/panoptikon/memory_backup_$(date +%Y%m%d_%H%M%S).jsonl"

# 2. Create working branch
git checkout -b knowledge-system-cleanup
git add -A
git commit -m "Backup before knowledge system cleanup - $(date +"%Y-%m-%d %H:%M")"
```

## Phase 1: Document Preparation

### 1.1 Rename and Update Roadmap

```bash
# Rename to canonical name
mv docs/read_panoptikon-development-roadmap.md docs/panoptikon_roadmap.md
```

### 1.2 Add Relationships Section to Roadmap

Add this section to the end of `panoptikon_roadmap.md` with MCP-compliant naming:

```markdown
## Relationships

### Phase Relationships
- **Phase 1 - Foundation**
  - **Precedes**: Phase 2 - Core Engine
  - **Contains**: Stage 1 - Project Initialization, Stage 2 - Core Infrastructure, Stage 3 - Filesystem Abstraction, Stage 4 - Database Foundation

- **Phase 2 - Core Engine**
  - **Depends On**: Phase 1 - Foundation
  - **Precedes**: Phase 3 - UI Framework
  - **Contains**: Stage 5 - Search Engine, Stage 6 - Indexing System

- **Phase 3 - UI Framework**
  - **Depends On**: Phase 2 - Core Engine
  - **Precedes**: Phase 4 - Integration
  - **Contains**: Stage 7 - UI Framework

- **Phase 4 - Integration**
  - **Depends On**: Phase 3 - UI Framework
  - **Precedes**: Phase 5 - Optimization
  - **Contains**: Stage 8 - Cloud Integration, Stage 9 - System Integration

- **Phase 5 - Optimization**
  - **Depends On**: Phase 4 - Integration
  - **Precedes**: Phase 6 - Packaging
  - **Contains**: Stage 10 - Optimization

- **Phase 6 - Packaging**
  - **Depends On**: Phase 5 - Optimization
  - **Contains**: Stage 11 - Packaging and Release

### Stage Component Relationships (MCP naming conventions)
- **Stage 1 - Project Initialization**
  - **Contains**: Project_Structure, Build_System, Testing_Framework

- **Stage 2 - Core Infrastructure**
  - **Contains**: Service_Container, Event_Bus, Configuration_System

- **Stage 3 - Filesystem Abstraction**
  - **Contains**: FSEvents_Wrapper, Security_Bookmarks, Cloud_Detection

- **Stage 4 - Database Foundation**
  - **Contains**: Database_Schema, Connection_Pool, Migration_System, Query_Optimization

- **Stage 5 - Search Engine**
  - **Contains**: Query_Parser, Search_Algorithm, Result_Management, Sorting_System, Filtering_System

- **Stage 6 - Indexing System**
  - **Contains**: Initial_Scanner, Incremental_Updates, File_System_Monitoring, Folder_Size_Calculation

- **Stage 7 - UI Framework**
  - **Contains**: Main_Window, Search_Field, Results_Table, Dual_Window_Manager, Folder_Size_Display

### Component Dependencies
- **Service_Container**
  - **Used By**: All core components

- **Database_Schema**
  - **Used By**: Connection_Pool, Migration_System, Search_Engine, Indexing_System

- **Query_Parser**
  - **Used By**: Search_Algorithm

- **Search_Engine**
  - **Depends On**: Database_Schema, Query_Parser
  - **Used By**: UI_Framework

### Feature Relationships
- **Folder_Size_Feature**
  - **Implemented By**: Folder_Size_Calculation, Folder_Size_Display
  - **Depends On**: Database_Schema, Migration_System

- **Dual_Window_Feature**
  - **Implemented By**: Dual_Window_Manager
  - **Depends On**: Main_Window, Event_Bus
```

### 1.3 Audit ai_docs.md Timestamps

**CRITICAL STEP**: Verify all timestamps in ai_docs.md are in correct format:

```bash
# Check timestamp format in ai_docs.md
grep -E "^## \[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}\]" docs/ai_docs.md

# Find any non-conforming date formats
grep -E "^## \[" docs/ai_docs.md | grep -v -E "^\## \[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}\]"

# If any bad timestamps found, they must be fixed or entries will be skipped
```

**⚠️ WARNING**: Any entries without proper timestamps will be ignored by the parser. Do NOT add timestamps to historical entries - preserve them as-is.

## Phase 2: Parser Development

### 2.0 Update Memory Manager for MCP Support

First, ensure `memory_manager_typed.py` has these methods:

```python
def add_observation(self, entity_name: str, observation: str, *, dry_run: bool = False) -> None:
    """Add observation to existing entity."""
    normalized = normalize_name(entity_name)
    entity = None
    
    # Find entity by normalized name
    for e in self._entity_cache.values():
        if normalize_name(e.name) == normalized:
            entity = e
            break
            
    if not entity:
        print(f"  [Error] Entity not found: {entity_name}")
        return
        
    if dry_run:
        print(f"  [DRY] Would add observation to {entity.name}: {observation}")
        return
        
    # Add observation to entity
    entity.observations.append(observation)
    
    # Write updated entity to file
    with self.memory_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entity.to_jsonl_dict()) + "\n")
    print(f"  [Add] Observation to {entity.name}: {observation}")

def entity_exists(self, name: str) -> bool:
    """Check if entity exists by normalized name."""
    normalized = normalize_name(name)
    return any(normalize_name(e.name) == normalized 
               for e in self._entity_cache.values())
```

### 2.1 Create ai_docs Parser

Create `scripts/knowledge/ai_docs_parser.py` with MCP-aware functionality:

```python
#!/usr/bin/env python3
"""MCP-aware parser for ai_docs.md progress tracking.

Extracts progress entries and links them to roadmap entities using MCP best practices.
CRITICAL: Only uses existing timestamps - NEVER generates dates/times.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.knowledge.models import entity_id, normalize_name


class AIDocsParser:
    """Parse ai_docs.md entries and extract progress information."""
    
    def __init__(self, memory_manager):
        self.km = memory_manager
        self.processed_entries = set()
        
    def parse_file(self, filepath: Path, dry_run: bool = False) -> None:
        """Parse ai_docs.md and extract all progress entries."""
        print(f"\nParsing AI docs: {filepath}")
        
        content = filepath.read_text(encoding="utf-8")
        entries = self._split_entries(content)
        
        valid_count = 0
        skipped_count = 0
        
        for entry in entries:
            if self._has_valid_timestamp(entry):
                self._process_entry(entry, dry_run)
                valid_count += 1
            else:
                skipped_count += 1
                
        print(f"\nProcessed {valid_count} entries, skipped {skipped_count} (no valid timestamp)")
            
    def _split_entries(self, content: str) -> List[str]:
        """Split content into individual dated entries."""
        # Split on the timestamp pattern, keeping the delimiter
        pattern = r'(?=## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\])'
        entries = re.split(pattern, content)
        return [e.strip() for e in entries if e.strip()]
        
    def _has_valid_timestamp(self, entry: str) -> bool:
        """Check if entry has a valid timestamp format."""
        return bool(re.match(r'## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]', entry))
        
    def _process_entry(self, entry: str, dry_run: bool = False) -> None:
        """Process a single progress entry using MCP best practices."""
        # Extract timestamp - NEVER generate, only extract
        timestamp_match = re.match(r'## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]', entry)
        if not timestamp_match:
            return
            
        timestamp = timestamp_match.group(1)
        
        # Extract tags from first line
        first_line = entry.split('\n')[0]
        tags = re.findall(r'#([\w.-]+)', first_line)
        
        # Extract phase/stage info
        phase_tags = [t for t in tags if t.startswith('phase')]
        stage_tags = [t for t in tags if t.startswith('stage')]
        
        # Extract status
        status = "In Progress"
        if 'done' in tags:
            status = "Complete"
        elif 'todo' in tags:
            status = "Planned"
        elif 'wip' in tags or 'in-progress' in tags:
            status = "In Progress"
            
        # Extract summary
        summary_match = re.search(r'- \*\*Summary:\*\*\s*(.+?)(?=\n-|\n\n|\Z)', entry, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # Process phases and stages
        for tag in phase_tags + stage_tags:
            entity_name = self._tag_to_entity_name(tag)
            entity_type = "Phase" if tag.startswith('phase') else "Stage"
            
            # Search for existing entity first (MCP best practice)
            existing = self._search_entity(entity_name)
            
            if existing:
                # Add observation to existing entity
                observations = self._create_atomic_observations(timestamp, status, summary)
                for obs in observations:
                    if dry_run:
                        print(f"  [DRY] Would add observation to {entity_name}: {obs}")
                    else:
                        self.km.add_observation(entity_name, obs)
                        print(f"  [Add] Observation to {entity_name}: {obs}")
            else:
                # Create new entity with initial observation
                obs = f"[{timestamp}] Status: {status}"
                self.km.add_entity(
                    entity_name, 
                    entity_type,
                    observation=obs,
                    dry_run=dry_run
                )
                
        # Process component mentions with MCP naming
        if summary:
            components = self._extract_components(summary)
            for component in components:
                # Use MCP naming convention
                component_name = self._mcp_component_name(component)
                
                # Search first
                if self._search_entity(component_name):
                    obs = f"[{timestamp}] {summary[:100]}..."
                    if not dry_run:
                        self.km.add_observation(component_name, obs)
                else:
                    self.km.add_entity(
                        component_name,
                        "Component", 
                        observation=f"[{timestamp}] First mentioned in progress",
                        dry_run=dry_run
                    )
                    
        # Handle architectural decisions
        if 'decision' in tags:
            self._process_decision(timestamp, summary, dry_run)
                    
    def _tag_to_entity_name(self, tag: str) -> str:
        """Convert a tag like 'phase5.1' to 'Phase 5.1'."""
        if tag.startswith('phase'):
            parts = tag.replace('phase', '').split('.')
            if len(parts) == 1:
                return f"Phase {parts[0]}"
            else:
                return f"Phase {parts[0]}.{parts[1]}"
        elif tag.startswith('stage'):
            num = tag.replace('stage', '').replace('_', '.')
            return f"Stage {num}"
        return tag
        
    def _mcp_component_name(self, component: str) -> str:
        """Convert component name to MCP convention."""
        # Remove common suffixes
        component = component.replace(" class", "").replace(" component", "")
        # Convert to underscore format
        return component.strip().replace(" ", "_")
        
    def _search_entity(self, name: str) -> bool:
        """Check if entity exists using normalized name."""
        normalized = normalize_name(name)
        return any(normalize_name(e.name) == normalized 
                  for e in self.km._entity_cache.values())
        
    def _create_atomic_observations(self, timestamp: str, status: str, 
                                   summary: str) -> List[str]:
        """Create atomic observations following MCP best practices."""
        observations = [f"[{timestamp}] Status: {status}"]
        
        if summary:
            # Extract specific accomplishments
            if "implemented" in summary.lower():
                impl_match = re.search(r'[Ii]mplemented\s+(.+?)(?:\.|,|;|$)', summary)
                if impl_match:
                    observations.append(f"[{timestamp}] Implemented: {impl_match.group(1)}")
                    
            if "fixed" in summary.lower():
                fix_match = re.search(r'[Ff]ixed\s+(.+?)(?:\.|,|;|$)', summary)
                if fix_match:
                    observations.append(f"[{timestamp}] Fixed: {fix_match.group(1)}")
                    
            if "added" in summary.lower():
                add_match = re.search(r'[Aa]dded\s+(.+?)(?:\.|,|;|$)', summary)
                if add_match:
                    observations.append(f"[{timestamp}] Added: {add_match.group(1)}")
                    
        return observations
        
    def _extract_components(self, text: str) -> List[str]:
        """Extract component names from text."""
        components = []
        
        # Common component patterns
        patterns = [
            r'(?:Implemented|Created|Added|Updated|Fixed)\s+(?:the\s+)?`?(\w+(?:\s+\w+)*?)`?(?:\s+class|\s+component|\s+module)?',
            r'`(\w+(?:\s+\w+)*?)`',  # Backtick references
            r'(?:^|\s)([A-Z]\w+(?:[A-Z]\w+)+)(?:\s|$)',  # CamelCase
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            components.extend(matches)
            
        # Filter and clean
        cleaned = []
        for comp in components:
            comp = comp.strip()
            # Skip common words and tags
            if comp and len(comp) > 2 and comp not in ['Status', 'Summary', 'Phase', 'Stage']:
                cleaned.append(comp)
                
        return list(set(cleaned))  # Remove duplicates
        
    def _process_decision(self, timestamp: str, summary: str, dry_run: bool) -> None:
        """Process architectural decisions with MCP decision type."""
        if summary:
            # Extract decision title
            decision_match = re.search(r'[Dd]ecided\s+(?:to\s+)?(.+?)(?:\.|$)', summary)
            if decision_match:
                # Use date portion of timestamp for decision name
                date_part = timestamp.split()[0]
                decision_name = f"Decision_{date_part}"
                self.km.add_entity(
                    decision_name,
                    "decision",  # MCP entity type
                    observation=f"[{timestamp}] {decision_match.group(1)}",
                    dry_run=dry_run
                )


def main():
    """CLI entry point."""
    import argparse
    from scripts.knowledge.memory_manager_typed import KnowledgeGraphManager
    
    parser = argparse.ArgumentParser(description="Parse ai_docs.md progress entries")
    parser.add_argument("file", help="Path to ai_docs.md")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    
    km = KnowledgeGraphManager()
    parser = AIDocsParser(km)
    parser.parse_file(Path(args.file), dry_run=args.dry_run)
    

if __name__ == "__main__":
    main()
```

## Phase 3: Update Rebuild Script

### 3.1 Modify rebuild_graph.sh

Update the extraction section in `scripts/knowledge/rebuild_graph.sh`:

```bash
# Phase 2: Extract from Documentation
echo -e "\n[Phase 2] Document Extraction"

# Extract from roadmap (structure and relationships)
echo "  Extracting project structure from roadmap..."
if [ -f "$DOCS_DIR/panoptikon_roadmap.md" ]; then
    python "$EXTRACTOR" "$DOCS_DIR/panoptikon_roadmap.md"
else
    echo "  [ERROR] panoptikon_roadmap.md not found!"
    exit 1
fi

# Extract from ai_docs (progress and status)
echo "  Extracting progress from ai_docs..."
if [ -f "$DOCS_DIR/ai_docs.md" ]; then
    if [ -f "$SCRIPTS_DIR/ai_docs_parser.py" ]; then
        python "$SCRIPTS_DIR/ai_docs_parser.py" "$DOCS_DIR/ai_docs.md"
    else
        echo "  [ERROR] ai_docs_parser.py not found!"
        exit 1
    fi
else
    echo "  [WARN] ai_docs.md not found - no progress data"
fi

# Remove old directory processing - these are empty
# No longer processing phases/, components/, decisions/
```

## Phase 4: Cleanup Operations

### 4.1 Archive Qdrant Dependencies

```bash
cd /Users/james/Documents/GitHub/panoptikon

# Create archive directory
mkdir -p scripts/archived/qdrant

# Move Qdrant-related files
mv scripts/documentation/dual_reindex.py scripts/archived/qdrant/
mv scripts/documentation/migrate_*.py scripts/archived/qdrant/
mv scripts/qdrant/* scripts/archived/qdrant/ 2>/dev/null || true

# Archive the directory with timestamp
tar -czf scripts/archived/qdrant_backup_$(date +%Y%m%d_%H%M%S).tar.gz scripts/archived/qdrant
```

### 4.2 Simplify ai_docs.py

Remove Qdrant dependencies from `scripts/documentation/ai_docs.py`:

```python
# Remove these imports
# from qdrant_client import QdrantClient
# from sentence_transformers import SentenceTransformer

# Remove Qdrant initialization from __init__
# Remove these methods:
# - ensure_collection()
# - search_docs()  
# - index_document()

# Keep only local file operations
```

### 4.3 Remove Empty Directories

```bash
# Remove empty documentation directories
rm -rf docs/progress/
rm -rf docs/decisions/
rm -rf docs/kg_export/

# Clean up any .DS_Store files
find docs -name ".DS_Store" -delete
```

## Phase 5: Testing & Validation

### 5.1 Test the New System

```bash
cd scripts/knowledge

# Dry run first
./rebuild_graph.sh --dry-run

# If looks good, run for real
./rebuild_graph.sh

# Check the results
wc -l "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
# Should show many more lines than before
```

### 5.2 Validate Knowledge Graph with MCP

```python
# Quick validation script using MCP functionality
from scripts.knowledge.memory_manager_typed import KnowledgeGraphManager
from datetime import datetime

km = KnowledgeGraphManager()

print(f"Validation run at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Check for Phase 5 entries with observations
phase5_entities = [e for e in km._entity_cache.values() 
                   if 'Phase 5' in e.name]
print(f"\nPhase 5 entities: {len(phase5_entities)}")

# Check observations on entities
for entity in phase5_entities[:3]:  # First 3 as examples
    print(f"\n{entity.name} ({entity.entityType}):")
    for obs in entity.observations:
        print(f"  - {obs}")

# Check for proper MCP naming
components = [e for e in km._entity_cache.values() 
              if e.entityType == "Component"]
mcp_named = [c for c in components if "_" in c.name]
print(f"\nComponents with MCP naming: {len(mcp_named)}/{len(components)}")

# Look for decisions
decisions = [e for e in km._entity_cache.values() 
             if e.entityType == "decision"]
print(f"\nArchitecture decisions tracked: {len(decisions)}")

# Verify atomic observations with timestamps
import re
all_observations = []
for entity in km._entity_cache.values():
    all_observations.extend(entity.observations)
    
timestamped = [o for o in all_observations if re.match(r'^\[\d{4}-\d{2}-\d{2}', o)]
print(f"\nTimestamped observations: {len(timestamped)}/{len(all_observations)}")

# Check for AI-generated timestamps (suspicious patterns)
suspicious_times = []
for obs in timestamped:
    time_match = re.match(r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]', obs)
    if time_match:
        time_str = time_match.group(1)
        # Check for patterns like always :00 or :30
        if time_str.endswith(':00') or time_str.endswith(':30'):
            suspicious_times.append(time_str)
            
if suspicious_times:
    print(f"\n⚠️  WARNING: Found {len(suspicious_times)} suspicious timestamps ending in :00 or :30")
    print("These may be AI-generated. Sample:", suspicious_times[:5])
```

## Phase 6: Documentation Updates

### 6.1 Update AI_DOCUMENTATION_GUIDE.md

Remove Qdrant references and align with MCP:

```markdown
# AI Documentation Guide - Panoptikon

## Knowledge System Overview

The Panoptikon knowledge system uses the MCP Knowledge Graph server for persistent memory:

1. **panoptikon_roadmap.md** - Project structure and relationships
2. **ai_docs.md** - Progress tracking and history  
3. **MCP Knowledge Graph** - Combined view stored in JSONL format

## Timestamp Requirements

**🚨 CRITICAL**: All timestamps MUST be system-generated. AI cannot accurately estimate times.

### Creating New Entries
```bash
# Correct - System generated
echo "## [$(date +"%Y-%m-%d %H:%M")] Progress update" >> docs/ai_docs.md

# WRONG - Never manually type timestamps
echo "## [2025-05-24 14:30] Progress update" >> docs/ai_docs.md
```

### Python Timestamps
```python
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
entry = f"## [{timestamp}] Progress update"
```

## MCP Integration

### Entity Naming Conventions
- Phases/Stages: `Phase 5.1`, `Stage 10`
- Components: `Query_Parser`, `Search_Engine` (use underscores)
- Decisions: `Decision_2025-05-24` (use system date)
- Consistency is key - entities are identified by name

### Entity Types
- `Phase` - Development phases
- `Stage` - Implementation stages  
- `Component` - Software modules
- `decision` - Architecture decisions
- `issue` - Problems/blockers
- `technology` - Tools/frameworks

### Observations
- Progress stored as timestamped observations
- Format: `[YYYY-MM-DD HH:MM] Status: X - Details`
- Keep observations atomic (one fact each)
- Automatically versioned by MCP

## Workflow

1. **Planning Changes**: Update panoptikon_roadmap.md relationships
2. **Progress Tracking**: Update ai_docs.md with system-timestamped entries
3. **Knowledge Graph**: Run `rebuild_graph.sh` to sync
4. **Query**: Use MCP tools (search_nodes, read_graph) to explore

## MCP Tools Available
- `create_entities` - New entities with observations
- `add_observations` - Add facts to existing entities
- `create_relations` - Link entities
- `search_nodes` - Find entities by name/type/content
- `read_graph` - Get complete graph
- `delete_entities` - Remove entities
- `update_entities` - Modify entities

## Best Practices
- Always use system timestamps
- Search before creating new entities
- Use consistent naming (especially underscores)
- Keep observations atomic and timestamped
- Let MCP handle versioning automatically
```

## Handling Roadmap Changes

### Change Process

When architectural changes are needed:

1. **Update panoptikon_roadmap.md**
   ```bash
   # Add system timestamp to change log
   echo "## [$(date +"%Y-%m-%d %H:%M")] Architectural Change" >> docs/panoptikon_roadmap.md
   echo "- Added new Stage 5.6 - Performance Monitoring" >> docs/panoptikon_roadmap.md
   echo "- Updated relationships section" >> docs/panoptikon_roadmap.md
   echo "- Reason: Need dedicated performance tracking" >> docs/panoptikon_roadmap.md
   ```

2. **Update affected stage files** (if they exist)
   ```bash
   # Check which stages reference changed components
   grep -r "Component Name" docs/stages/
   ```

3. **Record in ai_docs.md**
   ```bash
   # System timestamp for progress entry
   echo "## [$(date +"%Y-%m-%d %H:%M")] #architecture #change #stage5.6" >> docs/ai_docs.md
   echo "- **Phase:** 5 (Search Engine)" >> docs/ai_docs.md
   echo "- **Summary:** Added Stage 5.6 for performance monitoring" >> docs/ai_docs.md
   echo "- **Rationale:** Separate performance concerns from optimization" >> docs/ai_docs.md
   ```

4. **Rebuild knowledge graph**
   ```bash
   cd scripts/knowledge
   ./rebuild_graph.sh
   ```

### Cascade Handling

For cascading changes:
- Manual review ensures consistency
- Git diff shows what changed
- Knowledge graph rebuild captures new state
- ai_docs.md provides audit trail with accurate timestamps

## Rollback Plan

If issues arise:

```bash
# Restore from timestamped backup
cp "/Users/james/Library/Application Support/Claude/panoptikon/memory_backup_[timestamp].jsonl" \
   "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"

# Or rebuild from last known good state
git checkout [last-good-commit] -- docs/panoptikon_roadmap.md docs/ai_docs.md
./rebuild_graph.sh
```

## Success Verification with MCP

After implementation:

1. **Entity Count**: Should see 100+ entities (vs ~30 before)
2. **Progress Tracking**: Phase 5 entities should exist with observations
3. **Relationships**: All roadmap relationships preserved
4. **Performance**: Rebuild takes <5 seconds (no network calls)
5. **MCP Compliance**: 
   - Components use underscore naming
   - Observations are timestamped
   - Decisions tracked as separate entity type
   - Search functionality prevents duplicates
6. **JSONL Integrity**: Each line is valid JSON with proper MCP structure
7. **Timestamp Integrity**: No AI-generated timestamps in the system

## MCP Tool Usage

After cleanup, you can use MCP tools directly:

```python
from datetime import datetime

# Search for components
results = search_nodes("Query_Parser")

# Read full graph
graph = read_graph()

# Add new observations with system timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
add_observations([{
    "entityName": "Phase 5.1",
    "contents": [f"[{timestamp}] Deployed to production"]
}])

# Create new relations
create_relations([{
    "from": "Query_Parser",
    "to": "Search_Engine", 
    "relationType": "used_by"
}])
```

## Timestamp Validation Script

Use this to check for AI-generated timestamps:

```python
#!/usr/bin/env python3
"""Validate timestamps in ai_docs.md for AI hallucinations."""

import re
from pathlib import Path
from collections import Counter

def check_timestamps(filepath):
    content = filepath.read_text()
    timestamps = re.findall(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]', content)
    
    # Check for suspicious patterns
    minute_endings = Counter(ts.split(':')[1] for ts in timestamps)
    
    print(f"Total timestamps: {len(timestamps)}")
    print(f"Minute endings distribution:")
    for minute, count in minute_endings.most_common():
        pct = (count / len(timestamps)) * 100
        flag = "⚠️ " if minute in ['00', '30'] and pct > 20 else ""
        print(f"  :{minute} - {count} times ({pct:.1f}%) {flag}")
        
    # Check for sequential patterns
    print("\nChecking for suspicious sequential patterns...")
    for i in range(1, len(timestamps)):
        prev = timestamps[i-1]
        curr = timestamps[i]
        # If timestamps are exactly 30 or 60 minutes apart, flag
        # (This would be very unlikely with real system timestamps)
        
if __name__ == "__main__":
    check_timestamps(Path("docs/ai_docs.md"))
```

The cleaned system fully leverages MCP capabilities while maintaining simplicity and timestamp integrity.