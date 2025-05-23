#!/usr/bin/env python3
"""Simple template generator - creates documentation with relationship section"""

import os
import sys
from pathlib import Path

DOCS_DIR = Path(
    os.getenv("PANOPTIKON_DOCS_DIR", "/Users/james/Documents/GitHub/panoptikon/docs")
)


def generate_template(name: str, template_type: str) -> bool:
    """Generate a simple documentation template with relationships section."""
    if template_type not in ["component", "decision", "phase"]:
        print(f"Unknown template type: {template_type}")
        print("Valid types: component, decision, phase")
        return False
    if template_type == "component":
        output_dir = DOCS_DIR / "components"
        file_name = f"{name.lower().replace(' ', '-')}.md"
    elif template_type == "decision":
        output_dir = DOCS_DIR / "decisions"
        file_name = f"decision-{name.lower().replace(' ', '-')}.md"
    else:
        output_dir = DOCS_DIR / "phases"
        file_name = f"phase-{name.lower().replace(' ', '-')}.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / file_name
    if output_path.exists():
        print(f"Error: File already exists: {output_path}")
        return False
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
    else:
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
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created template at: {output_path}")
    return True


def main() -> None:
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
