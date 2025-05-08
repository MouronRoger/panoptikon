# Cursor AI Documentation for Panoptikon

This directory contains documentation and guidelines for using Cursor AI to implement the Panoptikon file search application. These resources will help you create high-quality code with fewer errors.

## Contents

- **[cursor_usage_guide.md](cursor_usage_guide.md)**: Best practices for using Cursor AI effectively
- **[implementation_plan.md](implementation_plan.md)**: Breakdown of the implementation into manageable tasks
- **[prompt_template.md](prompt_template.md)**: Template for creating component-specific prompts

## Key Principles

1. **Quality First**: Focus on creating high-quality implementations
2. **One Component at a Time**: Implement and test one component before moving to the next
3. **Clear Requirements**: Provide detailed requirements for each component
4. **Verify Before Proceeding**: Test and lint code before moving forward

## Using These Resources

1. Start by reviewing the implementation plan to understand the overall approach
2. For each component, create a specific prompt using the template
3. Implement components in the recommended order to minimize dependencies
4. Verify quality at each step with linting and tests

## Prompt Strategy

Use this strategy when prompting Claude:

1. **Design First**: Ask Claude to design the interface (signatures and docstrings) first
2. **Review Before Implementation**: Review the interface before asking for implementation
3. **Focused Requests**: Ask for one file at a time, not multiple files
4. **Explicit Quality Standards**: Always include quality requirements
5. **Verify**: Always verify code with linting and testing tools

## Example Workflow

1. Choose the next component from the implementation plan
2. Create a prompt using the template
3. Ask Claude to design the interface
4. Review the interface and provide feedback
5. Ask Claude to implement the full component
6. Run linting tools and ask Claude to fix any issues
7. Ask Claude to create tests for the component
8. Verify the component works correctly
9. Document completion and move to the next component

By following this structured approach, you'll be able to create a high-quality implementation of Panoptikon efficiently.