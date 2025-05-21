# Minimalist MCP Knowledge System: AI Implementation Plan

## AI-to-AI Continuity Instructions

This is an implementation plan for enhancing Panoptikon's knowledge system without adopting Akro's full framework. If context token limits are reached, this document provides continuity instructions for another Claude instance to continue the implementation work.

## System Overview

- **Purpose**: Enhance AI contextual understanding without disrupting human workflow
- **Philosophy**: Land Rover approach - simplicity, robustness, fitness for purpose
- **Operation Mode**: Background system, human-triggered only on direction changes
- **Core Value**: Invisible infrastructure that improves AI assistance quality

## Core Components

| Component | Location | Purpose | Notes |
|-----------|----------|---------|-------|
| **MCP Memory** | `/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl` | Primary knowledge store | Direct file access |
| **AI Documentation** | `/docs/ai_docs.md` | Historical context log | Source of decisions |
| **Documentation Files** | `/docs/{category}/*.md` | Source of truth | Relationship extraction source |

## Relationship Types

Core set of relationship types (simplified from Akro):

```
# Primary Relationship Types

## Essential Relationships (Priority)
- contains          # Contains/implements this component
- belongs_to        # Is part of this larger entity
- depends_on        # Requires this component to function
- required_by       # Is required by this component 
- implements        # Implements this requirement
- used_by           # Components using this component

## Extended Relationships (Optional)
- affects           # Affects this component
- affected_by       # Is affected by this decision
- precedes          # Comes before this in sequence
- follows           # Comes after this in sequence
```

## Implementation

### 1. Direct MCP Memory Manager

Create a simple utility to manage MCP memory directly:

```python
#!/usr/bin/env python3
"""
MCP Memory Manager - Direct manipulation of MCP knowledge graph

Usage:
  memory_manager.py add-entity <name> <type> [<observation>]
  memory_manager.py add-relation <from> <to> <type>
  memory_manager.py list-entities [<type>]
  memory_manager.py list-relations [<from>] [<type>]
  memory_manager.py export <output_file>
  memory_manager.py import <input_file>
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Path to MCP memory file - customize as needed
MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")

class MemoryManager:
    """Manager for MCP memory file"""
    
    def __init__(self, memory_path: Path = MEMORY_PATH):
        self.memory_path = memory_path
        self.memory = self._read_memory()
    
    def _read_memory(self) -> List[Dict[str, Any]]:
        """Read memory file into list of dictionaries"""
        if not self.memory_path.exists():
            return []
        
        try:
            with open(self.memory_path, 'r') as f:
                return [json.loads(line) for line in f if line.strip()]
        except json.JSONDecodeError:
            print(f"Error: Corrupted memory file at {self.memory_path}")
            return []
    
    def _write_memory(self) -> None:
        """Write memory back to file"""
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.memory_path, 'w') as f:
            for item in self.memory:
                f.write(json.dumps(item) + '\n')
    
    def add_entity(self, name: str, entity_type: str, observation: Optional[str] = None) -> None:
        """Add a new entity to memory"""
        # Check if entity already exists
        for item in self.memory:
            if item.get('type') == 'entity' and item.get('name') == name:
                print(f"Entity already exists: {name}")
                
                # Update entity type if different
                if item.get('entityType') != entity_type:
                    item['entityType'] = entity_type
                    print(f"Updated entity type to: {entity_type}")
                
                # Add observation if provided
                if observation:
                    if 'observations' not in item:
                        item['observations'] = []
                    if observation not in item['observations']:
                        item['observations'].append(observation)
                        print(f"Added observation to entity")
                
                self._write_memory()
                return
        
        # Create new entity
        entity = {
            "type": "entity",
            "name": name,
            "entityType": entity_type,
            "observations": [observation] if observation else []
        }
        
        self.memory.append(entity)
        self._write_memory()
        print(f"Added entity: {name} [{entity_type}]")
    
    def add_relation(self, from_entity: str, to_entity: str, relation_type: str) -> None:
        """Add a relationship between entities"""
        # Ensure both entities exist
        from_exists = any(item.get('type') == 'entity' and item.get('name') == from_entity for item in self.memory)
        to_exists = any(item.get('type') == 'entity' and item.get('name') == to_entity for item in self.memory)
        
        if not from_exists:
            print(f"Warning: Source entity '{from_entity}' does not exist, creating generic entity")
            self.add_entity(from_entity, "GenericEntity")
        
        if not to_exists:
            print(f"Warning: Target entity '{to_entity}' does not exist, creating generic entity")
            self.add_entity(to_entity, "GenericEntity")
        
        # Check if relation already exists
        for item in self.memory:
            if (item.get('type') == 'relation' and 
                item.get('from') == from_entity and 
                item.get('to') == to_entity and
                item.get('relationType') == relation_type):
                print(f"Relation already exists: {from_entity} -> {to_entity} [{relation_type}]")
                return
        
        # Add new relation
        relation = {
            "type": "relation",
            "from": from_entity,
            "to": to_entity,
            "relationType": relation_type
        }
        
        self.memory.append(relation)
        self._write_memory()
        print(f"Added relation: {from_entity} -> {to_entity} [{relation_type}]")
    
    def list_entities(self, entity_type: Optional[str] = None) -> None:
        """List entities, optionally filtered by type"""
        entities = [item for item in self.memory if item.get('type') == 'entity']
        
        if entity_type:
            entities = [e for e in entities if e.get('entityType') == entity_type]
        
        if not entities:
            print(f"No entities found" + (f" of type '{entity_type}'" if entity_type else ""))
            return
        
        print(f"Found {len(entities)} entities" + (f" of type '{entity_type}'" if entity_type else ""))
        for i, entity in enumerate(entities, 1):
            obs = entity.get('observations', [])
            obs_preview = obs[0][:50] + "..." if obs and len(obs[0]) > 50 else ""
            
            print(f"{i}. {entity.get('name')} [{entity.get('entityType')}]")
            if obs_preview:
                print(f"   {obs_preview}")
    
    def list_relations(self, from_entity: Optional[str] = None, relation_type: Optional[str] = None) -> None:
        """List relations, optionally filtered by source entity or type"""
        relations = [item for item in self.memory if item.get('type') == 'relation']
        
        if from_entity:
            relations = [r for r in relations if r.get('from') == from_entity]
        
        if relation_type:
            relations = [r for r in relations if r.get('relationType') == relation_type]
        
        if not relations:
            filters = []
            if from_entity:
                filters.append(f"from '{from_entity}'")
            if relation_type:
                filters.append(f"of type '{relation_type}'")
            
            print(f"No relations found" + (f" {' and '.join(filters)}" if filters else ""))
            return
        
        print(f"Found {len(relations)} relations" + (f" from '{from_entity}'" if from_entity else "") +
              (f" of type '{relation_type}'" if relation_type else ""))
        
        for i, relation in enumerate(relations, 1):
            print(f"{i}. {relation.get('from')} -> {relation.get('to')} [{relation.get('relationType')}]")
    
    def export_memory(self, output_file: Union[str, Path]) -> None:
        """Export memory to a JSON file"""
        output_path = Path(output_file)
        
        with open(output_path, 'w') as f:
            json.dump(self.memory, f, indent=2)
        
        print(f"Exported {len(self.memory)} items to {output_path}")
    
    def import_memory(self, input_file: Union[str, Path]) -> None:
        """Import memory from a JSON file"""
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            return
        
        try:
            with open(input_path, 'r') as f:
                imported_memory = json.load(f)
            
            if not isinstance(imported_memory, list):
                print("Error: Invalid memory format, expected a list of items")
                return
            
            # Merge with existing memory, avoiding duplicates
            new_count = 0
            
            for item in imported_memory:
                if item.get('type') == 'entity':
                    # Check if entity exists
                    exists = any(e.get('type') == 'entity' and e.get('name') == item.get('name') 
                                for e in self.memory)
                    
                    if not exists:
                        self.memory.append(item)
                        new_count += 1
                
                elif item.get('type') == 'relation':
                    # Check if relation exists
                    exists = any(r.get('type') == 'relation' and 
                                r.get('from') == item.get('from') and 
                                r.get('to') == item.get('to') and
                                r.get('relationType') == item.get('relationType')
                                for r in self.memory)
                    
                    if not exists:
                        self.memory.append(item)
                        new_count += 1
            
            self._write_memory()
            print(f"Imported {new_count} new items from {input_path}")
            
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in input file: {input_path}")
            return

def print_usage():
    """Print usage information"""
    print(__doc__)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    manager = MemoryManager()
    command = sys.argv[1]
    
    if command == "add-entity":
        if len(sys.argv) < 4:
            print("Error: Missing parameters")
            print("Usage: memory_manager.py add-entity <name> <type> [<observation>]")
            sys.exit(1)
        
        name = sys.argv[2]
        entity_type = sys.argv[3]
        observation = sys.argv[4] if len(sys.argv) > 4 else None
        
        manager.add_entity(name, entity_type, observation)
    
    elif command == "add-relation":
        if len(sys.argv) < 5:
            print("Error: Missing parameters")
            print("Usage: memory_manager.py add-relation <from> <to> <type>")
            sys.exit(1)
        
        from_entity = sys.argv[2]
        to_entity = sys.argv[3]
        relation_type = sys.argv[4]
        
        manager.add_relation(from_entity, to_entity, relation_type)
    
    elif command == "list-entities":
        entity_type = sys.argv[2] if len(sys.argv) > 2 else None
        manager.list_entities(entity_type)
    
    elif command == "list-relations":
        from_entity = sys.argv[2] if len(sys.argv) > 2 else None
        relation_type = sys.argv[3] if len(sys.argv) > 3 else None
        
        manager.list_relations(from_entity, relation_type)
    
    elif command == "export":
        if len(sys.argv) < 3:
            print("Error: Missing output file")
            print("Usage: memory_manager.py export <output_file>")
            sys.exit(1)
        
        output_file = sys.argv[2]
        manager.export_memory(output_file)
    
    elif command == "import":
        if len(sys.argv) < 3:
            print("Error: Missing input file")
            print("Usage: memory_manager.py import <input_file>")
            sys.exit(1)
        
        input_file = sys.argv[2]
        manager.import_memory(input_file)
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)

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
    title_match = re.search(r'^# (.*?)

### 4. Knowledge Graph Visualization Script

Create a simple script to visualize the knowledge graph:

```python
#!/usr/bin/env python3
"""
Knowledge Graph Visualizer

Generates a GraphViz DOT file from MCP memory for visualization.
"""

