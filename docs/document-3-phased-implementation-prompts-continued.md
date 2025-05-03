## Phase 2: Search Engine (Weeks 5-6) - Continued

### Prompt 7: Search Query Parser (Continued)

```
   - Generates optimized WHERE clauses
   - Applies appropriate type conversions
   - Has comprehensive error handling
   - Includes performance annotations

5. Comprehensive tests for all components:
   - tests/test_search/test_parser.py
   - tests/test_search/test_syntax.py
   - tests/test_search/test_filters.py
   - tests/test_search/test_compiler.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The parser should be robust, handling all documented query syntax with graceful error recovery. Implementation should follow clean design patterns with clear separation of concerns between parsing, filtering, and execution.
```

### Prompt 8: Search Engine Core

```
I need to implement the core search engine for Panoptikon that will efficiently process search queries and return relevant results. Please create:

1. A search engine (src/panoptikon/search/engine.py) that:
   - Coordinates search execution
   - Integrates with the query parser
   - Uses the database layer efficiently
   - Implements query optimization
   - Provides progress feedback
   - Handles cancellation
   - Controls resource usage
   - Implements proper error handling
   - Uses clean interface design
   - Has comprehensive logging

2. A results manager (src/panoptikon/search/results.py) that:
   - Implements lazy-loading for large result sets
   - Provides sorting on any column
   - Supports client-side filtering
   - Implements virtual results handling
   - Has consistent result object interfaces
   - Manages memory efficiently
   - Supports both sync and async patterns
   - Includes progress indicators

3. A ranking system (src/panoptikon/search/ranker.py) that:
   - Implements relevance scoring
   - Considers filename, path, and recency
   - Supports customizable ranking weights
   - Optimizes for search queries
   - Implements user feedback integration
   - Uses the strategy pattern for algorithms
   - Has clear documentation of ranking factors
   - Includes extensive testing

4. A search history manager (src/panoptikon/search/history.py) that:
   - Tracks user search queries
   - Manages saved searches
   - Provides query suggestions
   - Implements secure storage
   - Has privacy controls
   - Uses appropriate design patterns
   - Includes database integration
   - Has comprehensive tests

5. Comprehensive tests for all components:
   - tests/test_search/test_engine.py
   - tests/test_search/test_results.py
   - tests/test_search/test_ranker.py
   - tests/test_search/test_history.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The search engine must meet the 200ms response time requirement for basic queries while maintaining memory efficiency for large result sets.
```

## Phase 3: Cloud Integration (Weeks 7-8)

### Prompt 9: Cloud Provider Detection

```
I need to implement the cloud provider detection system for Panoptikon that will identify and track cloud storage locations. Please create:

1. A provider detector (src/panoptikon/cloud/detector.py) that:
   - Identifies cloud storage locations
   - Supports iCloud, Dropbox, Google Drive, OneDrive, Box
   - Uses efficient path-based detection
   - Caches results appropriately
   - Handles nested providers
   - Documents detection algorithms
   - Uses factory pattern for providers
   - Has comprehensive test coverage
   - Includes detailed logging

2. A provider registry (src/panoptikon/cloud/registry.py) that:
   - Manages provider implementation registration
   - Implements dynamic provider discovery
   - Provides clean interface abstractions
   - Supports multiple versions of providers
   - Uses dependency injection pattern
   - Has comprehensive documentation
   - Includes thorough testing
   - Follows clean design patterns

3. Provider-specific implementations:
   - src/panoptikon/cloud/providers/icloud.py
   - src/panoptikon/cloud/providers/dropbox.py
   - src/panoptikon/cloud/providers/gdrive.py
   - src/panoptikon/cloud/providers/onedrive.py
   - src/panoptikon/cloud/providers/box.py

   Each implementation should:
   - Implement a common provider interface
   - Handle provider-specific detection
   - Use efficient algorithms
   - Include comprehensive documentation
   - Have thorough test coverage
   - Follow clean design patterns

4. A cloud file status tracker (src/panoptikon/cloud/status.py) that:
   - Determines download status of cloud files
   - Works with provider-specific APIs
   - Uses heuristics when APIs unavailable
   - Handles status changes efficiently
   - Caches results appropriately
   - Has comprehensive documentation
   - Includes thorough testing
   - Uses observer pattern for updates

5. Comprehensive tests for all components:
   - tests/test_cloud/test_detector.py
   - tests/test_cloud/test_registry.py
   - tests/test_cloud/test_providers/
   - tests/test_cloud/test_status.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The implementation should prioritize performance while accurately detecting cloud storage locations. Each provider implementation should handle edge cases gracefully, with clear error recovery.
```

