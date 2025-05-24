#!/usr/bin/env python3
"""Check for hardcoded timestamps in documentation files.

This script helps prevent AI-generated timestamps from contaminating
the project's historical record by warning about potential hardcoded
timestamps in documentation files.
"""

import re
import sys
from pathlib import Path


def check_for_hardcoded_timestamps(filename: str) -> bool:
    """Warn about potential hardcoded timestamps.
    
    Args:
        filename: Path to the file to check
        
    Returns:
        True if no issues found, False if hardcoded timestamps detected
    """
    # Pattern to match timestamps like [2025-05-24 14:30]
    timestamp_pattern = r'\[2025-\d{2}-\d{2} \d{2}:\d{2}\]'
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return True  # Don't fail on read errors
        
    # Check if this is a documentation file that should use system timestamps
    if any(doc_file in filename for doc_file in ['ai_docs.md', 'progress.md', 'phase-']):
        matches = re.findall(timestamp_pattern, content)
        if matches:
            print(f"WARNING: Found potential hardcoded timestamps in {filename}:")
            for match in matches[:5]:  # Show first 5 matches
                print(f"  - {match}")
            print("Use system timestamps to avoid AI hallucination!")
            print("Example: from scripts.documentation.ai_docs import get_system_timestamp")
            return False
    
    return True


def main() -> None:
    """Main entry point for the timestamp checker."""
    if len(sys.argv) < 2:
        print("Usage: python timestamp_check.py <file1> [<file2> ...]")
        sys.exit(1)
    
    all_valid = True
    
    for filepath in sys.argv[1:]:
        if not Path(filepath).exists():
            print(f"Warning: File not found: {filepath}")
            continue
            
        # Only check markdown files
        if not filepath.endswith('.md'):
            continue
            
        if not check_for_hardcoded_timestamps(filepath):
            all_valid = False
    
    if not all_valid:
        sys.exit(1)  # Return error code for pre-commit


if __name__ == "__main__":
    main()