import sys
from pathlib import Path
import json
import subprocess
from typing import Dict, List, Any, Optional

# Path to MCP memory file
MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")

def generate_dot(output_file: Path, focus_entity: Optional[str] = None, depth: int = 2) -> None:
    """Generate DOT file from memory"""
    # Read memory
    if not MEMORY_PATH.exists():
        print(f"Error: Memory file not found at {MEMORY_PATH}")
        return
    
    with open(MEMORY_PATH, 'r') as f:
        memory = [json.loads(line) for line in f if line.strip()]
    
    # Extract entities and relations
    entities = {}
    relations = []
    
    for item in memory:
        if item.get('type') == 'entity':
            entity_name = item.get('name')
            entity_type = item.get('entityType', 'Unknown')
            
            if entity_name:
                entities[entity_name] = {
                    'type': entity_type,
                    'observations': item.get('observations', [])
                }
        
        elif item.get('type') == 'relation':
            from_entity = item.get('from')
            to_entity = item.get('to')
            relation_type = item.get('relationType')
            
            if from_entity and to_entity and relation_type:
                relations.append({
                    'from': from_entity,
                    'to': to_entity,
                    'type': relation_type
                })
    
    # Filter by focus entity and depth if specified
    if focus_entity:
        # Find entities within specified depth
        included_entities = {focus_entity}
        frontier = {focus_entity}
        
        for _ in range(depth):
            new_frontier = set()
            
            for entity in frontier:
                # Find directly connected entities
                for relation in relations:
                    if relation['from'] == entity and relation['to'] not in included_entities:
                        included_entities.add(relation['to'])
                        new_frontier.add(relation['to'])
                    
                    if relation['to'] == entity and relation['from'] not in included_entities:
                        included_entities.add(relation['from'])
                        new_frontier.add(relation['from'])
            
            frontier = new_frontier
            if not frontier:
                break
        
        # Filter relations
        relations = [r for r in relations if r['from'] in included_entities and r['to'] in included_entities]
    
    # Generate DOT file
    with open(output_file, 'w') as f:
        f.write('digraph KnowledgeGraph {\n')
        f.write('  rankdir=LR;\n')
        f.write('  node [shape=box, style=filled, fontname="Arial"];\n')
        f.write('  edge [fontname="Arial", fontsize=10];\n\n')
        
        # Add nodes
        for name, info in entities.items():
            if focus_entity and name not in included_entities:
                continue
            
            # Determine color based on entity type
            color = '#FFFFFF'  # Default white
            
            if 'Component' in info['type']:
                color = '#E1F5FE'  # Light blue
            elif 'Decision' in info['type']:
                color = '#FFF9C4'  # Light yellow
            elif 'Requirement' in info['type']:
                color = '#E8F5E9'  # Light green
            elif 'Phase' in info['type'] or 'Stage' in info['type']:
                color = '#F3E5F5'  # Light purple
            
            # Highlight focus entity
            if focus_entity and name == focus_entity:
                color = '#FF8A65'  # Highlighted orange
            
            # Escape quotes in name
            escaped_name = name.replace('"', '\\"')
            
            f.write(f'  "{escaped_name}" [fillcolor="{color}", label="{escaped_name}\\n({info["type"]})"];\n')
        
        f.write('\n')
        
        # Add edges
        for relation in relations:
            # Determine edge color based on relation type
            color = 'black'  # Default
            
            if relation['type'] in ['contains', 'belongs_to', 'implements', 'implemented_by']:
                color = 'blue'
            elif relation['type'] in ['depends_on', 'required_by', 'calls', 'called_by']:
                color = 'red'
            elif relation['type'] in ['precedes', 'follows', 'evolves_to', 'evolved_from']:
                color = 'green'
            elif relation['type'] in ['enables', 'enabled_by', 'constrains', 'constrained_by', 
                                      'affects', 'affected_by']:
                color = 'purple'
            
            # Escape quotes in entity names
            from_escaped = relation['from'].replace('"', '\\"')
            to_escaped = relation['to'].replace('"', '\\"')
            
            f.write(f'  "{from_escaped}" -> "{to_escaped}" [label="{relation["type"]}", color="{color}"];\n')
        
        f.write('}\n')
    
    print(f"Generated DOT file: {output_file}")
    print(f"Included {len(included_entities) if focus_entity else len(entities)} entities and {len(relations)} relations")