### Prompt 10: Cloud Search Integration

```
I need to implement the cloud search integration for Panoptikon that will allow users to filter and find files based on cloud storage status. Please create:

1. A cloud filter system (src/panoptikon/search/cloud_filter.py) that:
   - Extends the search filter system
   - Implements cloud provider filtering
   - Supports download status filtering
   - Integrates with the query parser
   - Has optimized SQL generation
   - Uses clean extension patterns
   - Includes comprehensive documentation
   - Has thorough test coverage

2. Cloud metadata extraction (src/panoptikon/cloud/metadata.py) that:
   - Extracts cloud-specific file metadata
   - Handles provider-specific attributes
   - Determines sync status efficiently
   - Caches results appropriately
   - Uses clean design patterns
   - Has comprehensive documentation
   - Includes thorough testing
   - Follows consistent interfaces

3. Cloud search extensions (src/panoptikon/search/extensions/cloud.py) that:
   - Adds cloud search syntax to the parser
   - Implements special cloud operators
   - Provides cloud-aware results sorting
   - Has optimized query generation
   - Uses clean extension patterns
   - Includes comprehensive documentation
   - Has thorough test coverage
   - Follows consistent interfaces

4. Status change monitoring (src/panoptikon/cloud/monitor.py) that:
   - Tracks cloud file status changes
   - Updates index when status changes
   - Uses efficient change detection
   - Minimizes resource usage
   - Implements observer pattern
   - Has comprehensive documentation
   - Includes thorough testing
   - Uses clean design patterns

5. Comprehensive tests for all components:
   - tests/test_search/test_cloud_filter.py
   - tests/test_cloud/test_metadata.py
   - tests/test_search/test_extensions/test_cloud.py
   - tests/test_cloud/test_monitor.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The implementation should provide seamless integration between cloud storage and search functionality, allowing users to efficiently find and filter files based on cloud provider and status.
```

## Phase 4: PyObjC UI (Weeks 9-12)

### Prompt 11: UI Architecture

```
I need to implement the UI architecture for Panoptikon using PyObjC, focusing on clean design patterns and separation of concerns. Please create:

1. An application architecture (src/panoptikon/ui/architecture.py) that:
   - Implements MVVM pattern for UI components
   - Separates view models from views
   - Uses reactive binding patterns
   - Maintains clean interfaces
   - Provides dependency injection
   - Documents component responsibilities
   - Follows AppKit best practices
   - Includes comprehensive documentation
   - Has thorough testing strategy

2. A window controller (src/panoptikon/ui/window.py) that:
   - Manages the main application window
   - Implements NSWindowController subclass
   - Handles window lifecycle correctly
   - Uses delegate patterns properly
   - Separates UI logic from business logic
   - Documents AppKit interactions
   - Includes comprehensive documentation
   - Has thorough testing approach

3. View model components (src/panoptikon/ui/viewmodels/) that:
   - Implement presenter role in MVVM
   - Manage all business logic
   - Use pure Python where possible
   - Separate UI from application logic
   - Follow immutable patterns where appropriate
   - Include comprehensive documentation
   - Have thorough test coverage
   - Use clean design patterns

4. UI components (src/panoptikon/ui/components/) that:
   - Implement atomic UI elements
   - Follow compositional patterns
   - Use consistent styling
   - Separate appearance from behavior
   - Document accessibility features
   - Include comprehensive documentation
   - Have thorough testing approach
   - Use consistent naming conventions

5. Comprehensive tests:
   - tests/test_ui/test_architecture.py
   - tests/test_ui/test_window.py
   - tests/test_ui/test_viewmodels/
   - tests/test_ui/test_components/

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The UI architecture should strictly separate business logic from presentation, allowing view models to be tested independently of UI components. Memory management approaches for Objective-C interop should be clearly documented.
```

### Prompt 12: Search Interface Implementation

