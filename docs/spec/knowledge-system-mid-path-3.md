# Version-2 Knowledge System: Robust Minimalism

## Overview

This document outlines a "just-right" knowledge system for Panoptikon that maintains simplicity while adding key safeguards to prevent system degradation over time. It enhances the stripped-down approach with minimal additions for long-term reliability.

## Core Components

| Component | Description | Purpose |
|-----------|-------------|---------|
| **memory_manager.py** | CLI utility for direct memory manipulation | Add/list/prune entities & relations |
| **relationship_extractor.py** | Regex-based documentation extractor | Extract relationships from docs |
| **gen_template.py** | Minimal template generator | Create docs with relationship sections |
| **test_relationship_extractor.py** | Simple unit test | Prevent extractor breakage |
| **doc_lint.py** | Pre-commit hook | Ensure relationship sections are valid |

## 1. Key Improvements

### A. Safety Features

1. **Environment Variable Override**:
```python
# At the top of both scripts
import os  # Add this import

# Path to MCP memory file with environment variable override
MEMORY_PATH = Path(
    os.getenv("PANOPTIKON_MCP_MEMORY",
              "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")
)
```

2. **Simple Unit Test** (adds reliability without complexity):
```python
# test_relationship_extractor.py
import tempfile
import pytest
from relationship_extractor import extract_relationships_from_file, get_entity_type, standardize_relation_type

def test_extracts_relations():
    """Test that relationship extraction works as expected."""
    test_content = """# TestComponent
    
## Overview
Test content
    
## Relationships
- **Contains**: ComponentX, ComponentY
- **Depends On**: ComponentZ
    
## Status
Active
"""
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w+') as tmp:
        tmp.write(test_content)
        tmp.flush()
        
        # Mock the add_entity and add_relation functions
        original_add_entity = extract_relationships_from_file.__globals__.get('add_entity')
        original_add_relation = extract_relationships_from_file.__globals__.get('add_relation')
        
        try:
            # Replace with mocks that just collect calls
            relations = []
            
            def mock_add_entity(name, entity_type, observation=None):
                pass
                
            def mock_add_relation(from_entity, to_entity, relation_type):
                relations.append((from_entity, to_entity, relation_type))
            
            extract_relationships_from_file.__globals__['add_entity'] = mock_add_entity
            extract_relationships_from_file.__globals__['add_relation'] = mock_add_relation
            
            # Call the function
            extract_relationships_from_file(tmp.name)
            
            # Should extract 3 relations (2 Contains, 1 Depends On)
            assert len(relations) == 3
            assert ('TestComponent', 'ComponentX', 'contains') in relations
            assert ('TestComponent', 'ComponentY', 'contains') in relations
            assert ('TestComponent', 'ComponentZ', 'depends_on') in relations
        
        finally:
            # Restore original functions
            if original_add_entity:
                extract_relationships_from_file.__globals__['add_entity'] = original_add_entity
            if original_add_relation:
                extract_relationships_from_file.__globals__['add_relation'] = original_add_relation

def test_get_entity_type():
    """Test that entity type detection works correctly."""
    assert get_entity_type(Path("/docs/components/test.md")) == "Component"
    assert get_entity_type(Path("/docs/decisions/test.md")) == "Decision"

def test_standardize_relation_type():
    """Test that relation type standardization works correctly."""
    assert standardize_relation_type("Contains") == "contains"
    assert standardize_relation_type("Depends On") == "depends_on"
    assert standardize_relation_type("Unknown") is None
```

### B. Author Guidance