def generate_png(dot_file: Path, output_file: Optional[Path] = None) -> None:
    """Generate PNG from DOT file using Graphviz"""
    if output_file is None:
        output_file = dot_file.with_suffix('.png')
    
    try:
        subprocess.run(['dot', '-Tpng', '-o', str(output_file), str(dot_file)], check=True)
        print(f"Generated PNG: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating PNG: {e}")
    except FileNotFoundError:
        print("Error: Graphviz dot command not found. Please install Graphviz.")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: visualize_graph.py <output_file> [focus_entity] [depth]")
        sys.exit(1)
    
    output_file = Path(sys.argv[1])
    focus_entity = sys.argv[2] if len(sys.argv) > 2 else None
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    generate_dot(output_file, focus_entity, depth)
    
    if output_file.suffix == '.dot':
        generate_png(output_file)

if __name__ == "__main__":
    main()
```

### 5. Documentation Template Generator

Create a script to generate documentation templates with relationship sections:

```python
#!/usr/bin/env python3
"""
Documentation Template Generator

Generates documentation templates with standardized relationship sections.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

DOCS_DIR = Path("/Users/james/Documents/GitHub/panoptikon/docs")

def generate_component_template(name: str, output_file: Optional[Path] = None) -> Path:
    """Generate a component documentation template"""
    if output_file is None:
        output_file = DOCS_DIR / "components" / f"{name.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {name}

## Overview
Brief description of the component's purpose and responsibility.

## Implementation
Key implementation details and technical approach.

## API
Public interface and usage examples.

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Hierarchical
- **Contains**: <!-- Child components -->
- **Belongs To**: <!-- Parent system -->
- **Implements**: <!-- Requirements implemented -->
- **Implemented By**: <!-- Implementing classes -->

### Dependencies
- **Depends On**: <!-- Components this depends on -->
- **Required By**: <!-- Components that require this -->
- **Calls**: <!-- Services/components this calls -->
- **Called By**: <!-- Who calls this component -->

### Decision Context
- **Enabled By**: <!-- Decisions that enabled this -->
- **Constrained By**: <!-- Limitations/constraints -->
- **Affects**: <!-- Components this affects -->
- **Affected By**: <!-- Decisions affecting this -->

## Testing
Testing approach and coverage information.

## Status
Current implementation status and next steps.

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Updated**: {datetime.now().strftime('%Y-%m-%d')}
- **Category**: Component
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated component template: {output_file}")
    return output_file

def generate_decision_template(title: str, output_file: Optional[Path] = None) -> Path:
    """Generate a decision documentation template"""
    if output_file is None:
        decision_id = datetime.now().strftime('%Y%m%d')
        output_file = DOCS_DIR / "decisions" / f"ADR-{decision_id}-{title.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {title}

## Status
<!-- Proposed, Accepted, Deprecated, Superseded -->
Proposed

## Context
<!-- Describe the context and problem statement -->

## Decision
<!-- The change that we're making -->

## Consequences
<!-- What becomes easier or more difficult because of this change -->

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Components
- **Affects**: <!-- Components affected by this decision -->
- **Enables**: <!-- Components enabled by this decision -->
- **Constrains**: <!-- Components constrained by this decision -->

### Other Decisions
- **Depends On**: <!-- Decisions this builds upon -->
- **Required By**: <!-- Decisions that depend on this -->
- **Supersedes**: <!-- Decisions this replaces -->
- **Superseded By**: <!-- Decisions that replace this -->

## Alternatives Considered
<!-- What other options were considered -->

## References
<!-- Additional information -->

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Author**: <!-- Your name -->
- **Category**: Decision
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated decision template: {output_file}")
    return output_file

def generate_phase_template(name: str, output_file: Optional[Path] = None) -> Path:
    """Generate a phase documentation template"""
    if output_file is None:
        output_file = DOCS_DIR / "phases" / f"{name.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {name}

## Objectives
<!-- Key objectives for this phase -->

## Components
<!-- Major components developed in this phase -->

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Timeline
- **Precedes**: <!-- Next phases -->
- **Follows**: <!-- Previous phases -->

### Dependencies
- **Depends On**: <!-- Dependencies for this phase -->
- **Required By**: <!-- Phases depending on this -->

### Implementation
- **Implements**: <!-- Requirements implemented -->
- **Contains**: <!-- Components in this phase -->

## Milestones
<!-- Key milestones -->

## Status
<!-- Current status -->

## Issues
<!-- Known issues -->

## Next Steps
<!-- Upcoming work -->

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Updated**: {datetime.now().strftime('%Y-%m-%d')}
- **Phase Number**: <!-- e.g., 4.2 -->
- **Category**: Phase
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated phase template: {output_file}")
    return output_file

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: generate_template.py <type> <name>")
        print("  type: component, decision, phase")
        print("  name: Name or title of the entity")
        sys.exit(1)
    
    template_type = sys.argv[1].lower()
    name = sys.argv[2]
    
    if template_type == "component":
        generate_component_template(name)
    elif template_type == "decision":
        generate_decision_template(name)
    elif template_type == "phase":
        generate_phase_template(name)
    else:
        print(f"Unknown template type: {template_type}")
        print("Supported types: component, decision, phase")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Workflow & Integration

### Installation

1. Create necessary directories:
   ```bash
   mkdir -p scripts/knowledge
   ```

2. Add the memory manager and extractor scripts:
   ```bash
   cp memory_manager.py scripts/knowledge/
   cp relationship_extractor.py scripts/knowledge/
   ```

3. Make them executable:
   ```bash
   chmod +x scripts/knowledge/memory_manager.py
   chmod +x scripts/knowledge/relationship_extractor.py
   ```

### Usage Workflow

#### 1. Human Triggers (Only When Needed)

When direction changes (new features, dropping features):

```bash
# Extract relationships from documentation
python scripts/knowledge/relationship_extractor.py
```

When documentation structure changes:
```bash
# Update memory directly
python scripts/knowledge/memory_manager.py add-entity "ComponentName" "Component"
python scripts/knowledge/memory_manager.py add-relation "ComponentA" "ComponentB" "depends_on"
```

#### 2. AI Knowledge Utilization

AIs should automatically leverage the knowledge graph in the background.

### AI-to-AI Prompt Strategy

When AI needs to use the knowledge graph effectively:

```
# Knowledge Graph Context Utilization

Before answering, check the Panoptikon knowledge graph:

1. Consider component relationships:
   - What components does this depend on?
   - What components depend on this?
   - What architecture does this belong to?

2. Consider project structure:
   - What phase/stage does this component belong to?
   - What decisions affect this component?

Focus on relationships that provide context to the current query.
```

## Continuity Plan

If context limitations require handoff to another Claude instance:

1. The current state of the minimalist knowledge system is:
   - One memory manager script (`memory_manager.py`) with system timestamp support
   - One relationship extractor script (`relationship_extractor.py`) with system timestamp handling
   - Documentation templates with simplified relationship sections

2. The next Claude instance should:
   - Continue implementation from the current state
   - Use the memory.jsonl file directly for knowledge continuity
   - Understand that this is a minimal system for AI knowledge only
   - Not add visualization or complex workflows
   - Maintain the Land Rover approach (simplicity, robustness, fitness)
   - Always use system timestamps, not AI-generated ones
   - Preserve existing timestamps during updates

3. Important timestamp handling guidelines:
   - Both scripts use `time.time()` to get actual system timestamps
   - Existing timestamps in memory.jsonl must be preserved
   - Never manually construct date strings or timestamps
   - Always use system time functions (time.time(), time.strftime(), etc.)
   - Don't reference dates in memory.jsonl without reading them first

4. If implementation is complete, the next instance should:
   - Test the implementation with sample documentation
   - Ensure error handling is robust
   - Validate the system meets the "invisible infrastructure" goal
, content, re.MULTILINE)
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
    rel_lines = re.finditer(r'^\s*-\s*\*\*(.*?)\*\*:\s*(.*?)

### 4. Knowledge Graph Visualization Script

Create a simple script to visualize the knowledge graph:

```python
#!/usr/bin/env python3
"""
Knowledge Graph Visualizer

