# Cursor AI Usage Guide for Panoptikon

This guide provides best practices for using Cursor AI to implement the Panoptikon file search application. Following these guidelines will ensure high-quality code with fewer errors.

## General Principles

1. **Incremental Implementation**: Implement one component at a time
2. **Quality First**: Focus on quality over quantity
3. **Verify Before Proceeding**: Test and lint code before moving to the next component
4. **Clear Requirements**: Provide detailed requirements for each component

## Effective Prompt Structure

Structure your prompts to Cursor AI as follows:

```
I need you to implement [specific component] for Panoptikon.

## Requirements
- [Requirement 1]
- [Requirement 2]
...

## Quality Standards
- Follow Google docstring style
- Add type annotations for all parameters and returns
- Keep functions under 50 lines
- Use pathlib instead of os.path
- Handle exceptions properly

## Implementation Steps
1. First design the interface (class/function signatures)
2. Then implement the details
3. Finally, add error handling and edge cases

## Testing Approach
- Create unit tests with pytest
- Test both normal operation and edge cases
- Use parameterized tests where appropriate
```

## Component Implementation Process

For each component, follow this process:

1. **Design Phase**:
   - Define interfaces first (classes, methods, functions)
   - Get approval before proceeding to implementation
   - Identify dependencies and integration points

2. **Implementation Phase**:
   - Implement one file at a time
   - Follow coding standards rigorously
   - Add comprehensive docstrings
   - Include proper error handling

3. **Verification Phase**:
   - Run linters (black, ruff, mypy)
   - Fix any issues
   - Write tests
   - Verify functionality

4. **Integration Phase**:
   - Ensure component works with existing code
   - Check for regressions
   - Document usage patterns

## Dealing with Errors

When encountering errors:

1. **Fix Immediately**: Address errors before moving on
2. **Understand Root Cause**: Don't just fix symptoms
3. **Refactor If Needed**: Sometimes redesign is better than patches
4. **Document Lessons**: Note patterns to avoid in future implementations

## Example: Implementing the FileCrawler

### Step 1: Design the Interface

```python
from pathlib import Path
from typing import List, Set, Iterator

class FileCrawler:
    """Crawler that recursively traverses directories to find files."""
    
    def __init__(self, root_dirs: List[Path], excluded_dirs: Set[Path] = None, 
                 excluded_patterns: Set[str] = None) -> None:
        """Initialize the file crawler.
        
        Args:
            root_dirs: List of root directories to crawl
            excluded_dirs: Set of directories to exclude from crawling
            excluded_patterns: Set of glob patterns for files to exclude
        """
        pass
        
    def crawl(self) -> Iterator[Path]:
        """Recursively crawl directories and yield found files.
        
        Yields:
            Path objects for each file found
        """
        pass
```

### Step 2: Implement the FileCrawler

```python
def crawl(self) -> Iterator[Path]:
    """Recursively crawl directories and yield found files.
    
    Yields:
        Path objects for each file found
    
    Raises:
        PermissionError: If permission is denied for a directory
    """
    for root_dir in self.root_dirs:
        try:
            # Implementation details...
        except PermissionError:
            logger.warning(f"Permission denied: {root_dir}")
            continue
```

### Step 3: Write Tests

```python
def test_crawler_with_exclusions(tmp_path):
    """Test crawler correctly applies exclusion patterns."""
    # Create test directory structure
    # ...
    
    # Initialize crawler with exclusions
    crawler = FileCrawler([tmp_path], excluded_patterns={"*.tmp"})
    
    # Verify results
    found_files = list(crawler.crawl())
    assert "example.tmp" not in [p.name for p in found_files]
```

## Recommended Implementation Order

For Phase 1, implement components in this order:

1. `FileCrawler` class
2. `MetadataExtractor` class
3. Database schema and connection management
4. `IndexingManager` class
5. Basic `SearchEngine` implementation
6. Query parser and filters
7. CLI interface

This order minimizes dependencies and allows for incremental testing.