1. **Minimal Template Generator**:
```python
#!/usr/bin/env python3
"""
Simple template generator - creates documentation with relationship section
"""
import sys
import os
from pathlib import Path

# Get docs directory from environment or use default
DOCS_DIR = Path(
    os.getenv("PANOPTIKON_DOCS_DIR", 
              "/Users/james/Documents/GitHub/panoptikon/docs")
)

def generate_template(name, template_type):
    """Generate a simple documentation template with relationships section"""
    if template_type not in ["component", "decision", "phase"]:
        print(f"Unknown template type: {template_type}")
        print("Valid types: component, decision, phase")
        return False
    
    # Determine output directory and file name
    if template_type == "component":
        output_dir = DOCS_DIR / "components"
        file_name = f"{name.lower().replace(' ', '-')}.md"
    elif template_type == "decision":
        output_dir = DOCS_DIR / "decisions"
        file_name = f"decision-{name.lower().replace(' ', '-')}.md"
    else:  # phase
        output_dir = DOCS_DIR / "phases"
        file_name = f"phase-{name.lower().replace(' ', '-')}.md"
    
    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Full output path
    output_path = output_dir / file_name
    
    # Check if file already exists
    if output_path.exists():
        print(f"Error: File already exists: {output_path}")
        return False
    
    # Generate content based on template type
    if template_type == "component":
        content = f"""# {name}

## Overview
Brief description of the component.

## Implementation
Key implementation details.

## Relationships
- **Contains**: <!-- Child components -->
- **Belongs To**: <!-- Parent system -->
- **Depends On**: <!-- Dependencies -->
- **Used By**: <!-- Components using this -->
- **Implements**: <!-- Requirements -->

## Testing
Testing approach.

## Status
Current status.
"""
    elif template_type == "decision":
        content = f"""# Decision: {name}

## Status
Proposed

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?

## Relationships
- **Affects**: <!-- Components affected -->
- **Depends On**: <!-- Prior decisions -->
- **Precedes**: <!-- Subsequent decisions -->

## Alternatives
What other options were considered?
"""
    else:  # phase
        content = f"""# Phase: {name}

## Objectives
Main objectives of this phase.

## Components
Major components in this phase.

## Relationships
- **Contains**: <!-- Components in this phase -->
- **Depends On**: <!-- Dependencies -->
- **Precedes**: <!-- Next phases -->
- **Follows**: <!-- Previous phases -->

## Status
Current status.

## Issues
Known issues.
"""
    
    # Write to file
    with open(output_path, "w") as f:
        f.write(content)
    
    print(f"Created template at: {output_path}")
    return True

def main():
    """Process command line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python gen_template.py <type> <name>")
        print("  type: component, decision, phase")
        print("  name: Name of the entity (e.g., 'Connection Pool')")
        return
    
    template_type = sys.argv[1].lower()
    name = sys.argv[2]
    
    generate_template(name, template_type)

if __name__ == "__main__":
    main()
```

2. **Documentation Linter** for Pre-commit:
```python
#!/usr/bin/env python3
"""
Documentation linter - checks for empty relationship sections
"""
import re
import sys
from pathlib import Path

def check_doc_file(filepath):
    """Check a documentation file for empty relationship sections"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has a relationship section
    rel_section_match = re.search(r'## Relationships.*?(?=^##|\Z)', content, re.DOTALL | re.MULTILINE)
    if not rel_section_match:
        return True  # No relationship section, so it's valid
    
    # Check if there are relationship lines
    rel_section = rel_section_match.group(0)
    rel_lines = re.findall(r'^\s*-\s*\*\*(.*?)\*\*:', rel_section, re.MULTILINE)
    
    if not rel_lines:
        print(f"Error: {filepath} has a Relationships section but no relationship entries")
        print("Add at least one relationship line with format: - **Type**: Entity")
        return False
    
    return True

def main():
    """Check all files passed as arguments"""
    if len(sys.argv) < 2:
        print("Usage: python doc_lint.py <file1> [<file2> ...]")
        sys.exit(1)
    
    all_valid = True
    
    for filepath in sys.argv[1:]:
        if not Path(filepath).exists():
            print(f"Warning: File not found: {filepath}")
            continue
            
        if not filepath.endswith('.md'):
            continue  # Skip non-markdown files
            
        if not check_doc_file(filepath):
            all_valid = False
    
    if not all_valid:
        sys.exit(1)  # Return error code for pre-commit

if __name__ == "__main__":
    main()
```

### C. Pre-commit Configuration

Add to `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: doc-lint
        name: Documentation Linter
        entry: python scripts/knowledge/doc_lint.py
        language: system
        files: ^docs/.+\.md$
        pass_filenames: true
```

### D. Minimal CI Job

Add to `.github/workflows/knowledge.yml`:

```yaml
name: Knowledge System Tests

on:
  push:
    paths:
      - 'docs/**/*.md'
      - 'scripts/knowledge/**'

jobs:
  test-knowledge-system:
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
          pip install pytest
          
      - name: Run relationship extractor tests
        run: |
          python -m pytest scripts/knowledge/test_relationship_extractor.py -v
          
      - name: Lint documentation files
        run: |
          for file in $(find docs -name "*.md"); do
            python scripts/knowledge/doc_lint.py "$file"
          done
```