Generates a GraphViz DOT file from MCP memory for visualization.
"""

import sys
from pathlib import Path
import json
import subprocess
from typing import Dict, List, Any, Optional

# Path to MCP memory file
MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")

def generate_dot(output_file: Path, focus_entity: Optional[str] = None, depth: int = 2) -> None:
    """Generate DOT file from memory"""
    # Read memory
    if not MEMORY_PATH.exists():
        print(f"Error: Memory file not found at {MEMORY_PATH}")
        return
    
    with open(MEMORY_PATH, 'r') as f:
        memory = [json.loads(line) for line in f if line.strip()]
    
    # Extract entities and relations
    entities = {}
    relations = []
    
    for item in memory:
        if item.get('type') == 'entity':
            entity_name = item.get('name')
            entity_type = item.get('entityType', 'Unknown')
            
            if entity_name:
                entities[entity_name] = {
                    'type': entity_type,
                    'observations': item.get('observations', [])
                }
        
        elif item.get('type') == 'relation':
            from_entity = item.get('from')
            to_entity = item.get('to')
            relation_type = item.get('relationType')
            
            if from_entity and to_entity and relation_type:
                relations.append({
                    'from': from_entity,
                    'to': to_entity,
                    'type': relation_type
                })
    
    # Filter by focus entity and depth if specified
    if focus_entity:
        # Find entities within specified depth
        included_entities = {focus_entity}
        frontier = {focus_entity}
        
        for _ in range(depth):
            new_frontier = set()
            
            for entity in frontier:
                # Find directly connected entities
                for relation in relations:
                    if relation['from'] == entity and relation['to'] not in included_entities:
                        included_entities.add(relation['to'])
                        new_frontier.add(relation['to'])
                    
                    if relation['to'] == entity and relation['from'] not in included_entities:
                        included_entities.add(relation['from'])
                        new_frontier.add(relation['from'])
            
            frontier = new_frontier
            if not frontier:
                break
        
        # Filter relations
        relations = [r for r in relations if r['from'] in included_entities and r['to'] in included_entities]
    
    # Generate DOT file
    with open(output_file, 'w') as f:
        f.write('digraph KnowledgeGraph {\n')
        f.write('  rankdir=LR;\n')
        f.write('  node [shape=box, style=filled, fontname="Arial"];\n')
        f.write('  edge [fontname="Arial", fontsize=10];\n\n')
        
        # Add nodes
        for name, info in entities.items():
            if focus_entity and name not in included_entities:
                continue
            
            # Determine color based on entity type
            color = '#FFFFFF'  # Default white
            
            if 'Component' in info['type']:
                color = '#E1F5FE'  # Light blue
            elif 'Decision' in info['type']:
                color = '#FFF9C4'  # Light yellow
            elif 'Requirement' in info['type']:
                color = '#E8F5E9'  # Light green
            elif 'Phase' in info['type'] or 'Stage' in info['type']:
                color = '#F3E5F5'  # Light purple
            
            # Highlight focus entity
            if focus_entity and name == focus_entity:
                color = '#FF8A65'  # Highlighted orange
            
            # Escape quotes in name
            escaped_name = name.replace('"', '\\"')
            
            f.write(f'  "{escaped_name}" [fillcolor="{color}", label="{escaped_name}\\n({info["type"]})"];\n')
        
        f.write('\n')
        
        # Add edges
        for relation in relations:
            # Determine edge color based on relation type
            color = 'black'  # Default
            
            if relation['type'] in ['contains', 'belongs_to', 'implements', 'implemented_by']:
                color = 'blue'
            elif relation['type'] in ['depends_on', 'required_by', 'calls', 'called_by']:
                color = 'red'
            elif relation['type'] in ['precedes', 'follows', 'evolves_to', 'evolved_from']:
                color = 'green'
            elif relation['type'] in ['enables', 'enabled_by', 'constrains', 'constrained_by', 
                                      'affects', 'affected_by']:
                color = 'purple'
            
            # Escape quotes in entity names
            from_escaped = relation['from'].replace('"', '\\"')
            to_escaped = relation['to'].replace('"', '\\"')
            
            f.write(f'  "{from_escaped}" -> "{to_escaped}" [label="{relation["type"]}", color="{color}"];\n')
        
        f.write('}\n')
    
    print(f"Generated DOT file: {output_file}")
    print(f"Included {len(included_entities) if focus_entity else len(entities)} entities and {len(relations)} relations")

def generate_png(dot_file: Path, output_file: Optional[Path] = None) -> None:
    """Generate PNG from DOT file using Graphviz"""
    if output_file is None:
        output_file = dot_file.with_suffix('.png')
    
    try:
        subprocess.run(['dot', '-Tpng', '-o', str(output_file), str(dot_file)], check=True)
        print(f"Generated PNG: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating PNG: {e}")
    except FileNotFoundError:
        print("Error: Graphviz dot command not found. Please install Graphviz.")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: visualize_graph.py <output_file> [focus_entity] [depth]")
        sys.exit(1)
    
    output_file = Path(sys.argv[1])
    focus_entity = sys.argv[2] if len(sys.argv) > 2 else None
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    generate_dot(output_file, focus_entity, depth)
    
    if output_file.suffix == '.dot':
        generate_png(output_file)

if __name__ == "__main__":
    main()
```

### 5. Documentation Template Generator

Create a script to generate documentation templates with relationship sections:

```python
#!/usr/bin/env python3
"""
Documentation Template Generator

