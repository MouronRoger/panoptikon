# Panoptikon Phase 4 Component Prompt Creation Guide

I need you to help break down the existing Panoptikon project implementation plan into well-structured component prompts for Phase 4 (Finalization and Distribution). This is strictly about creating carefully engineered prompts for Cursor/Claude to implement code from, not about writing the actual implementation code yourself.

## Task Overview

1. Examine the existing documentation structure and implementation plan
2. Create component-specific prompts for Phase 4 ONLY
3. Reference the style guide in all prompts
4. Number components to ensure they sort alphabetically/numerically for proper sequencing
5. Incorporate testing requirements at both component and integration levels
6. Include specific build and distribution milestones

## Roles Clarification

- **Prompt/Claude (you)**: Creating the component prompts that will guide implementation
- **Cursor/Claude**: The instance that will use these prompts to implement actual code
- **Human (me)**: Reviewing and providing guidance on the prompts you create

## Phase 4 Components

Based on the implementation plan, create prompts for these components:

1. Application Bundling System (component01-app-bundling.md)
2. Code Signing Implementation (component02-code-signing.md)
3. DMG Creation System (component03-dmg-creation.md)
4. Update Mechanism (component04-update-mechanism.md)
5. User Documentation Generator (component05-user-docs.md)
6. Technical Documentation Generator (component06-technical-docs.md)
7. Release Checklist Implementation (component07-release-checklist.md)
8. UI Polish and Refinements (component08-ui-polish.md)
9. Startup Optimization (component09-startup-optimization.md)
10. Self-Diagnostics System (component10-diagnostics.md)
11. Quality Verification Scripts (component11-quality-verification.md)
12. Performance Testing System (component12-performance-testing.md)
13. Accessibility Checker (component13-accessibility-checker.md)
14. Distribution Pipeline (component14-distribution-pipeline.md)
15. Security Verification (component15-security-verification.md)
16. Auto-Update Server Integration (component16-auto-update-server.md)
17. Crash Reporting System (component17-crash-reporting.md)

## Testing & Distribution Strategy

Include these testing and distribution requirements in your component prompts:

### Component Testing (For Every Component)
- Unit tests for all public methods and functions
- Security testing for distribution components
- Verification tests for bundling and packaging
- Performance tests for startup and update operations
- Cross-platform testing where appropriate
- Minimum 80% code coverage

### Distribution Testing
Create prompts for these distribution test points:

1. After component03 (Basic Packaging Test - component03-integration-test.md)
   - Test application bundling and packaging
   - Verify code signing functionality
   - Test DMG creation and installation

2. After component07 (Release Process Test - component07-integration-test.md)
   - Test release checklist functionality
   - Verify documentation generation
   - Test complete release process flow

3. After component13 (Quality Verification Test - component13-integration-test.md)
   - Test quality verification scripts
   - Verify performance testing system
   - Test accessibility compliance

4. After component17 (Complete Distribution Test - component17-integration-test.md)
   - Test auto-update functionality
   - Verify crash reporting system
   - Test complete distribution pipeline

### Build & Distribution Milestones
Create prompts for these distribution milestones:

1. After component03 (Initial Distribution Package - phase4-initial-package.md)
   - Create signed application bundle
   - Build distributable DMG
   - Test installation process

2. After component10 (Optimized Application Build - phase4-optimized-build.md)
   - Build with UI polish and optimizations
   - Include self-diagnostics
   - Test startup performance

3. After component17 (Production Release Build - phase4-production-build.md)
   - Create final production-ready release
   - Complete auto-update and crash reporting
   - Full security verification
   - Include all documentation

### Comprehensive Testing
Include a comprehensive distribution testing prompt (phase4-distribution-testing.md) that:
- Tests installation on different macOS versions
- Verifies update mechanism with different versions
- Tests security features and signing
- Validates accessibility compliance
- Includes performance benchmarking
- Tests crash reporting and diagnostics

## Existing Structure Examination

First, explore the existing structure:

1. Check the docs directory structure:
```
list_directory /Users/james/Documents/GitHub/panoptikon/docs
list_directory /Users/james/Documents/GitHub/panoptikon/docs/cursor
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts
list_directory /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-4-prompts
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

5. Read any existing Phase 4 execution and verification prompts to break down:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase4-execution-prompt.md
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase4-verification-prompt.md
```

## Component Prompt Creation Process

For each component in the Phase 4 implementation:

1. Create a numbered component prompt file in the phase-4-prompts directory:
   * File naming: `component01-filename.md`, `component02-filename.md`, etc.
   * Use numerical prefixes with leading zeros to ensure proper sequencing

