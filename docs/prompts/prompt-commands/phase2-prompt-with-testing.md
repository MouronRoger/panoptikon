# Panoptikon Phase 2 Component Prompt Creation Guide

I need you to help break down the existing Panoptikon project implementation plan into well-structured component prompts for Phase 2 (Native macOS UI). This is strictly about creating carefully engineered prompts for Cursor/Claude to implement code from, not about writing the actual implementation code yourself.

## Task Overview

1. Examine the existing documentation structure and implementation plan
2. Create component-specific prompts for Phase 2 ONLY
3. Reference the style guide in all prompts
4. Number components to ensure they sort alphabetically/numerically for proper sequencing
5. Incorporate testing requirements at both component and integration levels
6. Include specific build and run milestones

## Roles Clarification

- **Prompt/Claude (you)**: Creating the component prompts that will guide implementation
- **Cursor/Claude**: The instance that will use these prompts to implement actual code
- **Human (me)**: Reviewing and providing guidance on the prompts you create

## Phase 2 Components

Based on the execution prompt, create prompts for these components:

1. Application Delegate (component01-application-delegate.md)
2. Window Controller (component02-window-controller.md)
3. View Controller Architecture (component03-view-controller.md)
4. Application Entry Point (component04-application-entry.md)
5. Search Field Component (component05-search-field.md)
6. Results Table Component (component06-results-table.md)
7. Status Bar Component (component07-status-bar.md)
8. Toolbar Component (component08-toolbar.md)
9. File Operations Manager (component09-file-operations.md)
10. Context Menu Component (component10-context-menu.md)
11. Drag and Drop Support (component11-drag-drop.md)
12. Menu Bar Component (component12-menu-bar.md)
13. Application Menu (component13-app-menu.md)
14. Preferences Window (component14-preferences.md)
15. Search View Model (component15-search-viewmodel.md)
16. Results View Model (component16-results-viewmodel.md)
17. Application View Model (component17-app-viewmodel.md)

## Testing & Building Strategy

Include these testing requirements in your component prompts:

### Component Testing (For Every Component)
- Unit tests for all public methods and functions
- UI-specific testing for interface components
- Memory management tests for PyObjC components
- Edge case handling tests
- Error condition tests
- Minimum 80% code coverage

### Module Integration Testing
Create prompts for these integration test points:

1. After component04 (Core Application Test - component04-integration-test.md)
   - Test application startup and initialization
   - Verify window management
   - Test application lifecycle events

2. After component08 (UI Framework Test - component08-integration-test.md)
   - Test main UI components working together
   - Verify responsiveness and layout
   - Test keyboard navigation and focus management

3. After component14 (File and Menu Integration Test - component14-integration-test.md)
   - Test file operations with UI
   - Verify context menu functionality
   - Test menu bar and application menu

4. After component17 (View Model Integration Test - component17-integration-test.md)
   - Test all view models working with UI components
   - Verify data binding and updates
   - Test end-to-end UI workflows

### Build Milestones
Create prompts for these build milestones:

1. After component08 (First UI Prototype - phase2-prototype-build.md)
   - Build initial UI with core components
   - Test with Phase 1 backend
   - Focus on UI functionality, not aesthetics

2. After component17 (Complete UI Application - phase2-complete-build.md)
   - Build complete native UI application
   - Fully integrated with Phase 1 backend
   - Includes all UI features and functionality

### UI Testing
Include a comprehensive UI testing prompt (phase2-ui-testing.md) that:
- Tests all UI components with automated tests
- Verifies UI responsiveness during background operations
- Tests accessibility features
- Validates conformance to macOS design guidelines
- Includes user experience testing scenarios

## Existing Structure Examination

First, explore the existing structure:

1. Check the docs directory structure:
```
list_directory /Users/james/Documents/GitHub/panoptikon/docs
list_directory /Users/james/Documents/GitHub/panoptikon/docs/cursor
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-2-prompts
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

5. Read the large Phase 2 execution and verification prompts to break down:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase2-execution-prompt.md
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase2-verification-prompt.md
```

