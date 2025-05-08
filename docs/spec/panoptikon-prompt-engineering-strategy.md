# Panoptikon Prompt Engineering Strategy

## 1. Introduction

This document outlines the prompt engineering strategy for developing the Panoptikon file search application using Cursor AI and Claude 3.7 Sonnet. It provides guidelines for creating effective, modular prompts that result in high-quality, maintainable code.

## 2. Prompt Engineering Principles

### 2.1 Core Principles

1. **Incrementality**: Implement one component at a time
2. **Specificity**: Provide detailed requirements for each component
3. **Quality-First**: Emphasize quality standards in every prompt
4. **Verification**: Always verify output before proceeding
5. **Test-Driven**: Request tests alongside implementation

### 2.2 The Layered Prompt Approach

Each implementation task will use a layered prompt structure:

1. **Context Layer**: Project background and current status
2. **Specification Layer**: Detailed component requirements
3. **Quality Layer**: Reiteration of quality standards
4. **Integration Layer**: How the component fits with others
5. **Verification Layer**: How to test and validate the component

## 3. Prompt Types

### 3.1 Phase Execution Prompts

Phase execution prompts initiate each development phase and outline the high-level goals and components to be implemented.

**Template**:
```
I need to implement [Phase X: Phase Name] of the Panoptikon file search application.

First, read the current project status:
read_file docs/phase[X-1]_verification.md

Then, implement the following components:

1. [Component 1 Name] ([file_path]) that:
   - [Requirement 1]
   - [Requirement 2]
   - ...

2. [Component 2 Name] ([file_path]) that:
   - [Requirement 1]
   - [Requirement 2]
   - ...

[Additional components...]

For each component:
1. Follow the project quality standards
2. Write comprehensive tests
3. Add complete type annotations and docstrings
4. [Component-specific quality requirements]

After implementation, create a detailed implementation log at 'docs/phase[X]_implementation.md' that includes:
1. Description of all implemented components
2. API documentation for each module
3. Performance characteristics
4. Test coverage report
5. Known limitations or future improvements

This document is CRITICAL for continuity as it will be used in subsequent tasks.
```

### 3.2 Component Implementation Prompts

Component prompts focus on implementing a single module or class with detailed requirements.

**Template**:
```
I need to implement the [Component Name] for Panoptikon. This component is responsible for [main responsibility].

Current project context:
[Brief description of project status and related components]

Please implement the [Component Name] ([file_path]) that:

1. Core Functionality:
   - [Detailed requirement 1]
   - [Detailed requirement 2]
   - ...

2. Interface Requirements:
   - [Interface requirement 1]
   - [Interface requirement 2]
   - ...

3. Performance Considerations:
   - [Performance requirement 1]
   - [Performance requirement 2]
   - ...

4. Error Handling:
   - [Error handling requirement 1]
   - [Error handling requirement 2]
   - ...

5. Tests ([test_file_path]):
   - [Test case 1]
   - [Test case 2]
   - ...

Quality requirements:
- Follow the project's quality standards
- Maximum file length: 500 lines
- Maximum function length: 50 lines
- Complete docstrings with Google-style format
- Full type annotations for all functions
- Test coverage >= 80%
- [Component-specific quality requirements]

Related components:
- [Related component 1]: [Brief description of relationship]
- [Related component 2]: [Brief description of relationship]
- ...

After implementation, please:
1. Run the linters to ensure code quality
2. Execute the tests to verify functionality
3. Document any design decisions or trade-offs made
```

### 3.3 Verification Prompts

Verification prompts test implemented components and document their functionality and quality.

**Template**:
```
I need to verify the [Component Name] implementation for Panoptikon.

First, examine the implementation:
read_file [file_path]

Then, examine the tests:
read_file [test_file_path]

Please perform the following verification steps:

1. Code Quality Verification:
   - Run linters: black, ruff, mypy
   - Check docstring coverage
   - Verify type annotations
   - Check function and file lengths
   - Review design patterns used

2. Functionality Testing:
   - Run the tests and report results
   - Verify all requirements are implemented
   - Test edge cases and error handling
   - Check integration with related components

3. Performance Assessment:
   - Evaluate algorithmic complexity
   - Check resource usage
   - Verify performance against requirements
   - Identify any optimization opportunities

4. Documentation Review:
   - Verify API documentation completeness
   - Check clarity of docstrings
   - Review code comments for complex sections
   - Ensure usage examples are provided

Create a verification report that includes:
1. Summary of verification results
2. Any issues or concerns found
3. Recommendations for improvements
4. Confirmation of quality standards compliance
```

### 3.4 Refactoring Prompts

Refactoring prompts address identified issues or improvements in existing code.

**Template**:
```
I need to refactor the [Component Name] in Panoptikon to address [issue or improvement].

First, examine the current implementation:
read_file [file_path]

Then, review the identified issues:
[List of issues or improvements needed]

Please refactor the component to:

1. Address these specific issues:
   - [Issue 1]: [How to address]
   - [Issue 2]: [How to address]
   - ...

2. Improve these aspects:
   - [Improvement 1]: [How to implement]
   - [Improvement 2]: [How to implement]
   - ...

3. Maintain compatibility with:
   - [Related component 1]
   - [Related component 2]
   - ...

Quality requirements:
- Maintain or improve test coverage
- Follow all project quality standards
- Document all significant changes
- Provide clear before/after comparison

After refactoring, please:
1. Run the tests to ensure no regressions
2. Verify quality standards compliance
3. Document the improvements made
```