Generates documentation templates with standardized relationship sections.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

DOCS_DIR = Path("/Users/james/Documents/GitHub/panoptikon/docs")

def generate_component_template(name: str, output_file: Optional[Path] = None) -> Path:
    """Generate a component documentation template"""
    if output_file is None:
        output_file = DOCS_DIR / "components" / f"{name.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {name}

## Overview
Brief description of the component's purpose and responsibility.

## Implementation
Key implementation details and technical approach.

## API
Public interface and usage examples.

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Hierarchical
- **Contains**: <!-- Child components -->
- **Belongs To**: <!-- Parent system -->
- **Implements**: <!-- Requirements implemented -->
- **Implemented By**: <!-- Implementing classes -->

### Dependencies
- **Depends On**: <!-- Components this depends on -->
- **Required By**: <!-- Components that require this -->
- **Calls**: <!-- Services/components this calls -->
- **Called By**: <!-- Who calls this component -->

### Decision Context
- **Enabled By**: <!-- Decisions that enabled this -->
- **Constrained By**: <!-- Limitations/constraints -->
- **Affects**: <!-- Components this affects -->
- **Affected By**: <!-- Decisions affecting this -->

## Testing
Testing approach and coverage information.

## Status
Current implementation status and next steps.

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Updated**: {datetime.now().strftime('%Y-%m-%d')}
- **Category**: Component
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated component template: {output_file}")
    return output_file

def generate_decision_template(title: str, output_file: Optional[Path] = None) -> Path:
    """Generate a decision documentation template"""
    if output_file is None:
        decision_id = datetime.now().strftime('%Y%m%d')
        output_file = DOCS_DIR / "decisions" / f"ADR-{decision_id}-{title.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {title}

## Status
<!-- Proposed, Accepted, Deprecated, Superseded -->
Proposed

## Context
<!-- Describe the context and problem statement -->

## Decision
<!-- The change that we're making -->

## Consequences
<!-- What becomes easier or more difficult because of this change -->

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Components
- **Affects**: <!-- Components affected by this decision -->
- **Enables**: <!-- Components enabled by this decision -->
- **Constrains**: <!-- Components constrained by this decision -->

### Other Decisions
- **Depends On**: <!-- Decisions this builds upon -->
- **Required By**: <!-- Decisions that depend on this -->
- **Supersedes**: <!-- Decisions this replaces -->
- **Superseded By**: <!-- Decisions that replace this -->

## Alternatives Considered
<!-- What other options were considered -->

## References
<!-- Additional information -->

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Author**: <!-- Your name -->
- **Category**: Decision
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated decision template: {output_file}")
    return output_file

def generate_phase_template(name: str, output_file: Optional[Path] = None) -> Path:
    """Generate a phase documentation template"""
    if output_file is None:
        output_file = DOCS_DIR / "phases" / f"{name.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {name}

## Objectives
<!-- Key objectives for this phase -->

## Components
<!-- Major components developed in this phase -->

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Timeline
- **Precedes**: <!-- Next phases -->
- **Follows**: <!-- Previous phases -->

### Dependencies
- **Depends On**: <!-- Dependencies for this phase -->
- **Required By**: <!-- Phases depending on this -->

### Implementation
- **Implements**: <!-- Requirements implemented -->
- **Contains**: <!-- Components in this phase -->

## Milestones
<!-- Key milestones -->

## Status
<!-- Current status -->

## Issues
<!-- Known issues -->

## Next Steps
<!-- Upcoming work -->

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Updated**: {datetime.now().strftime('%Y-%m-%d')}
- **Phase Number**: <!-- e.g., 4.2 -->
- **Category**: Phase
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated phase template: {output_file}")
    return output_file

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: generate_template.py <type> <name>")
        print("  type: component, decision, phase")
        print("  name: Name or title of the entity")
        sys.exit(1)
    
    template_type = sys.argv[1].lower()
    name = sys.argv[2]
    
    if template_type == "component":
        generate_component_template(name)
    elif template_type == "decision":
        generate_decision_template(name)
    elif template_type == "phase":
        generate_phase_template(name)
    else:
        print(f"Unknown template type: {template_type}")
        print("Supported types: component, decision, phase")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Best Practices and Workflows

