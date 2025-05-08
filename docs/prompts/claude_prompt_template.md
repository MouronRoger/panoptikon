# Claude Code Implementation Template

Use this template when working with Claude to implement code for the Panoptikon project.

```
I need you to implement [describe the component] for the Panoptikon file search application. 

Follow the code style guide at: /Users/james/Documents/GitHub/panoptikon/docs/style_guide.md

## Component Details
- File path: [specify the file path]
- Purpose: [describe the purpose of the component]
- Dependencies: [list any dependencies]
- Required interfaces: [describe any interfaces to implement]

## Implementation Requirements
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]
...

## Implementation Steps
1. First, create the basic structure with proper type hints
2. Implement the core functionality
3. Add comprehensive error handling
4. Add complete docstrings following Google style
5. Verify compliance with our style guide

## Testing Approach
- Unit tests should cover: [list test cases]
- Test file path: [specify the test file path]

Important rules:
- Type annotations for all parameters and return values
- Comprehensive docstrings for all functions and classes
- Keep functions under 50 lines
- Use pathlib instead of os.path
- Handle exceptions properly
- No circular dependencies

Please show the implementation and then run linting tools to check for any issues.
```

## Remember
- The more specific your requirements, the better Claude's implementation will be
- Asking Claude to think about the approach first often leads to better results
- Breaking down complex implementations into smaller parts works better
- Reference other existing code for consistent patterns
