# Panoptikon Phase 3 Component Prompt Creation Guide

I need you to help break down the existing Panoptikon project implementation plan into well-structured component prompts for Phase 3 (Cloud + Extended Search). This is strictly about creating carefully engineered prompts for Cursor/Claude to implement code from, not about writing the actual implementation code yourself.

## Task Overview

1. Examine the existing documentation structure and implementation plan
2. Create component-specific prompts for Phase 3 ONLY
3. Reference the style guide in all prompts
4. Number components to ensure they sort alphabetically/numerically for proper sequencing
5. Incorporate testing requirements at both component and integration levels
6. Include specific build and run milestones

## Roles Clarification

- **Prompt/Claude (you)**: Creating the component prompts that will guide implementation
- **Cursor/Claude**: The instance that will use these prompts to implement actual code
- **Human (me)**: Reviewing and providing guidance on the prompts you create

## Phase 3 Components

Based on the implementation plan, create prompts for these components:

1. Cloud Provider Detection System (component01-provider-detector.md)
2. Cloud Provider Registry (component02-provider-registry.md)
3. iCloud Provider Implementation (component03-icloud-provider.md)
4. Dropbox Provider Implementation (component04-dropbox-provider.md)
5. Google Drive Provider Implementation (component05-gdrive-provider.md)
6. OneDrive Provider Implementation (component06-onedrive-provider.md)
7. Box Provider Implementation (component07-box-provider.md)
8. Cloud File Status Tracker (component08-cloud-status-tracker.md)
9. Cloud Filter System (component09-cloud-filter.md)
10. Cloud Metadata Extraction (component10-cloud-metadata.md)
11. Cloud Search Extensions (component11-cloud-search-extensions.md)
12. Status Change Monitoring (component12-status-change-monitor.md)
13. Advanced Search Syntax (component13-advanced-search-syntax.md)
14. Boolean Operators Implementation (component14-boolean-operators.md)
15. Size/Date Filters Implementation (component15-size-date-filters.md)
16. Search Preferences Integration (component16-search-preferences.md)
17. Incremental Index Updates (component17-incremental-indexing.md)

## Testing & Building Strategy

Include these testing requirements in your component prompts:

### Component Testing (For Every Component)
- Unit tests for all public methods and functions
- Provider-specific tests for cloud implementations
- Offline mode testing for cloud components
- Error handling tests with simulated cloud failures
- Performance tests for critical operations
- Minimum 80% code coverage

### Module Integration Testing
Create prompts for these integration test points:

1. After component02 (Cloud Provider Framework Test - component02-integration-test.md)
   - Test cloud provider detection and registry
   - Verify abstraction layer functionality
   - Test provider lifecycle management

2. After component08 (Cloud Status Test - component08-integration-test.md)
   - Test cloud status tracking across providers
   - Verify status change detection
   - Test with online/offline transitions

3. After component12 (Cloud Search Test - component12-integration-test.md)
   - Test cloud-aware search functionality
   - Verify cloud filters and metadata
   - Test with mixed local/cloud results

4. After component17 (Advanced Search Test - component17-integration-test.md)
   - Test all advanced search features
   - Verify boolean operators and filters
   - Test complex query performance
   - Validate incremental indexing

### Build Milestones
Create prompts for these build milestones:

1. After component08 (Cloud Provider Integration Build - phase3-cloud-build.md)
   - Build with core cloud provider functionality
   - Test integration with Phases 1 & 2
   - Focus on provider detection and status tracking

2. After component17 (Complete Phase 3 Build - phase3-complete-build.md)
   - Build with all Phase 3 features
   - Fully integrated with Phases 1 & 2
   - Includes advanced search and cloud integration

### Cloud Integration Testing
Include a comprehensive cloud testing prompt (phase3-cloud-testing.md) that:
- Tests all cloud providers with actual accounts
- Verifies seamless integration with local files
- Tests offline functionality and recovery
- Validates security and permissions handling
- Includes performance testing with large cloud directories

## Existing Structure Examination

First, explore the existing structure:

1. Check the docs directory structure:
```
list_directory /Users/james/Documents/GitHub/panoptikon/docs
list_directory /Users/james/Documents/GitHub/panoptikon/docs/cursor
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-3-prompts
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

5. Read any existing Phase 3 execution and verification prompts to break down:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase3-execution-prompt.md
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase3-verification-prompt.md
```

## Component Prompt Creation Process

For each component in the Phase 3 implementation:

1. Create a numbered component prompt file in the phase-3-prompts directory:
   * File naming: `component01-filename.md`, `component02-filename.md`, etc.
   * Use numerical prefixes with leading zeros to ensure proper sequencing

2. Each component prompt MUST:
   * Begin with a clear title and description
   * List specific requirements for that component only
   * Include interface definition with signatures and docstrings
   * Describe implementation considerations specific to cloud integration
   * Outline testing requirements with cloud-specific testing
   * Reference the style guide
   * Specify quality standards
   * Indicate file location
   * Show example usage

3. Each component prompt should instruct Cursor/Claude to create a progress report after implementing the code:
   * File naming: `/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase3-component01.md`, etc.
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

1. **Cloud Integration**:
   - [Cloud provider-specific guidance]
   - [API integration considerations]
   - [Offline handling]
   - [Performance considerations]

2. **Error Handling**:
   - [Error handling guidance]
   - [Fallback mechanisms]
   - [Network failure recovery]
   - [Timeout considerations]

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
- Provider-specific functionality
- Offline mode behavior
- Error recovery
- Edge cases for network operations
- Achieve minimum 80% code coverage

For cloud components, include these specific tests:
- Simulated network failure testing
- Timeout and retry behavior
- Authentication error handling
- Rate limiting compliance
- Large directory handling

## Quality Standards

Your implementation must adhere to these standards:

- Complete type annotations for all functions and methods
- Comprehensive docstrings following Google style
- Maximum function length of 50 lines
- No circular dependencies
- Clear separation of concerns
- Proper error handling
- Appropriate logging
- Efficient cloud API usage
- Graceful offline behavior

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
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase3-componentXX.md`

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

I need you to create integration tests for the [Module] module of the Panoptikon cloud integration. These tests will verify that all components in this module work together correctly.

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

## Cloud-Specific Testing

Include cloud-specific tests that:
1. [Cloud test 1]
2. [Cloud test 2]
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
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase3-integration-test.md`
```

## Build Milestone Prompt Template

For build milestone prompts, use this structure:

```markdown
# Phase 3 [Milestone Name] Build

I need you to build and verify the [milestone name] version of the Panoptikon application with cloud integration features. This build will demonstrate the cloud functionality implemented so far.

## Build Requirements

Create a buildable application that:
1. [Build requirement 1]
2. [Build requirement 2]
...

## Components to Include

Ensure the following components are included and working:
1. [Component 1]
2. [Component 2]
3. [Component 3]
...

## Build Process

1. Create a build script that packages all necessary components
2. Ensure proper integration with Phases 1 & 2
3. Configure cloud API access
4. Set up proper credentials management
5. Document any special build requirements

## Verification Steps

After building, verify:
1. [Verification step 1]
2. [Verification step 2]
...

## Cloud Testing

Test the build with these cloud-specific scenarios:
1. [Cloud test 1]
2. [Cloud test 2]
...

## Known Limitations

Document these known limitations for this milestone:
1. [Limitation 1]
2. [Limitation 2]
...

## Success Criteria

The build is considered successful when:
1. [Success criterion 1]
2. [Success criterion 2]
...

Please implement this build milestone. Focus on creating a functional application that demonstrates the cloud integration features.

After implementation, create a progress report at:
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase3-milestone.md`
```

## Important Guidelines

1. DO NOT WRITE ANY IMPLEMENTATION CODE. Focus only on creating prompts.
2. CHECK WHAT ALREADY EXISTS before creating new files.
3. NUMBERED SEQUENCING is critical for human usability.
4. Each prompt should be SELF-CONTAINED but reference related components.
5. ALWAYS reference the style guide in each prompt.
6. INSTRUCT CURSOR/CLAUDE TO CREATE BREADCRUMB REPORTS after implementing each component for continuity between different Cursor/Claude instances.
7. EMPHASIZE OFFLINE BEHAVIOR and ERROR RECOVERY in all cloud component prompts.
8. INCLUDE SECURITY CONSIDERATIONS for cloud API access.

## First Steps

1. Begin by checking if any Phase 3 component prompts already exist
2. Identify the first component that needs a prompt
3. Create that component prompt following the template
4. Proceed to the next component

## Examples from Previous Phases

Review the prompts from previous phases to understand the structure and detail level expected:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-1-prompts/component9-search-engine.md
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-2-prompts/component01-application-delegate.md
```

Remember: You (Prompt/Claude) are responsible for writing and saving the component prompts. Cursor/Claude will implement the code and write the progress reports. These reports create a trail for future Cursor/Claude instances to follow when implementing subsequent components.