```
I need to implement the search interface components for Panoptikon using PyObjC, focusing on responsive user experience and clean integration with the search engine. Please create:

1. A search field component (src/panoptikon/ui/components/search_field.py) that:
   - Implements NSSearchField wrapper
   - Provides as-you-type searching
   - Handles query history
   - Implements keyboard shortcuts
   - Uses proper delegate patterns
   - Follows AppKit best practices
   - Documents memory management
   - Includes comprehensive documentation
   - Has thorough test coverage

2. A results list component (src/panoptikon/ui/components/results_list.py) that:
   - Implements NSTableView wrapper
   - Supports virtual scrolling for large results
   - Provides column sorting
   - Implements row selection
   - Uses data source pattern correctly
   - Handles custom cell formatters
   - Documents memory management
   - Includes comprehensive documentation
   - Has thorough test coverage

3. A search view model (src/panoptikon/ui/viewmodels/search_vm.py) that:
   - Manages search state
   - Handles query execution
   - Controls results pagination
   - Implements filtering logic
   - Provides sort order management
   - Separates UI from search logic
   - Includes comprehensive documentation
   - Has complete test coverage

4. A search controller (src/panoptikon/ui/controllers/search_controller.py) that:
   - Coordinates search components
   - Manages user interactions
   - Implements keyboard shortcuts
   - Handles selection changes
   - Uses clean controller pattern
   - Separates concerns appropriately
   - Includes comprehensive documentation
   - Has thorough test coverage

5. Comprehensive tests:
   - tests/test_ui/test_components/test_search_field.py
   - tests/test_ui/test_components/test_results_list.py
   - tests/test_ui/test_viewmodels/test_search_vm.py
   - tests/test_ui/test_controllers/test_search_controller.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The search interface must provide a responsive experience with results appearing within 200ms of user input. Memory management for PyObjC interactions should be clearly documented with proper resource cleanup.
```

### Prompt 13: File Operations UI

```
I need to implement the file operations UI components for Panoptikon using PyObjC, focusing on providing clean file management capabilities. Please create:

1. A file operations manager (src/panoptikon/ui/operations.py) that:
   - Handles opening files with default applications
   - Implements "reveal in Finder" functionality
   - Manages file operations permissions
   - Handles multiple file selections
   - Uses native file APIs
   - Provides progress feedback
   - Includes comprehensive documentation
   - Has thorough test coverage

2. A context menu component (src/panoptikon/ui/components/context_menu.py) that:
   - Implements NSMenu wrapper for context menus
   - Provides dynamic menu generation
   - Handles menu item validation
   - Supports keyboard shortcuts
   - Uses delegate pattern correctly
   - Documents memory management
   - Includes comprehensive documentation
   - Has thorough test coverage

3. A drag and drop handler (src/panoptikon/ui/components/drag_drop.py) that:
   - Implements NSTableView drag source
   - Handles file drag operations
   - Manages pasteboard interactions
   - Provides proper feedback during drag
   - Uses delegate pattern correctly
   - Documents memory management
   - Includes comprehensive documentation
   - Has thorough test coverage

4. A file preview component (src/panoptikon/ui/components/preview.py) that:
   - Implements Quick Look integration
   - Provides file previews
   - Handles different file types
   - Uses AppKit APIs properly
   - Documents memory management
   - Follows Apple guidelines
   - Includes comprehensive documentation
   - Has thorough test coverage

5. Comprehensive tests:
   - tests/test_ui/test_operations.py
   - tests/test_ui/test_components/test_context_menu.py
   - tests/test_ui/test_components/test_drag_drop.py
   - tests/test_ui/test_components/test_preview.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The file operations UI should provide a native macOS experience that integrates smoothly with the Finder and other applications. Security considerations for file operations should be clearly documented.
```

### Prompt 14: Menu Bar and Preferences UI

