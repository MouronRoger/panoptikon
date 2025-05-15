#!/usr/bin/env python3
"""Test what files are found in the docs directory"""

from pathlib import Path

project_root = Path(__file__).parent.parent.parent
docs_dir = project_root / "docs"

print(f"Project root: {project_root}")
print(f"Docs directory: {docs_dir}")
print(f"Docs exists: {docs_dir.exists()}")
print()

print("All .md files found:")
md_files = list(docs_dir.rglob("*.md"))
for f in md_files:
    print(f"  {f.relative_to(docs_dir)}")

print(f"\nTotal: {len(md_files)} files")

# Check if frontmatter can be loaded
import frontmatter

test_file = md_files[0] if md_files else None
if test_file:
    print(f"\nTesting frontmatter on: {test_file.name}")
    try:
        with open(test_file) as f:
            post = frontmatter.load(f)
            print(f"  Title: {post.get('title', 'No title')}")
            print(f"  Content length: {len(post.content)}")
    except Exception as e:
        print(f"  Error: {e}")