## 4. Phase-Specific Prompting Strategy

### 4.1 Phase 0: Project Bootstrapping

**Focus Areas**:
- Quality tooling configuration
- Project structure setup
- Test framework establishment

**Prompt Strategy**:
- Comprehensive single prompt covering all setup
- Emphasis on documentation of quality standards
- Clear verification steps for the environment

### 4.2 Phase 1: MVP Backend

**Focus Areas**:
- File indexing system
- Database implementation
- Basic search functionality

**Prompt Strategy**:
- Component-by-component implementation
- Start with core data structures
- Build interfaces before implementations
- Heavy emphasis on testing

**Key Components**:
1. File Crawler
2. Database Schema
3. Search Engine Core
4. Command-line Interface

### 4.3 Phase 2: Native macOS UI

**Focus Areas**:
- PyObjC integration
- UI components
- Application lifecycle

**Prompt Strategy**:
- Architecture prompt first
- Component-by-component implementation
- Strict separation of UI and business logic
- Documentation of memory management

**Key Components**:
1. Application Framework
2. Window Controller
3. Search Interface
4. Results Display

### 4.4 Phase 3: Cloud Integration

**Focus Areas**:
- Provider detection
- Status tracking
- Search integration

**Prompt Strategy**:
- Provider interface design first
- Implementation of base functionality
- Provider-specific implementations
- Integration with search system

**Key Components**:
1. Cloud Provider Interface
2. Provider Implementations
3. Status Tracking
4. Search Extensions

### 4.5 Phase 4: Performance Optimization

**Focus Areas**:
- Search performance
- Indexing speed
- Memory efficiency

**Prompt Strategy**:
- Start with performance measurement
- Targeted optimization prompts
- Before/after benchmarking
- Documentation of trade-offs

**Key Components**:
1. Performance Benchmarks
2. Search Optimizer
3. Indexing Optimizer
4. Memory Optimizations

### 4.6 Phase 5: Distribution

**Focus Areas**:
- Application packaging
- Code signing
- Update mechanism

**Prompt Strategy**:
- Platform-specific requirements
- Security-focused prompts
- Documentation emphasis
- Final quality verification

**Key Components**:
1. Application Bundling
2. Code Signing
3. Update Mechanism
4. User Documentation

## 5. Prompt Chaining Strategy

### 5.1 Inter-Phase Chaining

Between phases, use the following chaining mechanism:

1. **Phase Completion Document**:
   - Create `phase{X}_complete.md` at end of phase
   - Document all completed components
   - List any known issues or limitations
   - Outline next phase requirements

2. **Phase Verification**:
   - Create verification prompt
   - Verify all phase requirements
   - Test integration between components
   - Create `phase{X}_verification.md`

3. **Phase Transition**:
   - Use verification document as input for next phase
   - Reference specific sections for continuity
   - Carry forward any unresolved issues

### 5.2 Intra-Phase Chaining

Within phases, use the following chaining mechanism:

1. **Component Dependency Mapping**:
   - Identify component dependencies
   - Implement components in dependency order
   - Document interfaces before implementation

2. **Implementation-Verification Cycle**:
   - Implement component
   - Verify implementation
   - Address any issues
   - Document completion

3. **Integration Verification**:
   - After related components are complete
   - Test integration between components
   - Document integration points
   - Address any integration issues

## 6. Quality Enforcement in Prompts

### 6.1 Quality Reiteration

Every implementation prompt will include:

1. **Project Quality Standards**:
   - Code style and structure requirements
   - Testing expectations
   - Documentation requirements

2. **Component-Specific Quality**:
   - Performance requirements
   - Error handling expectations
   - Special considerations

3. **Verification Requirements**:
   - How to validate the implementation
   - Test cases to cover
   - Integration points to verify

### 6.2 Quality Verification Prompts

After each significant implementation:

1. **Linting Verification**:
   - Run black, ruff, mypy
   - Check for any violations
   - Address all quality issues

2. **Test Verification**:
   - Run test suite
   - Verify coverage
   - Check test quality

3. **Documentation Verification**:
   - Verify docstring coverage
   - Check API documentation
   - Verify usage examples

## 7. Documentation Through Prompts

### 7.1 Documentation Requirements

Every prompt will require appropriate documentation:

1. **Code Documentation**:
   - Module docstrings
   - Function docstrings
   - Inline comments for complex sections

2. **API Documentation**:
   - Interface descriptions
   - Usage examples
   - Parameter documentation

3. **Architecture Documentation**:
   - Component relationships
   - Design patterns used
   - Integration points

### 7.2 Documentation Artifacts

Create and maintain these key documentation artifacts:

1. **Architecture Blueprint**:
   - Component architecture
   - Data flow
   - Module responsibilities