2. Each component prompt MUST:
   * Begin with a clear title and description
   * List specific requirements for that component only
   * Include interface definition with signatures and docstrings
   * Describe implementation considerations specific to distribution
   * Outline testing requirements with security and distribution testing
   * Reference the style guide
   * Specify quality standards
   * Indicate file location
   * Show example usage

3. Each component prompt should instruct Cursor/Claude to create a progress report after implementing the code:
   * File naming: `/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase4-component01.md`, etc.
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

1. **Distribution Considerations**:
   - [macOS distribution guidance]
   - [Security and signing considerations]
   - [Version management]
   - [Compatibility requirements]

2. **Error Handling**:
   - [Error handling guidance]
   - [Fallback mechanisms]
   - [Verification procedures]
   - [User feedback]

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
- Security verification
- Different macOS versions where relevant
- Error recovery and edge cases
- Integration with previous phases
- Achieve minimum 80% code coverage

For distribution components, include these specific tests:
- Verification of signing and notarization
- Installation testing
- Update mechanism verification
- Security validation
- Performance benchmarking

## Quality Standards

Your implementation must adhere to these standards:

- Complete type annotations for all functions and methods
- Comprehensive docstrings following Google style
- Maximum function length of 50 lines
- No circular dependencies
- Clear separation of concerns
- Proper error handling
- Appropriate logging
- Security best practices
- macOS distribution guidelines compliance

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
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase4-componentXX.md`

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

I need you to create integration tests for the [Module] module of the Panoptikon distribution system. These tests will verify that all components in this module work together correctly.

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

## Distribution Testing

Include distribution-specific tests that:
1. [Distribution test 1]
2. [Distribution test 2]
...

## Security Testing

Include security tests that:
1. [Security test 1]
2. [Security test 2]
...

## Test File Location

Implement these integration tests in:
`[test file path]`

## Success Criteria

The integration tests are considered successful when:
1. [Success criterion 1]
2. [Success criterion 2]
...

Please implement these integration tests. Focus on testing real-world distribution scenarios and security considerations.

After implementation, create a progress report at:
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase4-integration-test.md`
```

## Distribution Milestone Prompt Template

For distribution milestone prompts, use this structure:

```markdown
# Phase 4 [Milestone Name] Distribution

I need you to create the [milestone name] distribution package for the Panoptikon application. This distribution will include the features implemented so far and meet professional distribution standards.

## Distribution Requirements

Create a distribution package that:
1. [Distribution requirement 1]
2. [Distribution requirement 2]
...

## Components to Include

Ensure the following components are included and working:
1. [Component 1]
2. [Component 2]
3. [Component 3]
...

## Distribution Process

1. Create a distribution pipeline that packages all components
2. Implement code signing and notarization
3. Create installer or DMG
4. Configure update mechanism if applicable
5. Include appropriate documentation
6. Set up proper version identification

## Verification Steps

After creating the distribution package, verify:
1. [Verification step 1]
2. [Verification step 2]
...

## Security Verification

Perform these security checks:
1. [Security check 1]
2. [Security check 2]
...

## Known Limitations

Document these known limitations for this milestone:
1. [Limitation 1]
2. [Limitation 2]
...

## Success Criteria

The distribution is considered successful when:
1. [Success criterion 1]
2. [Success criterion 2]
...

Please implement this distribution milestone. Focus on creating a professional-quality distribution package that meets macOS standards.

After implementation, create a progress report at:
`/Users/james/Documents/GitHub/panoptikon/docs/cursor/reports/progress-phase4-milestone.md`
```

## Important Guidelines

1. DO NOT WRITE ANY IMPLEMENTATION CODE. Focus only on creating prompts.
2. CHECK WHAT ALREADY EXISTS before creating new files.
3. NUMBERED SEQUENCING is critical for human usability.
4. Each prompt should be SELF-CONTAINED but reference related components.
5. ALWAYS reference the style guide in each prompt.
6. INSTRUCT CURSOR/CLAUDE TO CREATE BREADCRUMB REPORTS after implementing each component for continuity between different Cursor/Claude instances.
7. EMPHASIZE SECURITY and VERIFICATION in all distribution component prompts.
8. INCLUDE COMPATIBILITY TESTING for different macOS versions.

## First Steps

1. Begin by checking if any Phase 4 component prompts already exist
2. Identify the first component that needs a prompt
3. Create that component prompt following the template
4. Proceed to the next component

## Examples from Previous Phases

Review the prompts from previous phases to understand the structure and detail level expected:
```
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-1-prompts/component1-file-crawler.md
read_file /Users/james/Documents/GitHub/panoptikon/docs/prompts/phase-3-prompts/component01-provider-detector.md
```

Remember: You (Prompt/Claude) are responsible for writing and saving the component prompts. Cursor/Claude will implement the code and write the progress reports. These reports create a trail for future Cursor/Claude instances to follow when implementing subsequent components.
