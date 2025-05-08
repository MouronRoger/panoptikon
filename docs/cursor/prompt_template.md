# Cursor AI Prompt Template for Panoptikon Components

Use this template when creating prompts for implementing Panoptikon components with Cursor AI.

```markdown
# Component X: [Component Name] Implementation

I need you to implement the [Component] class/module for the Panoptikon file search application. This component is responsible for [brief description of responsibility].

## Requirements

The [Component] should:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]
...

## Interface

First, implement the following interface:

```python
# Include interface code here with:
# - Imports
# - Class definition
# - Method signatures with type hints
# - Docstrings
# - But leave method bodies with 'pass'
```

## Implementation Details

When implementing the [Component], pay attention to:

1. **[Aspect 1]**: [Details about implementation aspect]
2. **[Aspect 2]**: [Details about implementation aspect]
3. **[Aspect 3]**: [Details about implementation aspect]
...

## Testing

After implementing the [Component], create tests in `tests/[test path]`:

1. Test [scenario 1]
2. Test [scenario 2]
3. Test [scenario 3]
...

## Quality Standards

Your implementation must adhere to these standards:

- Complete type annotations for all functions and methods
- Comprehensive docstrings following Google style
- Maximum function length of 50 lines
- No circular dependencies
- Clear separation of concerns
- Proper error handling
- Appropriate logging

## File Location

Implement the [Component] in:
`src/panoptikon/[module path]`

## Example Usage

The [Component] will be used like this:

```python
# Include example usage code showing how this component will be used
```

Please implement this component and provide tests. Focus on quality over quantity.
```

## Tips for Creating Effective Prompts

1. **Be Specific**: Clearly define what the component should do
2. **Provide Interface**: Give Claude the method signatures to implement
3. **Set Expectations**: Explain quality standards and testing requirements
4. **Show Usage**: Demonstrate how the component will be used
5. **Focus**: Ask for one component at a time, not several
6. **Break Down**: For complex components, break into smaller pieces
7. **Set Context**: Reference other components when necessary

## Example Implementation Process

For each component:

1. Create a prompt using this template
2. Review Claude's implementation
3. Run linting and fix any issues
4. Run tests and verify functionality
5. Document the implementation in the project documentation
6. Move to the next component

Remember: quality over quantity is the key principle for Panoptikon development.