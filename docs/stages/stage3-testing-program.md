# ## 1. Assessment Stage (1-2 days)

## Assessment Results

### Coverage Analysis for Filesystem Modules

Current coverage levels for filesystem modules:
- events.py: 100% (fully covered)
- access.py: 73% (moderate coverage)
- cloud.py: 68% (moderate coverage)
- paths.py: 57% (needs improvement)
- bookmarks.py: 35% (significant gaps)
- watcher.py: 23% (major gaps)

### Existing Test Structure
- Unit tests in `tests/core/test_filesystem_*.py`
- Integration tests in `tests/core/test_filesystem_integration.py`
- Event-based testing with mocked dependencies
- Platform-specific tests with conditional execution

### Critical Functions Needing Coverage
1. **watcher.py:** 
   - FSEventsWatcher and PollingWatcher implementations
   - Event-handling mechanisms
   - Path monitoring logic

2. **bookmarks.py:**
   - Security-scoped bookmark handling
   - Platform-specific macOS functionality
   - Bookmark persistence

3. **paths.py:**
   - Path normalization
   - Rule-based path filtering
   - Path matching

### External Dependencies to Mock
- FSEvents (macOS-specific)
- Platform-specific APIs (via PyObjC)
- File system operations
- Event bus messaging

### Key Challenges
- Platform-specific code (macOS vs. other platforms)
- Filesystem event handling timing dependencies
- Security-scoped bookmarks on macOS
- Cross-platform compatibility

**1** **Analyze current coverage for filesystem modules**
* Run coverage report focusing on filesystem modules
* Identify modules with lowest coverage first
* Determine critical paths and functionality
**1** **Review existing filesystem tests**
* Understand current test approach and patterns
* Identify gaps and potential improvements
* Check for platform-specific considerations
**1** **Code analysis**
* Examine filesystem module architecture and dependencies
* Identify complex or critical functions needing coverage
* Note any external dependencies that might need mocking

# ## 2. Strategy Development (1 day)

## Module Prioritization

Based on the assessment stage findings, we'll prioritize testing efforts as follows:

1. **watcher.py (23% coverage)**: Highest priority due to lowest coverage and critical functionality
2. **bookmarks.py (35% coverage)**: High priority due to significant gaps and security implications
3. **paths.py (57% coverage)**: Medium priority for its foundational role in path handling

## Testing Approaches by Module

### For watcher.py
1. **Unit Testing Strategy**:
   - Isolate FSEventsWatcher and PollingWatcher classes with dependency injection
   - Create mock event sources to simulate filesystem events
   - Test callback registration and event propagation mechanisms
   - Use parameterized tests for different event types (create, modify, delete)

2. **Integration Testing Strategy**:
   - Test actual filesystem monitoring with temporary directories
   - Implement controlled file operations to trigger genuine events
   - Use timeouts and synchronization mechanisms to handle asynchronous events

3. **Platform-Specific Strategy**:
   - Create conditional test suites for macOS (FSEvents) vs other platforms
   - Mock PyObjC dependencies for cross-platform testing
   - Implement platform detection in test fixtures

### For bookmarks.py
1. **Unit Testing Strategy**:
   - Mock macOS Security framework calls
   - Test bookmark data serialization/deserialization
   - Create fixtures with sample bookmark data

2. **Integration Testing Strategy**:
   - On macOS, test actual bookmark creation with limited scope
   - Implement bookmark persistence tests with temporary storage
   - Test security scope activation/deactivation sequences

3. **Cross-Platform Strategy**:
   - Implement alternative behavior testing for non-macOS platforms
   - Test graceful degradation on unsupported platforms

### For paths.py
1. **Unit Testing Strategy**:
   - Test path normalization with various input types
   - Create comprehensive test cases for path matching rules
   - Test edge cases (empty paths, invalid characters, etc.)

2. **Property-Based Testing Strategy**:
   - Generate random valid and invalid paths for testing
   - Test idempotence of normalization functions
   - Test filtering rules with varied inputs

## Test Fixture Development

1. **Filesystem Fixtures**:
   - Create temporary directory structure generator
   - Implement parameterized file content generation
   - Design fixtures for various file types (text, binary, zero-length)

2. **Event Mocking Fixtures**:
   - Create controlled event sequence generators
   - Implement timing control for event sequences
   - Design race condition simulation

3. **Platform-Specific Fixtures**:
   - Create macOS-specific bookmark fixtures
   - Implement platform detection and test skipping
   - Design cross-platform compatibility test helpers

## Mocking Strategy

1. **External Dependencies**:
   - Create mock classes for FSEvents
   - Mock PyObjC interfaces for testing on all platforms
   - Implement fake event bus for testing event propagation

2. **Filesystem Operations**:
   - Create controlled filesystem operation mocks
   - Implement predictable error conditions
   - Design timing-controllable filesystem operations

3. **Platform APIs**:
   - Create mock platform detection
   - Implement mock security-scoped bookmark APIs
   - Design abstract platform API layer for testing

## Success Criteria

1. **Coverage Targets**:
   - watcher.py: Increase from 23% to at least 80%
   - bookmarks.py: Increase from 35% to at least 75%
   - paths.py: Increase from 57% to at least 90%

2. **Quality Metrics**:
   - Test all critical path error handling
   - Ensure cross-platform test compatibility
   - Verify event handling with various timing conditions

