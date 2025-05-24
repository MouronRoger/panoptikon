# Knowledge System Cleanup - Phased Implementation Plan

## Executive Summary

This document provides a concrete, phased implementation plan for completing the Panoptikon knowledge system cleanup. Much of the preparatory work has been completed - this plan focuses on the remaining implementation tasks needed to achieve a fully functional two-document knowledge system.

**Current State:**
- ✅ Documents prepared (roadmap has relationships, ai_docs has timestamps)
- ✅ Empty directories removed
- ✅ Basic infrastructure exists (models, extractors)
- ❌ Missing ai_docs parser
- ❌ Missing key methods in KnowledgeGraphManager
- ❌ rebuild_graph.sh references old structure

**Target State:**
- 100+ entities (vs current 7)
- Full progress tracking from ai_docs.md
- Clean, simple two-document system
- No external dependencies

## Phase 1: Extend KnowledgeGraphManager (30 minutes)

### 1.1 Add Missing Methods to relationship_extractor_typed.py

Add these methods to the `KnowledgeGraphManager` class:

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
    
    # Check if observation already exists
    if observation in entity.observations:
        print(f"  [Skip] Observation already exists on {entity.name}")
        return
        
    # Add observation to entity
    entity.observations.append(observation)
    
    # Rewrite the entire entity with updated observations
    # Note: This is inefficient but maintains compatibility with MCP format
    with self.memory_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entity.to_jsonl_dict()) + "\n")
    print(f"  [Add] Observation to {entity.name}: {observation}")

def entity_exists(self, name: str) -> bool:
    """Check if entity exists by normalized name."""
    normalized = normalize_name(name)
    return any(normalize_name(e.name) == normalized 
               for e in self._entity_cache.values())

def search_entities(self, name: str) -> Optional[Entity]:
    """Search for entity by normalized name."""
    normalized = normalize_name(name)
    for e in self._entity_cache.values():
        if normalize_name(e.name) == normalized:
            return e
    return None
