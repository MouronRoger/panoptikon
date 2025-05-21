# Minimalist MCP Knowledge System: Stripped-Down Implementation

## AI-to-AI Continuity Instructions

This implementation plan provides the most minimal possible approach to enhancing Panoptikon's knowledge system. If context token limits are reached, this document enables another Claude instance to continue the implementation.

## System Overview

- **Purpose**: Enhance AI contextual understanding with zero human overhead
- **Philosophy**: Land Rover approach - absolute simplicity, robustness, fitness for purpose
- **Operation Mode**: Background system, human-triggered only on direction changes
- **Core Value**: Invisible infrastructure that improves AI assistance quality

## Core Components

| Component | Location | Purpose | Notes |
|-----------|----------|---------|-------|
| **MCP Memory** | `/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl` | Primary knowledge store | Direct file access |
| **Documentation Files** | `/docs/{category}/*.md` | Source of truth | Relationship extraction source |

## Relationship Types

Core set of relationship types (minimal set):

```
# Primary Relationship Types

## Essential Relationships
- contains          # Contains/implements this component
- belongs_to        # Is part of this larger entity
- depends_on        # Requires this component to function
- required_by       # Is required by this component 
- implements        # Implements this requirement
- used_by           # Components using this component
```

## Implementation: Memory Manager 

```python
#!/usr/bin/env python3
"""
Simple MCP Memory Manager - Direct manipulation of knowledge graph
"""
import json
import sys
import time  # For system timestamps
from pathlib import Path

# Path to MCP memory file
MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")

def add_entity(name, entity_type, observation=None):
    """Add entity to memory.jsonl"""
    entity = {
        "type": "entity",
        "name": name,
        "entityType": entity_type,
        "observations": [observation] if observation else [],
        "timestamp": int(time.time())  # Use system timestamp
    }
    
    # Read existing memory
    memory = []
    if MEMORY_PATH.exists():
        with open(MEMORY_PATH, 'r') as f:
            memory = [json.loads(line) for line in f if line.strip()]
    
    # Check if entity already exists
    for item in memory:
        if item.get('type') == 'entity' and item.get('name') == name:
            print(f"Entity already exists: {name}")
            # Preserve existing timestamp
            return
    
    # Add entity
    memory.append(entity)
    
    # Write back
    with open(MEMORY_PATH, 'w') as f:
        for item in memory:
            f.write(json.dumps(item) + '\n')
    
    print(f"Added entity: {name} [{entity_type}]")

def add_relation(from_entity, to_entity, relation_type):
    """Add a relationship directly to memory.jsonl"""
    relation = {
        "type": "relation",
        "from": from_entity,
        "to": to_entity,
        "relationType": relation_type,
        "timestamp": int(time.time())  # Use system timestamp
    }
    
    # Read existing memory
    memory = []
    if MEMORY_PATH.exists():
        with open(MEMORY_PATH, 'r') as f:
            memory = [json.loads(line) for line in f if line.strip()]
    
    # Check if relation already exists
    for item in memory:
        if (item.get('type') == 'relation' and 
            item.get('from') == from_entity and 
            item.get('to') == to_entity and
            item.get('relationType') == relation_type):
            print(f"Relation already exists: {from_entity} -> {to_entity} [{relation_type}]")
            # Preserve existing timestamp
            return
    
    # Add relation
    memory.append(relation)
    
    # Write back
    with open(MEMORY_PATH, 'w') as f:
        for item in memory:
            f.write(json.dumps(item) + '\n')
    
    print(f"Added relation: {from_entity} -> {to_entity} [{relation_type}]")

def prune_relations(entity_name=None):
    """Remove relations for an entity or orphaned relations"""
    memory = []
    if MEMORY_PATH.exists():
        with open(MEMORY_PATH, 'r') as f:
            memory = [json.loads(line) for line in f if line.strip()]
    
    entities = {item.get('name') for item in memory if item.get('type') == 'entity'}
    
    if entity_name:
        # Remove relations involving this entity
        original_count = len(memory)
        memory = [item for item in memory if not (
            item.get('type') == 'relation' and 
            (item.get('from') == entity_name or item.get('to') == entity_name)
        )]
        removed = original_count - len(memory)
        print(f"Removed {removed} relations involving {entity_name}")
    else:
        # Remove orphaned relations (where entities don't exist)
        original_count = len(memory)
        memory = [item for item in memory if not (
            item.get('type') == 'relation' and 
            (item.get('from') not in entities or item.get('to') not in entities)
        )]
        removed = original_count - len(memory)
        print(f"Removed {removed} orphaned relations")
    
    # Write back
    with open(MEMORY_PATH, 'w') as f:
        for item in memory:
            f.write(json.dumps(item) + '\n')

def list_memory():
    """List all entities and relations in memory"""
    if not MEMORY_PATH.exists():
        print(f"No memory file found at {MEMORY_PATH}")
        return
    
    with open(MEMORY_PATH, 'r') as f:
        memory = [json.loads(line) for line in f if line.strip()]
    
    entities = [item for item in memory if item.get('type') == 'entity']
    relations = [item for item in memory if item.get('type') == 'relation']
    
    print(f"Memory contains {len(entities)} entities and {len(relations)} relations")
    
    print("\nEntities:")
    for i, entity in enumerate(entities, 1):
        timestamp = entity.get('timestamp', 'unknown')
        print(f"{i}. {entity.get('name')} [{entity.get('entityType')}] (ts: {timestamp})")
    
    print("\nRelations:")
    for i, rel in enumerate(relations, 1):
        timestamp = rel.get('timestamp', 'unknown')
        print(f"{i}. {rel.get('from')} -> {rel.get('to')} [{rel.get('relationType')}] (ts: {timestamp})")

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  memory_manager.py add-entity <n> <type> [<observation>]")
        print("  memory_manager.py add-relation <from> <to> <type>")
        print("  memory_manager.py prune [<entity>]")
        print("  memory_manager.py list")
        return
    
    command = sys.argv[1]
    
    if command == "add-entity" and len(sys.argv) >= 4:
        name = sys.argv[2]
        entity_type = sys.argv[3]
        observation = sys.argv[4] if len(sys.argv) > 4 else None
        add_entity(name, entity_type, observation)
    
    elif command == "add-relation" and len(sys.argv) == 5:
        from_entity = sys.argv[2]
        to_entity = sys.argv[3]
        relation_type = sys.argv[4]
        add_relation(from_entity, to_entity, relation_type)
    
    elif command == "prune":
        entity_name = sys.argv[2] if len(sys.argv) > 2 else None
        prune_relations(entity_name)
    
    elif command == "list":
        list_memory()
    
    else:
        print("Invalid command or arguments")
        print("Run without arguments for usage information")

if __name__ == "__main__":
    main()
```