```
I need to implement the menu bar integration and preferences UI for Panoptikon using PyObjC, focusing on following macOS design guidelines. Please create:

1. A menu bar component (src/panoptikon/ui/menubar.py) that:
   - Implements NSStatusItem for menu bar presence
   - Provides quick search access
   - Handles activation/deactivation
   - Manages menu items dynamically
   - Uses delegate pattern correctly
   - Documents memory management
   - Follows macOS guidelines
   - Includes comprehensive documentation
   - Has thorough test coverage

2. A preferences window (src/panoptikon/ui/preferences.py) that:
   - Creates a standard preferences window
   - Implements tabbed interface for categories
   - Provides settings binding
   - Handles user input validation
   - Persists settings correctly
   - Uses AppKit properly
   - Documents memory management
   - Includes comprehensive documentation
   - Has thorough test coverage

3. Preference panels:
   - src/panoptikon/ui/preferences/general.py
   - src/panoptikon/ui/preferences/indexing.py
   - src/panoptikon/ui/preferences/search.py
   - src/panoptikon/ui/preferences/cloud.py

   Each panel should:
   - Implement a consistent interface
   - Handle settings validation
   - Provide immediate feedback
   - Use AppKit controls properly
   - Document memory management
   - Include comprehensive documentation
   - Have thorough test coverage

4. A settings manager (src/panoptikon/config/settings.py) that:
   - Manages application settings
   - Persists changes to database
   - Provides change notifications
   - Implements defaults mechanism
   - Validates setting values
   - Handles migration of settings
   - Includes comprehensive documentation
   - Has thorough test coverage

5. Comprehensive tests:
   - tests/test_ui/test_menubar.py
   - tests/test_ui/test_preferences.py
   - tests/test_ui/test_preferences/ (for panels)
   - tests/test_config/test_settings.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The implementation should follow macOS design guidelines, providing a native experience consistent with other applications. Settings should be persisted safely with proper error handling.
```

## Phase 5: Performance Optimization (Weeks 13-14)

### Prompt 15: Search Optimization

```
I need to implement search performance optimizations for Panoptikon to ensure it meets the 200ms response time requirement. Please create:

1. A search optimizer (src/panoptikon/search/optimizer.py) that:
   - Analyzes query patterns
   - Implements query planning
   - Generates optimized SQL
   - Uses appropriate indexes
   - Caches frequent searches
   - Provides performance metrics
   - Includes comprehensive documentation
   - Has thorough performance tests

2. An index optimizer (src/panoptikon/db/index_optimizer.py) that:
   - Analyzes database usage patterns
   - Recommends index improvements
   - Implements automatic index creation
   - Measures query performance
   - Uses SQLite optimization features
   - Manages index lifecycle
   - Includes comprehensive documentation
   - Has thorough test coverage

3. A result cache (src/panoptikon/search/cache.py) that:
   - Implements LRU caching for results
   - Handles cache invalidation
   - Optimizes memory usage
   - Provides hit/miss metrics
   - Uses efficient serialization
   - Manages cache size constraints
   - Includes comprehensive documentation
   - Has thorough test coverage

4. Query profiling tools (src/panoptikon/search/profiler.py) that:
   - Measure query performance
   - Identify bottlenecks
   - Provide optimization suggestions
   - Log performance metrics
   - Use minimal overhead
   - Follow clean instrumentation pattern
   - Include comprehensive documentation
   - Have thorough test coverage

5. Comprehensive performance tests:
   - tests/test_search/test_optimizer.py
   - tests/test_db/test_index_optimizer.py
   - tests/test_search/test_cache.py
   - tests/test_search/test_profiler.py
   - benchmarks/search_performance.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The optimizations should achieve the 200ms response time goal without compromising result quality. Include clear documentation of performance characteristics and tradeoffs.
```

### Prompt 16: Indexing Performance

```
I need to implement indexing performance optimizations for Panoptikon to meet the 1000+ files per second indexing requirement. Please create:

1. An indexing optimizer (src/panoptikon/index/optimizer.py) that:
   - Implements batch operations
   - Uses prepared statements effectively
   - Optimizes transaction boundaries
   - Manages memory usage
   - Provides performance metrics
   - Uses thread pools efficiently
   - Includes comprehensive documentation
   - Has thorough performance tests

2. A throttling system (src/panoptikon/index/throttle.py) that:
   - Controls indexing speed
   - Adjusts based on system load
   - Respects battery status
   - Implements priority queuing
   - Provides feedback mechanisms
   - Uses adaptive algorithms
   - Includes comprehensive documentation
   - Has thorough test coverage

3. Memory optimizations (src/panoptikon/utils/memory.py) that:
   - Reduce memory footprint
   - Implement efficient data structures
   - Use object pooling where appropriate
   - Control garbage collection
   - Provide memory usage metrics
   - Follow clean design patterns
   - Include comprehensive documentation
   - Have thorough test coverage

4. I/O optimizations (src/panoptikon/utils/io.py) that:
   - Implement efficient file reading
   - Batch file operations
   - Use appropriate buffer sizes
   - Minimize system calls
   - Provide I/O metrics
   - Follow clean design patterns
   - Include comprehensive documentation
   - Have thorough test coverage

5. Comprehensive performance tests:
   - tests/test_index/test_optimizer.py
   - tests/test_index/test_throttle.py
   - tests/test_utils/test_memory.py
   - tests/test_utils/test_io.py
   - benchmarks/indexing_performance.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The optimizations should achieve the 1000+ files per second goal while maintaining system responsiveness and minimizing resource usage. Include clear documentation of performance characteristics and tradeoffs.
```

