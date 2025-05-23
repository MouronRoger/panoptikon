#!/usr/bin/env python3
"""Add a template '## Relationships' section to all docs/components, docs/decisions, and docs/phases .md
files if missing.
"""

from pathlib import Path
import re

DOC_DIRS = [
    Path("docs/components"),
    Path("docs/decisions"),
    Path("docs/phases"),
]

TEMPLATES = {
    "components": """## Relationships
- **Contains**: <!-- Child components -->
- **Belongs To**: <!-- Parent system -->
- **Depends On**: <!-- Dependencies -->
- **Used By**: <!-- Components using this -->
- **Implements**: <!-- Requirements -->
""",
    "decisions": """## Relationships
- **Affects**: <!-- Components affected -->
- **Depends On**: <!-- Prior decisions -->
- **Precedes**: <!-- Subsequent decisions -->
""",
    "phases": """## Relationships
- **Contains**: <!-- Components in this phase -->
- **Depends On**: <!-- Dependencies -->
- **Precedes**: <!-- Next phases -->
- **Follows**: <!-- Previous phases -->
""",
}


def add_relationship_section(md_path: Path) -> bool:
    """Add a template relationships section if missing. Returns True if modified."""
    with open(md_path, encoding="utf-8") as f:
        content = f.read()
    if re.search(r"^## Relationships", content, re.MULTILINE):
        return False  # Already present
    # Determine doc type
    if "components" in md_path.parts:
        template = TEMPLATES["components"]
    elif "decisions" in md_path.parts:
        template = TEMPLATES["decisions"]
    elif "phases" in md_path.parts:
        template = TEMPLATES["phases"]
    else:
        return False
    # Insert after first '##' header, or at end if none
    match = re.search(r"^## .+$", content, re.MULTILINE)
    if match:
        insert_at = match.end()
        new_content = content[:insert_at] + "\n\n" + template + content[insert_at:]
    else:
        new_content = content.rstrip() + "\n\n" + template
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Added Relationships section to: {md_path}")
    return True


def main() -> None:
    """Process all .md files in target directories."""
    for doc_dir in DOC_DIRS:
        if not doc_dir.exists():
            continue
        for md_path in doc_dir.glob("*.md"):
            add_relationship_section(md_path)


if __name__ == "__main__":
    main()