2. **Implementation Log**:
   - Implemented components
   - Design decisions
   - Known limitations

3. **API Reference**:
   - Public interfaces
   - Usage examples
   - Best practices

## 8. Example Prompts

### 8.1 Example: File Crawler Implementation

```
I need to implement the File Crawler component for Panoptikon. This component is responsible for recursively traversing the file system and collecting file metadata.

Current project context:
- The project structure and quality tools are set up
- We need to implement the core indexing functionality
- This component will be used by the Indexer to build the file index

Please implement the File Crawler (src/panoptikon/index/crawler.py) that:

1. Core Functionality:
   - Recursively traverses directories
   - Collects file paths and basic metadata
   - Respects inclusion/exclusion patterns
   - Supports cancellation and pausing
   - Provides progress updates
   - Handles permission errors gracefully

2. Interface Requirements:
   - Class-based implementation with clear public API
   - Generator-based traversal for memory efficiency
   - Support for filtering by patterns
   - Configuration options for depth, symlinks, etc.
   - Callback mechanism for progress reporting

3. Performance Considerations:
   - Efficient directory traversal
   - Minimal memory footprint
   - Throttling capability to limit system impact
   - Handle large directory structures efficiently

4. Error Handling:
   - Gracefully handle permission errors
   - Skip inaccessible directories
   - Log errors appropriately
   - Provide error summary

5. Tests (tests/test_index/test_crawler.py):
   - Test directory traversal
   - Test inclusion/exclusion patterns
   - Test error handling
   - Test cancellation and pausing
   - Test with mock file system

Quality requirements:
- Follow the project's quality standards
- Maximum file length: 500 lines
- Maximum function length: 50 lines
- Complete docstrings with Google-style format
- Full type annotations for all functions
- Use pathlib instead of os.path
- Test coverage >= 80%
- No bare except statements

Related components:
- Indexer (src/panoptikon/index/indexer.py): Will use the crawler to build the index
- Exclusion Patterns (src/panoptikon/index/exclusion.py): Will provide pattern matching

After implementation, please:
1. Run the linters to ensure code quality
2. Execute the tests to verify functionality
3. Document any design decisions or trade-offs made
```

### 8.2 Example: Search Engine Verification

```
I need to verify the Search Engine implementation for Panoptikon.

First, examine the implementation:
read_file src/panoptikon/search/engine.py

Then, examine the tests:
read_file tests/test_search/test_engine.py

Please perform the following verification steps:

1. Code Quality Verification:
   - Run: black src/panoptikon/search/engine.py --check
   - Run: ruff src/panoptikon/search/engine.py
   - Run: mypy src/panoptikon/search/engine.py
   - Check docstring coverage (should be ≥95%)
   - Verify type annotations for all functions
   - Check function lengths (max 50 lines)
   - Verify file length (max 500 lines)

2. Functionality Testing:
   - Run: pytest tests/test_search/test_engine.py -v
   - Verify basic search functionality
   - Check query parsing and execution
   - Test result ranking
   - Verify filter application
   - Test performance for small and large queries
   - Check integration with database layer

3. Performance Assessment:
   - Time search operations for various query sizes
   - Verify sub-200ms response for basic queries
   - Check memory usage for large result sets
   - Identify any performance bottlenecks
   - Verify query optimization is working

4. Documentation Review:
   - Check module docstring completeness
   - Verify class and method documentation
   - Review parameter and return value documentation
   - Check for usage examples where appropriate

Create a verification report that includes:
1. Summary of verification results
2. Any issues or concerns found
3. Recommendations for improvements
4. Confirmation of quality standards compliance
```

## 9. Continuous Improvement of Prompts

### 9.1 Prompt Refinement Cycle

As development progresses, continuously improve prompts through:

1. **Learning from Previous Prompts**:
   - Identify patterns in successful prompts
   - Note areas where prompts were unclear
   - Adapt future prompts based on feedback

2. **Template Evolution**:
   - Refine templates based on results
   - Add more specificity where needed
   - Remove unnecessary verbosity

3. **Knowledge Transfer**:
   - Ensure knowledge from previous phases is carried forward
   - Reference specific documents for continuity
   - Maintain consistent terminology

### 9.2 Feedback Integration

Integrate feedback from implementation results:

1. **Implementation Feedback**:
   - Note areas where implementation deviated from requirements
   - Identify ambiguities in the prompts
   - Document successful prompt patterns

2. **Quality Feedback**:
   - Track common quality issues
   - Refine quality requirements in prompts
   - Add specific examples for common problems

3. **Integration Feedback**:
   - Note integration challenges
   - Improve interface specifications
   - Clarify component relationships

## 10. Conclusion

This prompt engineering strategy provides a framework for developing Panoptikon in a systematic, quality-focused way. By following these guidelines, we can ensure:

1. **Consistent Quality**: All components meet high standards
2. **Maintainable Code**: Well-structured, documented implementation
3. **Effective Communication**: Clear requirements and validation
4. **Continuous Improvement**: Learning and adaptation throughout the process

The success of this approach relies on the careful crafting of prompts, thorough verification of outputs, and consistent application of quality standards across all phases of development.