# ## 3. Implementation Stage (3-5 days)

## Module 1: watcher.py (2 days)

### Day 1: Core Unit Testing

1. **FSEventsWatcher Implementation**:
   - Create `test_fsevents_watcher.py` with test fixtures
   - Implement mock FSEvents interface
   - Test watcher initialization with various parameters
   - Create tests for event callback registration
   
   ```python
   # Example test structure
   def test_fsevents_watcher_initialization():
       # Test with valid paths
       # Test with invalid paths
       # Test with various configuration options
   
   def test_fsevents_watcher_event_callbacks():
       # Test callback registration
       # Test callback execution on events
       # Test callback error handling
   ```

2. **PollingWatcher Implementation**:
   - Create `test_polling_watcher.py` with test fixtures
   - Test polling intervals and threading behavior
   - Verify path monitoring with mock filesystem
   - Test stopping and starting the watcher

3. **Event Handling Mechanisms**:
   - Test event normalization across watcher types
   - Verify event filtering logic
   - Test event propagation to registered handlers

### Day 2: Integration and Edge Cases

1. **Integration Testing**:
   - Create temporary directory test fixtures
   - Test actual file creation/modification/deletion detection
   - Verify correct event types are generated
   - Test with multiple watchers on overlapping directories

2. **Platform-Specific Testing**:
   - Implement platform detection for conditional tests
   - Create macOS-specific FSEvents tests
   - Test platform fallback mechanisms

3. **Edge Cases and Error Handling**:
   - Test with invalid paths and permissions
   - Test with rapid file changes
   - Test watcher recovery after filesystem errors
   - Verify memory management for long-running watchers

## Module 2: bookmarks.py (1.5 days)

### Day 1: Core Functionality

1. **Bookmark Creation and Resolution**:
   - Create `test_bookmark_creation.py`
   - Mock security framework for bookmark data generation
   - Test URL to bookmark conversion
   - Test bookmark to URL resolution
   
   ```python
   # Example test structure
   @pytest.mark.skipif(not is_macos, reason="macOS-specific functionality")
   def test_create_bookmark_from_url():
       # Test creating bookmarks from file URLs
       # Test with various file types and locations
       # Test error handling for invalid URLs
   
   def test_resolve_bookmark_to_url():
       # Test with valid bookmark data
       # Test with outdated/stale bookmarks
       # Test error handling
   ```

2. **Bookmark Persistence**:
   - Test serialization and deserialization
   - Verify bookmark data integrity
   - Test with corrupted bookmark data

### Day 2: Security and Cross-Platform

1. **Security Scope Handling**:
   - Test security scope activation
   - Test scope lifetime management
   - Verify cleanup on scope deactivation

2. **Cross-Platform Behavior**:
   - Test graceful degradation on non-macOS platforms
   - Verify error handling on unsupported platforms
   - Test alternative implementations for cross-platform compatibility

## Module 3: paths.py (1.5 days)

### Day 1: Core Path Operations

1. **Path Normalization**:
   - Create `test_path_normalization.py`
   - Test with various path formats (absolute, relative, with symbols)
   - Verify normalization is idempotent
   - Test cross-platform path handling
   
   ```python
   # Example test structure
   def test_normalize_path():
       # Test absolute paths
       # Test relative paths
       # Test paths with . and ..
       # Test paths with symlinks
       # Test with invalid characters
   
   def test_normalize_path_idempotence():
       # Verify normalized paths don't change when normalized again
   ```

2. **Path Matching and Filtering**:
   - Test pattern matching with glob patterns
   - Verify inclusion/exclusion rule application
   - Test with nested rules and complex patterns

### Day 2: Advanced Path Operations

1. **Property-Based Testing**:
   - Implement property-based tests with hypothesis
   - Generate random valid and invalid paths
   - Test path operations with generated paths

2. **Edge Cases and Optimizations**:
   - Test with very long paths
   - Test with Unicode characters
   - Verify handling of reserved filenames
   - Test performance with large path sets

## Continuous Integration

1. **Platform CI Configuration**:
   - Update CI workflow to test on multiple platforms
   - Configure platform-specific test filtering
   - Set up conditional coverage reporting

2. **Test Reporting**:
   - Configure detailed coverage reporting
   - Set up test failure categorization
   - Implement regression detection

⠀4. Verification Stage (1-2 days)
**1** **Run coverage analysis**
* Measure improvement against baseline
* Identify remaining gaps
**1** **Test quality review**
* Ensure tests are meaningful, not just covering lines
* Check for brittleness or platform dependencies
**1** **Documentation update**
* Document testing approach for filesystem modules
* Update test improvement summary

⠀5. Integration Stage (1 day)
**1** **Run full test suite**
* Ensure new tests don't break existing functionality
* Check for performance issues
**1** **Update CI/CD pipeline**
* Add any necessary changes for new tests

⠀Techniques to Apply
**1** **Filesystem mocking**:
* Use unittest.mock for file operations
* Consider filesystem abstraction libraries for testing
**1** **Platform-specific testing**:
* Create platform guards (skip tests on incompatible platforms)
* Implement platform-specific test variants
**1** **Property-based testing** for filesystem operations:
* Generate test cases for varied filenames, paths, contents
* Test with various file sizes and types
**1** **Error condition testing**:
* Permissions issues
* File not found scenarios
* Corrupted files
* Path length limitations
