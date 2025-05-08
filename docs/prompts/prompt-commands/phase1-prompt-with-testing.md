# Panoptikon Phase 1 Component Prompt Creation Guide

I need you to help break down the existing Panoptikon project implementation plan into well-structured component prompts for Phase 1 (Core Indexing). This is strictly about creating carefully engineered prompts for Cursor/Claude to implement code from, not about writing the actual implementation code yourself.

## Task Overview

1. Examine the existing documentation structure and implementation plan
2. Create component-specific prompts for Phase 1 ONLY
3. Reference the style guide in all prompts
4. Number components to ensure they sort alphabetically/numerically for proper sequencing
5. Incorporate testing requirements at both component and integration levels
6. Include build and run milestones

## Roles Clarification

- **Prompt/Claude (you)**: Creating the component prompts that will guide implementation
- **Cursor/Claude**: The instance that will use these prompts to implement actual code
- **Human (me)**: Reviewing and providing guidance on the prompts you create

## Phase 1 Components

Based on the implementation plan, create prompts for these components:

1. File Crawler (component01-file-crawler.md)
2. Metadata Extractor (component02-metadata-extractor.md)
3. Database Schema (component03-database-schema.md)
4. Connection Manager (component04-connection-manager.md)
5. Database Operations (component05-database-operations.md)
6. Migration Manager (component06-migration-manager.md)
7. Indexing Manager (component07-indexing-manager.md)
8. Directory Monitor (component08-directory-monitor.md)
9. Search Engine (component09-search-engine.md)
10. Query Parser (component10-query-parser.md)
11. Filter Builder (component11-filter-builder.md)
12. Results Manager (component12-results-manager.md)
13. Terminal Interface (component13-terminal-interface.md)
14. Command Line Arguments (component14-command-line-arguments.md)

## Testing & Building Strategy

Include these testing requirements in your component prompts:

### Component Testing (For Every Component)
- Unit tests for all public methods and functions
- Edge case handling tests
- Error condition tests
- Performance tests for critical operations
- Minimum 80% code coverage

### Module Integration Testing
Create prompts for these integration test points:
1. After component07 (Indexing Module Test - component07-integration-test.md)
   - Test file crawling, metadata extraction, and indexing together
   - Verify database operations with real file data
   - Test performance with moderate data volumes

2. After component12 (Search Module Test - component12-integration-test.md)
   - Test search engine with query parser and filter builder
   - Verify results manager with actual search results
   - Test search performance with indexed data

### Application Testing
After component14, create a final Phase 1 Testing prompt (phase1-application-test.md) that:
- Tests the complete terminal application
- Verifies all components working together
- Includes end-to-end workflows
- Tests with realistic data volumes
- Validates performance requirements
- Includes usability testing of terminal interface

### Building Milestone
After component14, include a build and run milestone (phase1-build-milestone.md) that:
- Creates a functional terminal application
- Provides instructions for building the application
- Includes verification steps for core functionality
- Documents known limitations
- Sets success criteria for the milestone

## Existing Structure Examination

First, explore the existing structure:

1. Check the docs directory structure:
```
list_directory /Users/james/Documents/GitHub/panoptikon/docs
list_directory /Users/james/Documents/GitHub/panoptikon/docs/cursor
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-1-prompts
```

2. Read the implementation plan to understand phases and components:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/cursor/implementation_plan.md
```

3. Read the style guide to reference in prompts:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/cursor/style_guide.md
```

4. Read the prompt template to follow:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/cursor/prompt_template.md
```

## Component Prompt Creation Process

For each component in the Phase 1 implementation:

1. Create a numbered component prompt file in the phase-1-prompts directory:
   * File naming: `component01-filename.md`, `component02-filename.md`, etc.
   * Use numerical prefixes with leading zeros to ensure proper sequencing

2. Each component prompt MUST:
   * Begin with a clear title and description
   * List specific requirements for that component only
   * Include interface definition with signatures and docstrings
   * Describe implementation considerations
   * Outline component-level testing requirements
   * Reference the style guide
   * Specify quality standards
   * Indicate file location
   * Show example usage

3. Each component prompt should instruct Cursor/Claude to create a progress report after implementing the code:
   * File naming: `/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase1-component01.md`, etc.
   * Cursor/Claude should include what it has implemented
   * Reference what component comes next
   * Note any observations or challenges encountered during implementation
   * Include test coverage metrics and test results
   * These reports create a breadcrumb trail for continuity between Cursor/Claude instances

## Component Prompt Template

Each component prompt should follow this structure:

```markdown
# Component XX: [Component Name] Implementation

I need you to implement the [Component Name] for the Panoptikon file search application. This component is responsible for [brief description].

## Requirements

The [Component Name] should:
1. [Requirement 1]
2. [Requirement 2]
...

## Interface

First, implement the following interface:

```python
[Interface code with docstrings and type annotations]
```

## Implementation Details

When implementing the [Component Name], pay attention to:

1. **Performance Considerations**:
   - [Performance guidance]
   - [Resource management considerations]
   - [Efficiency considerations]

2. **Error Handling**:
   - [Error handling guidance]
   - [Recovery mechanisms]
   - [Logging considerations]

3. **[Additional Category]**:
   - [Additional implementation guidance]
   - [Best practices]
   - [Pitfalls to avoid]

## Testing

After implementing the [Component Name], create tests in `[test file path]`:

1. [Test requirement 1]
2. [Test requirement 2]
...

Ensure your tests cover:
- All public methods and functions
- Edge cases and error conditions
- Performance benchmarks for critical operations
- Achieve minimum 80% code coverage

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

Implement the [Component Name] in:
`[file path]`

## Example Usage

The [Component Name] will be used like this:

```python
[Example usage code]
```

Please implement this component and provide tests. Focus on quality over quantity.

After implementation, create a progress report at:
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase1-componentXX.md`

Include:
1. What you've implemented
2. Test coverage metrics
3. Any challenges encountered
4. What component comes next
```

## Integration Test Prompt Template

For integration test prompts, use this structure:

```markdown
# [Module] Integration Testing

I need you to create integration tests for the [Module] module of the Panoptikon file search application. These tests will verify that all components in this module work together correctly.

## Components to Test

The following components should be tested together:
1. [Component 1]
2. [Component 2]
3. [Component 3]
...

## Integration Test Requirements

Create integration tests that:
1. [Test requirement 1]
2. [Test requirement 2]
...

## Test Scenarios

Implement these specific test scenarios:

1. **[Scenario 1]**:
   - [Description of scenario]
   - [Expected behavior]
   - [Verification methods]

2. **[Scenario 2]**:
   - [Description of scenario]
   - [Expected behavior]
   - [Verification methods]

...

## Performance Testing

Include performance tests that:
1. [Performance test 1]
2. [Performance test 2]
...

## Test File Location

Implement these integration tests in:
`[test file path]`

## Success Criteria

The integration tests are considered successful when:
1. [Success criterion 1]
2. [Success criterion 2]
...

Please implement these integration tests. Focus on testing real-world usage patterns and interactions between components.

After implementation, create a progress report at:
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase1-integration-test.md`
```

## Application Test and Build Prompt Template

For the final application testing and build milestone, use this structure:

```markdown
# Phase 1 Application Testing and Build

I need you to create comprehensive application tests and build the Phase 1 terminal version of the Panoptikon file search application. This will verify that all Phase 1 components work together as a complete application.

## Testing Requirements

Create application-level tests that:
1. [Test requirement 1]
2. [Test requirement 2]
...

## End-to-End Test Scenarios

Implement these end-to-end test scenarios:

1. **[Scenario 1]**:
   - [Description of scenario]
   - [Test steps]
   - [Expected results]
   - [Verification methods]

2. **[Scenario 2]**:
   - [Description of scenario]
   - [Test steps]
   - [Expected results]
   - [Verification methods]

...

## Performance Testing

Create performance tests that verify:
1. Indexing performance (minimum 1000 files/second)
2. Search response time (maximum 200ms)
3. Memory usage (maximum 200MB for 100,000 files)
4. CPU utilization during background indexing

## Build Instructions

1. Create a build script that produces a runnable terminal application
2. Include all necessary dependencies
3. Configure logging and error handling
4. Create a simple installation process
5. Provide command-line documentation

## Verification Steps

After building, verify:
1. [Verification step 1]
2. [Verification step 2]
...

## Success Criteria

The Phase 1 milestone is considered successful when:
1. All application tests pass
2. The application builds successfully
3. The terminal interface is functional
4. Performance metrics meet requirements
5. User can perform basic search operations
6. Indexing works with real file systems

Please implement these tests and build steps. Focus on creating a functional terminal application that demonstrates the core capabilities of Panoptikon.

After implementation, create a progress report at:
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase1-application.md`
```

## Important Guidelines

1. DO NOT WRITE ANY IMPLEMENTATION CODE. Focus only on creating prompts.
2. CHECK WHAT ALREADY EXISTS before creating new files.
3. NUMBERED SEQUENCING is critical for human usability.
4. Each prompt should be SELF-CONTAINED but reference related components.
5. ALWAYS reference the style guide in each prompt.
6. INSTRUCT CURSOR/CLAUDE TO CREATE BREADCRUMB REPORTS after implementing each component for continuity between different Cursor/Claude instances.
7. EMPHASIZE TESTABILITY in all component prompts.
8. INCLUDE PERFORMANCE METRICS in testing requirements.

## First Steps

1. Begin by checking if any Phase 1 component prompts already exist
2. Identify the first component that needs a prompt
3. Create that component prompt following the template
4. Proceed to the next component

Remember: You (Prompt/Claude) are responsible for writing and saving the component prompts. Cursor/Claude will implement the code and write the progress reports. These reports create a trail for future Cursor/Claude instances to follow when implementing subsequent components.