## Phase 6: Packaging & Distribution (Weeks 15-16)

### Prompt 17: Application Packaging

```
I need to implement the packaging system for Panoptikon to create a distributable macOS application. Please create:

1. An application bundling script (scripts/bundle_app.py) that:
   - Creates a proper macOS .app bundle
   - Packages all required resources
   - Manages Python dependencies
   - Handles PyObjC integration
   - Optimizes bundle size
   - Sets proper permissions
   - Includes comprehensive documentation
   - Has thorough testing

2. A code signing script (scripts/sign_app.py) that:
   - Implements proper code signing
   - Handles entitlements configuration
   - Supports notarization workflow
   - Verifies signature integrity
   - Manages developer certificates
   - Follows Apple guidelines
   - Includes comprehensive documentation
   - Has thorough testing

3. A DMG creation script (scripts/create_dmg.py) that:
   - Builds a standard macOS disk image
   - Includes application and shortcuts
   - Configures background image
   - Sets up proper appearance
   - Optimizes compression
   - Follows Apple guidelines
   - Includes comprehensive documentation
   - Has thorough testing

4. An update mechanism (src/panoptikon/utils/updater.py) that:
   - Checks for updates securely
   - Downloads updates efficiently
   - Verifies package signatures
   - Handles installation process
   - Provides progress feedback
   - Manages error recovery
   - Includes comprehensive documentation
   - Has thorough test coverage

5. Comprehensive tests and verification:
   - tests/test_packaging/test_bundling.py
   - tests/test_packaging/test_signing.py
   - tests/test_packaging/test_dmg.py
   - tests/test_utils/test_updater.py

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The packaging system should create a professional-quality macOS application that meets App Store requirements. Security considerations should be a priority, particularly for code signing and the update mechanism.
```

### Prompt 18: Documentation and Final Polish

```
I need to implement comprehensive documentation and final polish for the Panoptikon application. Please create:

1. User documentation (docs/user/):
   - Getting started guide
   - Search syntax reference
   - Cloud integration guide
   - Preferences documentation
   - Troubleshooting guide
   - Keyboard shortcuts reference
   - Each with clear, concise explanations
   - Including screenshots and examples

2. Technical documentation (docs/technical/):
   - Architecture overview
   - Component descriptions
   - API reference
   - Performance characteristics
   - Database schema
   - Extension points
   - Each with appropriate diagrams
   - Including code examples

3. A release checklist (RELEASE_CHECKLIST.md) that:
   - Lists all verification steps
   - Includes performance benchmarks
   - Covers security considerations
   - Addresses accessibility requirements
   - Details distribution steps
   - Documents rollback procedures
   - Includes manual testing scenarios
   - Has clear pass/fail criteria

4. Final polish tasks:
   - src/panoptikon/ui/polish.py for UI refinements
   - src/panoptikon/utils/startup.py for optimized launch
   - src/panoptikon/utils/diagnostics.py for self-diagnostics
   - Each with comprehensive documentation
   - Complete with thorough testing

5. Quality verification scripts:
   - scripts/verify_quality.py
   - scripts/performance_test.py
   - scripts/accessibility_check.py
   - Each with comprehensive documentation
   - Complete with thorough testing

All components must meet our quality standards: complete docstrings, proper type hints, manageable file/function sizes, and thorough test coverage. The documentation should be clear, concise, and comprehensive, suitable for both end users and developers. Final polish should focus on creating a professional, polished application experience.
```