### 1. Adding New Entities

1. Use the template generator to create a structured document:
   ```bash
   ./generate_template.py component "DatabaseConnectionPool"
   ```

2. Edit the Markdown file in your editor of choice, ensuring the relationship section is completed

3. Run the relationship extractor to update MCP memory:
   ```bash
   ./relationship_extractor.py
   ```

### 2. Querying the Knowledge Graph

1. Use the memory manager CLI to explore entities and relationships:
   ```bash
   # List all components
   ./memory_manager.py list-entities Component
   
   # Show dependencies for a specific component
   ./memory_manager.py list-relations "DatabaseConnectionPool" "depends_on"
   ```

2. Generate visualizations for complex subsystems:
   ```bash
   ./visualize_graph.py database_subsystem.dot "DatabaseConnectionPool" 3
   ```

### 3. Prompt Engineering Strategies

Include the following in AI prompts to ensure rich context utilization:

```
# Knowledge Graph Reference Guide

When answering, first check the MCP memory for relationships between components:

1. Query entity: [ENTITY_NAME]
2. Identify dependencies and hierarchical relationships
3. Consider decision context and rationale

For architecture decisions, analyze impacts and constraints:
- What components are affected by this decision?
- What decisions enabled or constrained this?
- How does this impact existing relationships?

For implementation questions, trace the component graph:
- What does this component depend on?
- What depends on this component?
- What hierarchy does it belong to?
```

### 4. Documentation Review Process

Incorporate these steps into your regular workflow:

1. **Weekly Graph Sync**: Run the relationship extractor weekly to ensure MCP memory stays updated
2. **Documentation Consistency**: Use the template generator for all new entities
3. **Visualization Check**: Generate graph visualizations before major implementation changes
4. **Relationship Quality**: Review relationship consistency and accuracy regularly

## Integration with Development Workflow

### CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# In .github/workflows/docs.yml

name: Documentation Quality

on:
  push:
    paths:
      - 'docs/**/*.md'

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml frontmatter
          
      - name: Validate relationship sections
        run: |
          python scripts/documentation/validate_relationships.py
          
      - name: Generate knowledge graph statistics
        run: |
          python scripts/documentation/kg_stats.py
          
      - name: Generate visualization
        if: success()
        run: |
          sudo apt-get install graphviz
          python scripts/documentation/visualize_graph.py kg_latest.dot
          
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: knowledge-graph-artifacts
          path: |
            kg_latest.dot
            kg_latest.png
            kg_stats.json
```

### IDE Integration (VS Code Tasks)

Add to your `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Component Template",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/generate_template.py component \"${input:componentName}\"",
      "problemMatcher": []
    },
    {
      "label": "Generate Decision Template",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/generate_template.py decision \"${input:decisionTitle}\"",
      "problemMatcher": []
    },
    {
      "label": "Update Knowledge Graph",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/relationship_extractor.py",
      "problemMatcher": []
    },
    {
      "label": "Visualize Knowledge Graph",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/visualize_graph.py ${workspaceFolder}/docs/kg_export/latest.dot",
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "componentName",
      "description": "Name of the component",
      "default": "NewComponent",
      "type": "promptString"
    },
    {
      "id": "decisionTitle",
      "description": "Title of the decision",
      "default": "New Decision",
      "type": "promptString"
    }
  ]
}
```

## Conclusion

This minimalist knowledge system achieves the best of both worlds:

1. **Invisible Infrastructure**: The system works quietly in the background without disrupting workflow
2. **AI-Optimized**: Designed specifically for AI consumption rather than human visualization
3. **On-Demand Updates**: Triggered only when project direction changes
4. **Zero Maintenance**: No regular upkeep required beyond direction changes
5. **Land Rover Approach**: Simple, robust, and focused on actual needs

The system leverages direct access to the MCP memory file to create a reliable knowledge base that supports AI work without creating technical debt or workflow overhead. It focuses exclusively on what's needed - relationship management - without unnecessary complexity.

If another Claude instance needs to continue this implementation, this document provides complete continuity information and clear next steps.

### Recommendation

Implement this minimalist system and evaluate its effectiveness over time. The explicit goal is for humans to never need to think about the knowledge graph while AIs get increasingly better context from its existence.
, rel_section, re.MULTILINE)
    
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
    print("Extracting relationships from documentation...")
    
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

### 4. Knowledge Graph Visualization Script

Create a simple script to visualize the knowledge graph:

```python
#!/usr/bin/env python3
"""
Knowledge Graph Visualizer

Generates a GraphViz DOT file from MCP memory for visualization.
"""

import sys
from pathlib import Path
import json
import subprocess
from typing import Dict, List, Any, Optional

# Path to MCP memory file
MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")