```

### 1.2 Test the Extended Manager

Create a quick test script to verify the new methods work:

```bash
cd /Users/james/Documents/GitHub/panoptikon
python3 -c "
from scripts.knowledge.relationship_extractor_typed import KnowledgeGraphManager
km = KnowledgeGraphManager()
print(f'Entity exists test: {km.entity_exists(\"Phase 5.1\")}')
km.add_entity('Test_Entity', 'Component', 'Initial observation', dry_run=True)
km.add_observation('Test_Entity', '[2025-05-24 23:00] Test observation', dry_run=True)
"
```

## Phase 2: Create AI Docs Parser (2 hours)

### 2.1 Create scripts/knowledge/ai_docs_parser.py

```python
#!/usr/bin/env python3
"""MCP-aware parser for ai_docs.md progress tracking.

Extracts progress entries and links them to roadmap entities using MCP best practices.
CRITICAL: Only uses existing timestamps - NEVER generates dates/times.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.knowledge.relationship_extractor_typed import KnowledgeGraphManager
from scripts.knowledge.models import normalize_name


class AIDocsParser:
    """Parse ai_docs.md entries and extract progress information."""
    
    def __init__(self, memory_manager: KnowledgeGraphManager):
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
            if self.km.entity_exists(entity_name):
                # Add observation to existing entity
                observations = self._create_atomic_observations(timestamp, status, summary)
                for obs in observations:
                    self.km.add_observation(entity_name, obs, dry_run=dry_run)
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
                if self.km.entity_exists(component_name):
                    obs = f"[{timestamp}] {summary[:100]}..."
                    self.km.add_observation(component_name, obs, dry_run=dry_run)
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

### 2.2 Test the Parser

```bash
# Dry run first
cd /Users/james/Documents/GitHub/panoptikon
python scripts/knowledge/ai_docs_parser.py docs/ai_docs.md --dry-run | head -50

# Check if it's finding entries
python scripts/knowledge/ai_docs_parser.py docs/ai_docs.md --dry-run | grep "Phase\|Stage\|Component"
```

## Phase 3: Update Rebuild Script (30 minutes)

### 3.1 Update scripts/knowledge/rebuild_graph.sh

Replace the current extraction section with:

```bash
# Phase 2: Extract from Documentation
echo -e "\n[Phase 2] Document Extraction"

# Extract from roadmap (structure and relationships)
echo "  Extracting project structure from roadmap..."
if [ -f "$DOCS_DIR/panoptikon_roadmap.md" ]; then
    if [ -f "$SCRIPTS_DIR/relationship_extractor_typed.py" ]; then
        python "$SCRIPTS_DIR/relationship_extractor_typed.py" "$DOCS_DIR/panoptikon_roadmap.md"
    else
        python "$SCRIPTS_DIR/relationship_extractor.py" "$DOCS_DIR/panoptikon_roadmap.md"
    fi
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

### 3.2 Remove Qdrant References

Remove or comment out the entire "Optional: Sync to Qdrant" section:

```bash
# Phase 6: Summary
echo -e "\n[Phase 6] Summary"
if [ -f "$SCRIPTS_DIR/graph_summary.py" ]; then
    python "$SCRIPTS_DIR/graph_summary.py"
else
    echo "  [Warn] graph_summary.py not found"
    # Simple fallback
    echo "  Entities: $(grep -c '"type":"entity"' "$MEMORY_PATH" 2>/dev/null || echo 0)"
    echo "  Relations: $(grep -c '"type":"relation"' "$MEMORY_PATH" 2>/dev/null || echo 0)"
fi

# Removed Qdrant sync section - no longer needed

echo -e "\n=== Rebuild Complete ==="
echo "Finished at: $(date)"
exit 0
```

## Phase 4: Testing & Validation (1 hour)

### 4.1 Full System Test

```bash
cd /Users/james/Documents/GitHub/panoptikon

# Backup current knowledge graph
cp "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl" \
   "/Users/james/Library/Application Support/Claude/panoptikon/memory_backup_$(date +%Y%m%d_%H%M%S).jsonl"

# Run the full rebuild
cd scripts/knowledge
./rebuild_graph.sh

# Check results
echo "Entity count: $(grep -c '"type":"entity"' "$MEMORY_PATH")"
echo "Relation count: $(grep -c '"type":"relation"' "$MEMORY_PATH")"
```

### 4.2 Validation Script

Create a validation script to check the results:

```python
#!/usr/bin/env python3
"""Validate the rebuilt knowledge graph."""

from scripts.knowledge.relationship_extractor_typed import KnowledgeGraphManager

km = KnowledgeGraphManager()

# Count entities by type
entity_types = {}
for entity in km._entity_cache.values():
    entity_types[entity.entityType] = entity_types.get(entity.entityType, 0) + 1

print("Entity counts by type:")
for etype, count in sorted(entity_types.items()):
    print(f"  {etype}: {count}")

# Check for progress observations
progress_count = 0
for entity in km._entity_cache.values():
    if any('Status:' in obs for obs in entity.observations):
        progress_count += 1

print(f"\nEntities with progress: {progress_count}")

# Sample some phases
print("\nSample Phase observations:")
for entity in km._entity_cache.values():
    if entity.entityType == "Phase" and entity.observations:
        print(f"\n{entity.name}:")
        for obs in entity.observations[:3]:
            print(f"  - {obs}")
        if len(entity.observations) > 3:
            print(f"  ... and {len(entity.observations) - 3} more")
```

### 4.3 MCP Tool Verification

Test with MCP tools:

```python
# Use the MCP knowledge graph tools
search_nodes("Phase 5")  # Should find Phase 5 entries
open_nodes(["Phase 5.1", "Query_Parser"])  # Should show observations
```

## Phase 5: Cleanup & Documentation (30 minutes)

### 5.1 Remove Old Files

```bash
# Archive any Qdrant-related scripts if found
find scripts -name "*qdrant*" -o -name "*dual_reindex*" | while read f; do
    echo "Found: $f"
    # mkdir -p scripts/archived
    # mv "$f" scripts/archived/
done

# Clean up any empty directories
find docs -type d -empty -delete
```

### 5.2 Update Documentation

Update AI_DOCUMENTATION_GUIDE.md to reflect the new system:
- Remove Qdrant references from the core knowledge system
- Update the workflow to use rebuild_graph.sh
- Add examples of using MCP tools

### 5.3 Create a Quick Reference Card

Create `docs/guides/KNOWLEDGE_GRAPH_QUICK_REFERENCE.md`:

```markdown
# Knowledge Graph Quick Reference

## Daily Workflow

1. **Update Progress**
   ```bash
   echo "## [$(date +"%Y-%m-%d %H:%M")] #phase5 #wip" >> docs/ai_docs.md
   echo "- **Summary:** Implemented feature X" >> docs/ai_docs.md
   ```

2. **Sync Knowledge Graph**
   ```bash
   cd scripts/knowledge
   ./rebuild_graph.sh
   ```

3. **Query from AI**
   - Use: search_nodes("component name")
   - Use: open_nodes(["Phase 5.1"])

## Key Files
- Structure: `/docs/panoptikon_roadmap.md`
- Progress: `/docs/ai_docs.md`
- Graph: `.../Claude/panoptikon/memory.jsonl`

## MCP Entity Naming
- Phases: `Phase 5.1` (with space)
- Stages: `Stage 10` (with space)
- Components: `Query_Parser` (underscore)
- Decisions: `Decision_2025-05-24`
```

## Success Criteria

After implementation:

1. **Entity Count**: 100+ entities (vs current 7)
   - All 6 phases represented
   - All 11 stages represented
   - Major components tracked
   - Progress observations attached

2. **Observations**: 
   - Each phase/stage has status observations
   - Timestamps preserved from ai_docs.md
   - Atomic, meaningful observations

3. **Performance**:
   - Rebuild completes in <10 seconds
   - No network calls (all local)
   - Clean output with clear progress

4. **Cleanliness**:
   - No Qdrant dependencies in core workflow
   - Simple two-document system
   - Clear documentation

## Rollback Plan

If issues arise:

```bash
# Restore from backup
cp "/Users/james/Library/Application Support/Claude/panoptikon/memory_backup_[timestamp].jsonl" \
   "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"

# Or rebuild from git state
git stash  # Save any changes
git checkout main -- docs/panoptikon_roadmap.md docs/ai_docs.md
cd scripts/knowledge
./rebuild_graph.sh
```

## Time Estimate

- Phase 1: 30 minutes (extend manager)
- Phase 2: 2 hours (create parser)
- Phase 3: 30 minutes (update scripts)
- Phase 4: 1 hour (test & validate)
- Phase 5: 30 minutes (cleanup & docs)

**Total: ~4.5 hours of focused work**

## Next Actions

1. Start with Phase 1 - extend KnowledgeGraphManager
2. Test the extensions work correctly
3. Move to Phase 2 - create the parser
4. Continue through phases sequentially
5. Validate at each step before proceeding

The system will be significantly more valuable once this cleanup is complete, providing accurate project state to the AI assistant.