## Implementation: Relationship Extractor

```python
#!/usr/bin/env python3
"""
Simple Relationship Extractor - Extract relationships from documentation

Only run this when direction changes (new features, removed features)
"""
import re
import os
import time  # For system timestamps
from pathlib import Path

# Path to docs directory
DOCS_DIR = Path("/Users/james/Documents/GitHub/panoptikon/docs")

# Import memory manager from same directory
from memory_manager import add_entity, add_relation, prune_relations

def extract_relationships_from_file(filepath):
    """Extract relationships from a documentation file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract document title (entity name)
    title_match = re.search(r'^# (.*?)$', content, re.MULTILINE)
    if not title_match:
        print(f"Warning: No title found in {filepath}")
        return []
    
    entity_name = title_match.group(1).strip()
    entity_type = get_entity_type(filepath)
    
    # Extract all relationships
    relations = []
    
    # Find relationship section
    rel_section_match = re.search(r'## Relationships.*?(?=^##|\Z)', content, re.DOTALL | re.MULTILINE)
    if not rel_section_match:
        return []
    
    rel_section = rel_section_match.group(0)
    
    # Look for relationship lines with pattern: - **Type**: Entities
    rel_lines = re.finditer(r'^\s*-\s*\*\*(.*?)\*\*:\s*(.*?)$', rel_section, re.MULTILINE)
    
    for match in rel_lines:
        rel_type = match.group(1).strip()
        targets = match.group(2).strip()
        
        # Skip empty targets
        if not targets:
            continue
        
        # Split targets by commas and clean up
        target_list = [t.strip() for t in targets.split(',')]
        
        # Map relationship type to standard type
        std_type = standardize_relation_type(rel_type)
        if not std_type:
            print(f"Warning: Unknown relation type '{rel_type}' in {filepath}")
            continue
        
        # Add relations
        for target in target_list:
            if target:  # Skip empty targets
                relations.append((entity_name, target, std_type))
    
    # First create the entity
    add_entity(entity_name, entity_type)
    
    # Then add all relations
    for from_entity, to_entity, rel_type in relations:
        add_relation(from_entity, to_entity, rel_type)
    
    return relations

def get_entity_type(filepath):
    """Determine entity type from filepath"""
    parent_dir = os.path.basename(os.path.dirname(filepath))
    
    type_map = {
        'components': 'Component',
        'architecture': 'Architecture',
        'decisions': 'Decision',
        'stages': 'Stage',
        'phases': 'Phase'
    }
    
    return type_map.get(parent_dir, 'Document')

def standardize_relation_type(rel_type):
    """Map UI relationship type to standard type"""
    relation_map = {
        'Contains': 'contains',
        'Belongs To': 'belongs_to',
        'Depends On': 'depends_on',
        'Required By': 'required_by',
        'Implements': 'implements',
        'Used By': 'used_by',
        'Affects': 'affects',
        'Affected By': 'affected_by',
        'Precedes': 'precedes',
        'Follows': 'follows'
    }
    
    return relation_map.get(rel_type)

def process_directory(directory):
    """Process all markdown files in a directory"""
    dir_path = DOCS_DIR / directory
    if not dir_path.exists():
        print(f"Directory not found: {dir_path}")
        return 0
    
    count = 0
    for filepath in dir_path.glob('*.md'):
        relations = extract_relationships_from_file(filepath)
        count += len(relations)
    
    return count

def main():
    """Main entry point"""
    print(f"Extracting relationships from documentation at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    print(f"Using system timestamp: {int(time.time())}")
    
    # Process key directories
    total = 0
    for directory in ['components', 'architecture', 'decisions', 'stages', 'phases']:
        count = process_directory(directory)
        if count > 0:
            print(f"Extracted {count} relations from {directory}/")
            total += count
    
    print(f"Total relations extracted: {total}")
    
    # Clean up orphaned relations
    prune_relations()

if __name__ == "__main__":
    main()
```