def generate_dot(output_file: Path, focus_entity: Optional[str] = None, depth: int = 2) -> None:
    """Generate DOT file from memory"""
    # Read memory
    if not MEMORY_PATH.exists():
        print(f"Error: Memory file not found at {MEMORY_PATH}")
        return
    
    with open(MEMORY_PATH, 'r') as f:
        memory = [json.loads(line) for line in f if line.strip()]
    
    # Extract entities and relations
    entities = {}
    relations = []
    
    for item in memory:
        if item.get('type') == 'entity':
            entity_name = item.get('name')
            entity_type = item.get('entityType', 'Unknown')
            
            if entity_name:
                entities[entity_name] = {
                    'type': entity_type,
                    'observations': item.get('observations', [])
                }
        
        elif item.get('type') == 'relation':
            from_entity = item.get('from')
            to_entity = item.get('to')
            relation_type = item.get('relationType')
            
            if from_entity and to_entity and relation_type:
                relations.append({
                    'from': from_entity,
                    'to': to_entity,
                    'type': relation_type
                })
    
    # Filter by focus entity and depth if specified
    if focus_entity:
        # Find entities within specified depth
        included_entities = {focus_entity}
        frontier = {focus_entity}
        
        for _ in range(depth):
            new_frontier = set()
            
            for entity in frontier:
                # Find directly connected entities
                for relation in relations:
                    if relation['from'] == entity and relation['to'] not in included_entities:
                        included_entities.add(relation['to'])
                        new_frontier.add(relation['to'])
                    
                    if relation['to'] == entity and relation['from'] not in included_entities:
                        included_entities.add(relation['from'])
                        new_frontier.add(relation['from'])
            
            frontier = new_frontier
            if not frontier:
                break
        
        # Filter relations
        relations = [r for r in relations if r['from'] in included_entities and r['to'] in included_entities]
    
    # Generate DOT file
    with open(output_file, 'w') as f:
        f.write('digraph KnowledgeGraph {\n')
        f.write('  rankdir=LR;\n')
        f.write('  node [shape=box, style=filled, fontname="Arial"];\n')
        f.write('  edge [fontname="Arial", fontsize=10];\n\n')
        
        # Add nodes
        for name, info in entities.items():
            if focus_entity and name not in included_entities:
                continue
            
            # Determine color based on entity type
            color = '#FFFFFF'  # Default white
            
            if 'Component' in info['type']:
                color = '#E1F5FE'  # Light blue
            elif 'Decision' in info['type']:
                color = '#FFF9C4'  # Light yellow
            elif 'Requirement' in info['type']:
                color = '#E8F5E9'  # Light green
            elif 'Phase' in info['type'] or 'Stage' in info['type']:
                color = '#F3E5F5'  # Light purple
            
            # Highlight focus entity
            if focus_entity and name == focus_entity:
                color = '#FF8A65'  # Highlighted orange
            
            # Escape quotes in name
            escaped_name = name.replace('"', '\\"')
            
            f.write(f'  "{escaped_name}" [fillcolor="{color}", label="{escaped_name}\\n({info["type"]})"];\n')
        
        f.write('\n')
        
        # Add edges
        for relation in relations:
            # Determine edge color based on relation type
            color = 'black'  # Default
            
            if relation['type'] in ['contains', 'belongs_to', 'implements', 'implemented_by']:
                color = 'blue'
            elif relation['type'] in ['depends_on', 'required_by', 'calls', 'called_by']:
                color = 'red'
            elif relation['type'] in ['precedes', 'follows', 'evolves_to', 'evolved_from']:
                color = 'green'
            elif relation['type'] in ['enables', 'enabled_by', 'constrains', 'constrained_by', 
                                      'affects', 'affected_by']:
                color = 'purple'
            
            # Escape quotes in entity names
            from_escaped = relation['from'].replace('"', '\\"')
            to_escaped = relation['to'].replace('"', '\\"')
            
            f.write(f'  "{from_escaped}" -> "{to_escaped}" [label="{relation["type"]}", color="{color}"];\n')
        
        f.write('}\n')
    
    print(f"Generated DOT file: {output_file}")
    print(f"Included {len(included_entities) if focus_entity else len(entities)} entities and {len(relations)} relations")

def generate_png(dot_file: Path, output_file: Optional[Path] = None) -> None:
    """Generate PNG from DOT file using Graphviz"""
    if output_file is None:
        output_file = dot_file.with_suffix('.png')
    
    try:
        subprocess.run(['dot', '-Tpng', '-o', str(output_file), str(dot_file)], check=True)
        print(f"Generated PNG: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating PNG: {e}")
    except FileNotFoundError:
        print("Error: Graphviz dot command not found. Please install Graphviz.")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: visualize_graph.py <output_file> [focus_entity] [depth]")
        sys.exit(1)
    
    output_file = Path(sys.argv[1])
    focus_entity = sys.argv[2] if len(sys.argv) > 2 else None
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    generate_dot(output_file, focus_entity, depth)
    
    if output_file.suffix == '.dot':
        generate_png(output_file)

if __name__ == "__main__":
    main()
```

### 5. Documentation Template Generator

Create a script to generate documentation templates with relationship sections:

```python
#!/usr/bin/env python3
"""
Documentation Template Generator

Generates documentation templates with standardized relationship sections.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

DOCS_DIR = Path("/Users/james/Documents/GitHub/panoptikon/docs")

def generate_component_template(name: str, output_file: Optional[Path] = None) -> Path:
    """Generate a component documentation template"""
    if output_file is None:
        output_file = DOCS_DIR / "components" / f"{name.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {name}

## Overview
Brief description of the component's purpose and responsibility.

## Implementation
Key implementation details and technical approach.

## API
Public interface and usage examples.

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Hierarchical
- **Contains**: <!-- Child components -->
- **Belongs To**: <!-- Parent system -->
- **Implements**: <!-- Requirements implemented -->
- **Implemented By**: <!-- Implementing classes -->

### Dependencies
- **Depends On**: <!-- Components this depends on -->
- **Required By**: <!-- Components that require this -->
- **Calls**: <!-- Services/components this calls -->
- **Called By**: <!-- Who calls this component -->

### Decision Context
- **Enabled By**: <!-- Decisions that enabled this -->
- **Constrained By**: <!-- Limitations/constraints -->
- **Affects**: <!-- Components this affects -->
- **Affected By**: <!-- Decisions affecting this -->

## Testing
Testing approach and coverage information.

## Status
Current implementation status and next steps.

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Updated**: {datetime.now().strftime('%Y-%m-%d')}
- **Category**: Component
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated component template: {output_file}")
    return output_file

def generate_decision_template(title: str, output_file: Optional[Path] = None) -> Path:
    """Generate a decision documentation template"""
    if output_file is None:
        decision_id = datetime.now().strftime('%Y%m%d')
        output_file = DOCS_DIR / "decisions" / f"ADR-{decision_id}-{title.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {title}

## Status
<!-- Proposed, Accepted, Deprecated, Superseded -->
Proposed

## Context
<!-- Describe the context and problem statement -->

## Decision
<!-- The change that we're making -->

## Consequences
<!-- What becomes easier or more difficult because of this change -->

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Components
- **Affects**: <!-- Components affected by this decision -->
- **Enables**: <!-- Components enabled by this decision -->
- **Constrains**: <!-- Components constrained by this decision -->

### Other Decisions
- **Depends On**: <!-- Decisions this builds upon -->
- **Required By**: <!-- Decisions that depend on this -->
- **Supersedes**: <!-- Decisions this replaces -->
- **Superseded By**: <!-- Decisions that replace this -->

## Alternatives Considered
<!-- What other options were considered -->

## References
<!-- Additional information -->

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Author**: <!-- Your name -->
- **Category**: Decision
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated decision template: {output_file}")
    return output_file

def generate_phase_template(name: str, output_file: Optional[Path] = None) -> Path:
    """Generate a phase documentation template"""
    if output_file is None:
        output_file = DOCS_DIR / "phases" / f"{name.lower().replace(' ', '-')}.md"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# {name}

## Objectives
<!-- Key objectives for this phase -->

## Components
<!-- Major components developed in this phase -->

## Relationships
<!-- Standardized section for knowledge graph representation -->

### Timeline
- **Precedes**: <!-- Next phases -->
- **Follows**: <!-- Previous phases -->

### Dependencies
- **Depends On**: <!-- Dependencies for this phase -->
- **Required By**: <!-- Phases depending on this -->

### Implementation
- **Implements**: <!-- Requirements implemented -->
- **Contains**: <!-- Components in this phase -->

## Milestones
<!-- Key milestones -->

## Status
<!-- Current status -->

## Issues
<!-- Known issues -->

## Next Steps
<!-- Upcoming work -->

## Metadata
- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Updated**: {datetime.now().strftime('%Y-%m-%d')}
- **Phase Number**: <!-- e.g., 4.2 -->
- **Category**: Phase
"""
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Generated phase template: {output_file}")
    return output_file

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: generate_template.py <type> <name>")
        print("  type: component, decision, phase")
        print("  name: Name or title of the entity")
        sys.exit(1)
    
    template_type = sys.argv[1].lower()
    name = sys.argv[2]
    
    if template_type == "component":
        generate_component_template(name)
    elif template_type == "decision":
        generate_decision_template(name)
    elif template_type == "phase":
        generate_phase_template(name)
    else:
        print(f"Unknown template type: {template_type}")
        print("Supported types: component, decision, phase")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Best Practices and Workflows