## Component Prompt Creation Process

For each component in the Phase 2 implementation:

1. Create a numbered component prompt file in the phase-2-prompts directory:
   * File naming: `component01-filename.md`, `component02-filename.md`, etc.
   * Use numerical prefixes with leading zeros to ensure proper sequencing

2. Each component prompt MUST:
   * Begin with a clear title and description
   * List specific requirements for that component only
   * Include interface definition with signatures and docstrings
   * Describe implementation considerations specific to PyObjC
   * Outline testing requirements, including UI-specific testing
   * Reference the style guide
   * Specify quality standards
   * Indicate file location
   * Show example usage

3. Each component prompt should instruct Cursor/Claude to create a progress report after implementing the code:
   * File naming: `/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase2-component01.md`, etc.
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

1. **PyObjC Integration**:
   - [PyObjC-specific guidance]
   - [Memory management considerations]
   - [Objective-C bridging notes]

2. **UI Considerations**:
   - [UI-specific implementation guidance]
   - [Accessibility notes]
   - [Performance considerations]

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
- UI interaction and appearance
- Memory management and resource cleanup
- Edge cases and error conditions
- Achieve minimum 80% code coverage

For UI components, include these specific tests:
- Appearance testing with different themes
- Keyboard navigation testing
- Accessibility compliance
- Responsive behavior during background operations

## Quality Standards

Your implementation must adhere to these standards:

- Complete type annotations for all functions and methods
- Comprehensive docstrings following Google style
- Maximum function length of 50 lines
- No circular dependencies
- Clear separation of concerns
- Proper error handling
- Appropriate logging
- PyObjC memory management documentation
- macOS design guideline compliance

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
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase2-componentXX.md`

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

I need you to create integration tests for the [Module] module of the Panoptikon native UI. These tests will verify that all components in this module work together correctly.

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

## UI Testing

Include UI-specific tests that:
1. [UI test 1]
2. [UI test 2]
...

## Memory Management Testing

Include memory management tests that:
1. [Memory test 1]
2. [Memory test 2]
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
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase2-integration-test.md`
```

## Build Milestone Prompt Template

For build milestone prompts, use this structure:

```markdown
# Phase 2 [Milestone Name] Build

I need you to build and verify the [milestone name] version of the Panoptikon application with its native macOS UI. This build will demonstrate the core UI functionality implemented so far.

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
2. Ensure proper bundling of Python code with PyObjC
3. Configure resource inclusion
4. Set up proper macOS application structure
5. Document any special build requirements

## Verification Steps

After building, verify:
1. [Verification step 1]
2. [Verification step 2]
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

Please implement this build milestone. Focus on creating a functional UI application that demonstrates the progress made so far.

After implementation, create a progress report at:
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase2-milestone.md`
```

## Important Guidelines

1. DO NOT WRITE ANY IMPLEMENTATION CODE. Focus only on creating prompts.
2. CHECK WHAT ALREADY EXISTS before creating new files.
3. NUMBERED SEQUENCING is critical for human usability.
4. Each prompt should be SELF-CONTAINED but reference related components.
5. ALWAYS reference the style guide in each prompt.
6. INSTRUCT CURSOR/CLAUDE TO CREATE BREADCRUMB REPORTS after implementing each component for continuity between different Cursor/Claude instances.
7. EMPHASIZE UI TESTING and MEMORY MANAGEMENT in all PyObjC component prompts.
8. INCLUDE SPECIFIC MACOS DESIGN GUIDELINES in relevant components.

## First Steps

1. Begin by checking if any Phase 2 component prompts already exist
2. Identify the first component that needs a prompt
3. Create that component prompt following the template
4. Proceed to the next component

## Examples from Phase 1

Review the Phase 1 prompts to understand the structure and detail level expected:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-1-prompts/component1-file-crawler.md
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-1-prompts/component9-search-engine.md
```

Remember: You (Prompt/Claude) are responsible for writing and saving the component prompts. Cursor/Claude will implement the code and write the progress reports. These reports create a trail for future Cursor/Claude instances to follow when implementing subsequent components.