## Documentation Example

### Standard Relationship Section (Example)

```markdown
## Relationships
- **Contains**: ComponentX, ComponentY
- **Depends On**: ComponentZ
- **Implements**: RequirementA
- **Used By**: ComponentB
```

## Workflow & Integration

### Installation

1. Create necessary directory:
   ```bash
   mkdir -p scripts/knowledge
   ```

2. Add the two minimal scripts:
   ```bash
   cp memory_manager.py scripts/knowledge/
   cp relationship_extractor.py scripts/knowledge/
   ```

3. Make them executable:
   ```bash
   chmod +x scripts/knowledge/memory_manager.py
   chmod +x scripts/knowledge/relationship_extractor.py
   ```

### Usage Instructions

#### Human Triggers (Only When Needed)

When direction changes (new features, dropping features):

```bash
# Extract relationships from documentation
python scripts/knowledge/relationship_extractor.py
```

Manual intervention (rarely needed):
```bash
# Direct manipulation when necessary
python scripts/knowledge/memory_manager.py add-entity "ComponentName" "Component"
python scripts/knowledge/memory_manager.py add-relation "ComponentA" "ComponentB" "depends_on"
```

## Timestamp Handling

AIs like Claude don't have access to the actual system time and may hallucinate dates. Both scripts have built-in timestamp handling to:

1. Use system time functions (time.time()) for all new records
2. Preserve existing timestamps during updates
3. Display real timestamps in logs and list output
4. Avoid AI-hallucinated dates entirely

## Continuity Plan

If context limitations require handoff to another Claude instance:

1. The current state of the system is:
   - One memory manager script (`memory_manager.py`) with system timestamp support
   - One relationship extractor script (`relationship_extractor.py`) with system timestamp handling
   - An example relationship section for documentation

2. The next Claude instance should:
   - Continue implementation from the current state
   - Maintain the minimalist approach - do not add visualization or complex workflows
   - Always use system timestamps, not AI-generated ones
   - Preserve existing timestamps during updates

## Conclusion

This stripped-down implementation achieves the Land Rover goal of absolute simplicity while providing powerful knowledge enhancement for AI tools. Key benefits:

1. **Zero Human Overhead**: System is invisible to human workflow
2. **True Minimalism**: Just two Python scripts, no dependencies
3. **AI-Optimized**: Designed specifically for AI consumption
4. **On-Demand Updates**: Triggered only when project direction changes
5. **Set-and-Forget**: No maintenance burden or CI integration

Implementation time: 1-2 days maximum. The resulting system will enhance AI assistance without introducing any workflow complexity, technical debt, or ongoing maintenance burden.