### 1. Adding New Entities

1. Use the template generator to create a structured document:
   ```bash
   ./generate_template.py component "DatabaseConnectionPool"
   ```

2. Edit the Markdown file in your editor of choice, ensuring the relationship section is completed

3. Run the relationship extractor to update MCP memory:
   ```bash
   ./relationship_extractor.py
   ```

### 2. Querying the Knowledge Graph

1. Use the memory manager CLI to explore entities and relationships:
   ```bash
   # List all components
   ./memory_manager.py list-entities Component
   
   # Show dependencies for a specific component
   ./memory_manager.py list-relations "DatabaseConnectionPool" "depends_on"
   ```

2. Generate visualizations for complex subsystems:
   ```bash
   ./visualize_graph.py database_subsystem.dot "DatabaseConnectionPool" 3
   ```

### 3. Prompt Engineering Strategies

Include the following in AI prompts to ensure rich context utilization:

```
# Knowledge Graph Reference Guide

When answering, first check the MCP memory for relationships between components:

1. Query entity: [ENTITY_NAME]
2. Identify dependencies and hierarchical relationships
3. Consider decision context and rationale

For architecture decisions, analyze impacts and constraints:
- What components are affected by this decision?
- What decisions enabled or constrained this?
- How does this impact existing relationships?

For implementation questions, trace the component graph:
- What does this component depend on?
- What depends on this component?
- What hierarchy does it belong to?
```

### 4. Documentation Review Process

Incorporate these steps into your regular workflow:

1. **Weekly Graph Sync**: Run the relationship extractor weekly to ensure MCP memory stays updated
2. **Documentation Consistency**: Use the template generator for all new entities
3. **Visualization Check**: Generate graph visualizations before major implementation changes
4. **Relationship Quality**: Review relationship consistency and accuracy regularly

## Integration with Development Workflow

### CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# In .github/workflows/docs.yml

name: Documentation Quality

on:
  push:
    paths:
      - 'docs/**/*.md'

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml frontmatter
          
      - name: Validate relationship sections
        run: |
          python scripts/documentation/validate_relationships.py
          
      - name: Generate knowledge graph statistics
        run: |
          python scripts/documentation/kg_stats.py
          
      - name: Generate visualization
        if: success()
        run: |
          sudo apt-get install graphviz
          python scripts/documentation/visualize_graph.py kg_latest.dot
          
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: knowledge-graph-artifacts
          path: |
            kg_latest.dot
            kg_latest.png
            kg_stats.json
```

### IDE Integration (VS Code Tasks)

Add to your `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Component Template",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/generate_template.py component \"${input:componentName}\"",
      "problemMatcher": []
    },
    {
      "label": "Generate Decision Template",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/generate_template.py decision \"${input:decisionTitle}\"",
      "problemMatcher": []
    },
    {
      "label": "Update Knowledge Graph",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/relationship_extractor.py",
      "problemMatcher": []
    },
    {
      "label": "Visualize Knowledge Graph",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/documentation/visualize_graph.py ${workspaceFolder}/docs/kg_export/latest.dot",
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "componentName",
      "description": "Name of the component",
      "default": "NewComponent",
      "type": "promptString"
    },
    {
      "id": "decisionTitle",
      "description": "Title of the decision",
      "default": "New Decision",
      "type": "promptString"
    }
  ]
}
```

## Migration Steps

### 1. Prepare Directory Structure

```bash
mkdir -p scripts/documentation
```

### 2. Install Initial Scripts

Copy the scripts from this document to the appropriate locations:

```bash
cp memory_manager.py scripts/documentation/
cp relationship_extractor.py scripts/documentation/
cp visualize_graph.py scripts/documentation/
cp generate_template.py scripts/documentation/
```

### 3. Export Existing Knowledge

```bash
# Export current knowledge graph to JSON format
python scripts/documentation/memory_manager.py export docs/kg_export/kg_legacy_export.json
```

### 4. Enhance Documentation Templates

Update existing documentation to include relationship sections:

```bash
# For each major component
python scripts/documentation/generate_template.py component "ComponentName"
```

### 5. Initial Relationship Extraction

```bash
# Extract relationships from updated documentation
python scripts/documentation/relationship_extractor.py
```

### 6. Validate Knowledge Graph

```bash
# List all entities and relationships
python scripts/documentation/memory_manager.py list-entities
python scripts/documentation/memory_manager.py list-relations

# Generate visualization
python scripts/documentation/visualize_graph.py docs/kg_export/knowledge_graph.dot
```

## Maintenance Requirements

1. **Weekly Sync**: Run relationship extractor weekly to ensure MCP memory is current
2. **Documentation Template**: Use for all new components/decisions/phases
3. **Pre-Implementation Check**: Visualize affected subsystems before major changes
4. **CI/CD Integration**: Include validation in your pipeline
5. **Backup**: Periodically export memory to JSON backup files

## Conclusion

This mid-path approach balances the benefits of a structured knowledge graph with practical implementation considerations. By directly manipulating the MCP memory while maintaining structured documentation, you get:

1. **Rich relationships** and context for AI assistance
2. **Direct control** of knowledge representation
3. **Visualization capabilities** for system understanding
4. **Documentation-driven** knowledge with minimal overhead
5. **Graceful degradation** with file-based backups

The approach maintains compatibility with existing Panoptikon processes while enhancing them with selected concepts from Akro.
