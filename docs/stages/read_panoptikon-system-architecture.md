# Panoptikon System Architecture - Pragmatic Approach

## 1. System Overview

Panoptikon is a high-performance macOS file search utility designed to provide instant filename search across all storage locations with zero configuration. The system focuses exclusively on ultra-fast filename search in its initial stage, with a clean architecture that balances immediate development needs with strategic resilience against the most critical aspects of macOS evolution.

### 1.1 Core Value Proposition

Panoptikon's core promise is simple: "It knows where everything is with no blindspots." The application delivers:
- Ultra-fast filename search (sub-50ms response time)
- Complete visibility across local, network, and cloud storage
- Zero configuration for cloud services
- Dual-paradigm interface supporting both keyboard and mouse workflows
- Minimal resource footprint

### 1.2 Target Performance Metrics

- **Launch time**: Under 100ms from hotkey to focused search field
- **Search latency**: Under 50ms from keystroke to displayed results
- **UI responsiveness**: 60fps animation and rendering (16ms per frame)
- **Indexing speed**: 250,000 files in under 60 seconds
- **Memory footprint**: Below 50MB when idle
- **CPU usage**: Negligible when idle
- **Installed size**: Application bundle under 30MB

### 1.3 OS Evolution Protection Strategy

Rather than attempting to bulletproof every aspect of the system, this architecture focuses on protecting the most volatile and critical OS touchpoints:

- **Targeted Abstraction**: Create strong abstraction only for historically volatile OS interfaces
- **Focused Capability Detection**: Implement feature detection for essential capabilities with known variation
- **Strategic Adaptation**: Provide adaptation mechanisms for high-risk subsystems
- **Standard Approaches**: Use conventional design for stable components

## 2. System Architecture

### 2.1 Component Structure

```
┌─ UI Layer ──────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Search Field│  │   Tab Bar   │  │Results Table│  │Context Menus│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │Progress Bar │  │  Tooltips   │  │ Status Bar  │  │Pref. Panel  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                              │                                        │
│  ┌─────────────┐  ┌─────────┴───────┐  ┌─────────────┐              │
│  │Search Engine│  │Input Controller │  │Results Model│              │
│  └──────┬──────┘  └─────────────────┘  └──────┬──────┘              │
│         │                                      │                     │
│  ┌──────┴──────┐  ┌─────────────────┐  ┌──────┴──────┐              │
│  │Query Parser │  │Service Container│  │Result Sorter│              │
│  └─────────────┘  └────────┬────────┘  └─────────────┘              │
│                            │                                         │
│  ┌─────────────┐  ┌────────┴────────┐  ┌─────────────┐              │
│  │Path Resolver│  │    Event Bus    │  │Cloud Manager│              │
│  └─────────────┘  └─────────────────┘  └─────────────┘              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                              │                                        │
│  ┌─────────────┐  ┌─────────┴───────┐  ┌─────────────┐              │
│  │  Indexer    │  │ Database Access │  │File Monitor │              │
│  └──────┬──────┘  └─────────────────┘  └──────┬──────┘              │
│         │                                      │                     │
│  ┌──────┴──────┐  ┌─────────────────┐  ┌──────┴──────┐              │
│  │Metadata Extr│  │   SQLite DB     │  │FSEvents Wrap│              │
│  └─────────────┘  └────────┬────────┘  └─────────────┘              │
│                            │                                         │
│  ┌─────────────┐  ┌────────┴────────┐  ┌─────────────┐              │
│  │Radix Cache  │  │Connection Pool  │  │FS Operations│              │
│  └─────────────┘  └─────────────────┘  └─────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

In this pragmatic architecture, we adopt a standard layered approach but include **key abstraction points** for the most volatile OS interfaces:

1. **FSEvents Wrapper**: Isolated to handle file system monitoring changes
2. **FS Operations**: Abstracted to manage permissions and cloud storage evolution
3. **UI Components**: Carefully designed to accommodate UI framework changes

### 2.2 Core Components

#### 2.2.1 UI Layer

- **Search Field**: NSSearchField for user input with as-you-type filtering
- **Tab Bar**: NSSegmentedControl for category filtering
- **Results Table**: NSTableView with virtual rendering for performance
- **Context Menus**: Right-click operations for Windows-familiar workflow
- **Progress Overlay**: Non-intrusive indexing status visualization
- **Preference Panel**: Configuration interface for path rules and settings

#### 2.2.2 Core Services Layer

- **Search Engine**: Query parsing and execution with wildcard support
- **Input Controller**: Transforms user input into queries and commands
- **Results Model**: Data structure for filtered and sorted results
- **Query Parser**: Interprets search patterns and optimizes execution
- **Service Container**: Dependency injection system for components
- **Result Sorter**: Optimized ordering of result sets
- **Path Resolver**: Rule evaluation for inclusion/exclusion logic
- **Event Bus**: Decoupled messaging between components
- **Cloud Manager**: Provider detection and delegation

#### 2.2.3 Data Layer

- **Indexer**: Background process for building file database
- **Database Access**: Interface for storage operations
- **File Monitor**: Detects file system changes with adaptation capabilities
- **Metadata Extractor**: Pulls essential file attributes
- **SQLite Database**: Primary storage for file metadata
- **FSEvents Wrapper**: Isolated integration with file notifications
- **Radix Cache**: In-memory structure for rapid path matching
- **Connection Pool**: Thread-safe database access
- **FS Operations**: File system interaction with permission awareness

### 2.3 Data Flow Architecture

#### 2.3.1 Primary Search Flow

1. User enters search text in Search Field
2. Input Controller transforms input to search query
3. Search Engine executes query against Database and Radix Cache
4. Results Model collects and organizes matching files
5. Results Table displays virtual view of results
6. UI updates in under 50ms for instantaneous feel

#### 2.3.2 Indexing Flow

1. File Monitor receives file system notifications through FSEvents Wrapper
2. Path Resolver evaluates path against inclusion/exclusion rules
3. Indexer extracts metadata from qualifying files
4. Database Access stores information in SQLite
5. Progress Overlay provides non-intrusive status updates
6. Radix Cache updates in-memory representation

#### 2.3.3 File Operation Flow with Provider Awareness

1. User selects file(s) in Results Table
2. Context Menu or keyboard shortcut initiates operation
3. Cloud Manager determines file location type
4. FS Operations delegates to system handlers:
   - For cloud files: Uses NSWorkspace.shared.open() or equivalent
   - For local files: Direct file system operations
   - Never directly handles cloud sync/download - always delegates to Finder
5. UI provides feedback on operation outcome

## 3. Data Architecture

### 3.1 Database Schema

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,               -- Filename without path
    name_lower TEXT NOT NULL,         -- Lowercase for case-insensitive search
    extension TEXT,                   -- File extension (lowercase)
    path TEXT NOT NULL,               -- Full path
    parent_path TEXT NOT NULL,        -- Parent directory path
    size INTEGER,                     -- File size (NULL for cloud-only)
    date_created INTEGER,             -- Creation timestamp
    date_modified INTEGER,            -- Modification timestamp 
    file_type TEXT,                   -- UTType identifier
    is_directory INTEGER NOT NULL,    -- 1 if directory, 0 if file
    cloud_provider TEXT,              -- NULL, 'iCloud', 'Dropbox', etc.
    cloud_status INTEGER,             -- 0=local, 1=downloaded, 2=cloud-only
    indexed_at INTEGER NOT NULL       -- Timestamp of last indexing
);

CREATE TABLE directories (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,        -- Directory path
    included INTEGER NOT NULL,        -- 1 if included, 0 if excluded
    priority INTEGER NOT NULL,        -- Higher number takes precedence
    recursive INTEGER NOT NULL,       -- 1 if rule applies to subdirectories
    permission_state INTEGER NOT NULL -- Current permission status
);

CREATE TABLE file_types (
    id INTEGER PRIMARY KEY,
    extension TEXT NOT NULL UNIQUE,   -- Lowercase extension without dot
    type_name TEXT NOT NULL,          -- User-friendly type name
    category TEXT NOT NULL            -- Category for tab grouping
);

CREATE TABLE tabs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,               -- Display name
    filter_def TEXT NOT NULL,         -- JSON filter definition
    position INTEGER NOT NULL,        -- Order in tab bar
    visible INTEGER NOT NULL          -- 1 if visible, 0 if hidden
);

CREATE TABLE indexing_log (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,       -- Operation timestamp
    operation TEXT NOT NULL,          -- 'initial', 'incremental', etc.
    path TEXT,                        -- Related path if applicable
    file_count INTEGER,               -- Number of files processed
    duration INTEGER                  -- Operation duration in milliseconds
);

CREATE TABLE schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Single row table
    version TEXT NOT NULL,                  -- Semantic version (Major.Minor.Patch)
    updated_at INTEGER NOT NULL             -- Last update timestamp
);

CREATE TABLE permission_bookmarks (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,        -- Path this bookmark grants access to
    bookmark BLOB NOT NULL,           -- Security-scoped bookmark data
    created_at INTEGER NOT NULL       -- Creation timestamp
);
```

### 3.2 Key Optimization Strategies

1. **Indexing for Common Queries**:
```sql
CREATE INDEX idx_files_name ON files(name_lower);         -- Fast name search
CREATE INDEX idx_files_ext ON files(extension);           -- Extension filtering
CREATE INDEX idx_files_path ON files(path);               -- Path lookup
CREATE INDEX idx_files_parent ON files(parent_path);      -- Parent directory queries
CREATE INDEX idx_files_type ON files(file_type);          -- File type filtering
CREATE INDEX idx_files_cloud ON files(cloud_provider, cloud_status); -- Cloud status
```

2. **In-Memory Caching**:
   - Radix tree for fast path prefix matching
   - LRU cache for frequent queries
   - Metadata cache for active directories

3. **Query Optimization**:
   - Prepared statements for all common operations
   - Transaction batching for bulk operations
   - Write-ahead logging for crash resilience

### 3.3 Data Lifecycle Management

1. **Database Versioning**:
   - Schema version tracked in dedicated table
   - Simple forward migrations applied automatically
   - Backup before schema changes

2. **Integrity Protection**:
   - Journaling with synchronous mode
   - Periodic integrity checks with auto-repair
   - Automatic backup on corruption detection

3. **Cleanup Processes**:
   - Periodic pruning of deleted file references
   - Database vacuuming during idle periods
   - Cache invalidation on index updates

## 4. Critical OS Touchpoint Protection

### 4.1 FSEvents Monitoring Resilience

**Risk**: macOS has historically changed file system monitoring APIs and behavior

**Protection Strategy**:
1. **FSEvents Wrapper**:
   - Isolate all FSEvents interactions within a dedicated component
   - Implement a polling-based fallback mechanism when FSEvents fails
   - Add shadow verification to detect missed events on network storage

2. **Change Detection Interface**:
   - Create a stable file change notification interface
   - Support graceful degradation to less efficient mechanisms
   - Implement adaptive event coalescing based on system load

3. **Path Monitoring Strategies**:
   - Support both recursive and path-specific monitoring
   - Handle network path monitoring limitations
   - Provide event validation and recovery mechanisms

### 4.2 Permission and Security Model Adaptation

**Risk**: macOS security model has become increasingly restrictive

**Protection Strategy**:
1. **Permission Management**:
   - Implement security-scoped bookmark handling for persistent access
   - Create progressive permission acquisition with minimum required access
   - Add permission state visualization for user awareness

2. **Access Levels**:
   - Design for minimal permissions (standard user directories)
   - Support enhanced capabilities with Security-Scoped Bookmarks
   - Gracefully utilize Full Disk Access when available
   - Properly handle cloud storage permission delegation

3. **Operation Delegation**:
   - Implement file operation strategies based on available permissions
   - Provide clear user guidance for permission requirements
   - Maintain functionality with limited permissions

### 4.3 Cloud Storage Provider Integration

**Risk**: Cloud providers frequently change APIs and integration methods

**Protection Strategy**:
1. **Provider Detection**:
   - Use path patterns and attributes for provider identification
   - Implement behavior-based detection over provider-specific code
   - Support common providers (iCloud, Dropbox, Google Drive, OneDrive, Box)

2. **Operation Handling**:
   - Create provider-agnostic file operation interfaces
   - **CRITICAL**: All cloud file operations (open, reveal, download) must be delegated to the system/Finder using NSWorkspace or equivalent
   - Never implement direct cloud provider APIs or handle sync/download internally
   - Support offline handling by delegating to Finder which manages sync status

3. **Status Visualization**:
   - Implement consistent cloud file indicators
   - Support cloud-only placeholder visualization
   - Provide download progress for cloud files

### 4.4 UI Framework Integration

**Risk**: AppKit evolves with each macOS version

**Protection Strategy**:
1. **Component Composition**:
   - Use composition over inheritance for UI components
   - Create clear separation between presentation and business logic
   - Implement focused UI adapters for volatile components

2. **Event Handling**:
   - Use standard AppKit patterns for event processing
   - Implement consistent keyboard and mouse handling
   - Support accessibility through standard protocols

3. **Layout Management**:
   - Use Auto Layout for flexible positioning
   - Support dynamic type and different display densities
   - Maintain consistent visual appearance across OS versions

## 5. Concurrency Architecture

### 5.1 Thread Model with GIL Mitigation

1. **Thread Domains**:
   - UI Domain: Main thread only
   - Indexing Domain: Background thread pool
   - Search Domain: Dedicated optimized thread
   - I/O Domain: Asynchronous operation queue
   - Monitoring Domain: Event processing queue

2. **GIL Contention Management**:
   - Clear thread confinement with ownership boundaries
   - Batch operations to minimize transitions
   - Strategic use of PyObjC autorelease pools

3. **Resource Adaptation**:
   - Dynamic thread pool sizing based on system capabilities
   - Thread priority management for responsive UI
   - Throttling during resource constraints

### 5.2 Task Prioritization

1. **Priority Levels**:
   - Critical: UI responsiveness, search operations
   - High: File operations, visibility updates
   - Normal: Incremental indexing, metadata extraction
   - Background: Full indexing, database optimization
   - Idle: Analytics, cleanup operations

2. **Scheduling System**:
   - Preemptive scheduling for high-priority tasks
   - Work stealing for balanced distribution
   - Energy-aware scheduling on battery power

### 5.3 Memory Management

1. **Ownership Model**:
   - Explicit object ownership across thread boundaries
   - Memory pressure monitoring and adaptation
   - Caching with size limits

2. **PyObjC Memory Management**:
   - Explicit autorelease pool management
   - Controlled crossing of language boundaries
   - Careful management of Objective-C object references

## 6. Interface Architecture

### 6.1 Service Interface Contract

All internal services follow a standard interface pattern:

```python
class ServiceInterface:
    """Base interface that all services must implement."""
    
    def initialize(self):
        """Initialize the service."""
        raise NotImplementedError
        
    def shutdown(self):
        """Gracefully shut down the service."""
        raise NotImplementedError
        
    def get_status(self):
        """Return the current service status."""
        raise NotImplementedError
```

Specific service interfaces extend this base with their specialized methods.

### 6.2 Event Bus Design

The event bus provides a decoupled communication system:

1. **Event Types**:
   - `FileSystemEvent`: File creation, modification, deletion
   - `IndexingEvent`: Indexing start, progress, completion
   - `SearchEvent`: Query execution, results available
   - `UIEvent`: User interaction tracking
   - `SystemEvent`: Application lifecycle events

2. **Subscription Model**:
```python
def subscribe(event_type, callback):
    """Subscribe to an event type."""
    pass
    
def unsubscribe(event_type, callback):
    """Unsubscribe from an event type."""
    pass
    
def publish(event_type, event_data):
    """Publish an event to all subscribers."""
    pass
```

3. **Event Format**:
```python
{
    "type": "EventType",
    "timestamp": 1620000000,
    "data": {
        # Event-specific data
    },
    "source": "ComponentName"
}
```

### 6.3 Error Handling Strategy

1. **Error Categories**:
   - User Input Errors: Invalid queries, unsupported operations
   - System Errors: File access issues, database problems
   - Resource Errors: Memory exhaustion, disk space
   - External Errors: Cloud service failures, network issues

2. **Recovery Strategies**:
   - Automatic retry for transient failures
   - Graceful degradation for unavailable services
   - User notification for blocking issues
   - Automatic repair for corrupted state

3. **Error Format**:
```python
{
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "severity": "INFO|WARNING|ERROR|CRITICAL",
    "component": "ComponentName",
    "timestamp": 1620000000,
    "recoverable": True,
    "details": {
        # Error-specific details
    }
}
```

## 7. Extension Architecture

### 7.1 Content Search Extension Point

While Stage 1 focuses exclusively on filename search, the architecture includes extension points for future content search capabilities:

1. **Database Schema Extension**:
```sql
CREATE TABLE content_index (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,         -- Reference to files table
    content_type TEXT NOT NULL,       -- 'text', 'pdf', 'doc', etc.
    content TEXT NOT NULL,            -- Extracted text content
    language TEXT,                    -- Detected language
    indexed_at INTEGER NOT NULL,      -- Timestamp of indexing
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE content_fts USING fts5(
    content,
    content='content_index',
    content_rowid='id'
);
```

2. **Extractor Interface**:
```python
class ContentExtractorInterface(ServiceInterface):
    """Interface for content extraction implementations."""
    
    def supports_file_type(self, file_type):
        """Check if this extractor supports the given file type."""
        raise NotImplementedError
        
    def extract_content(self, file_path, file_type):
        """Extract content from the file and return structured data."""
        raise NotImplementedError
        
    def get_supported_types(self):
        """Return list of supported file types."""
        raise NotImplementedError
```

### 7.2 OCR Extension Point

OCR capabilities will be added in a future stage:

1. **OCR Service Interface**:
```python
class OCRServiceInterface(ServiceInterface):
    """Interface for OCR service implementations."""
    
    def scan_image(self, image_path, languages=None, options=None):
        """Perform OCR on the given image and return extracted text."""
        raise NotImplementedError
        
    def scan_pdf(self, pdf_path, page_range=None, languages=None, options=None):
        """Perform OCR on the given PDF and return extracted text by page."""
        raise NotImplementedError
        
    def get_supported_formats(self):
        """Return list of supported image formats."""
        raise NotImplementedError
```

2. **OCR Database Schema**:
```sql
CREATE TABLE ocr_results (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,             -- Reference to files table
    page_number INTEGER,                  -- NULL for images, page for PDFs
    text TEXT NOT NULL,                   -- Extracted text
    confidence REAL,                      -- OCR confidence score (0-1)
    language TEXT,                        -- Detected language
    coordinates TEXT,                     -- JSON text region coordinates
    processed_at INTEGER NOT NULL,        -- Timestamp of processing
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE ocr_fts USING fts5(
    text,
    content='ocr_results',
    content_rowid='id'
);
```

## 8. Security Architecture

### 8.1 Permission Model

1. **Access Levels**:
   - Standard Access: User directory access
   - Extended Access: User-selected folders via security-scoped bookmarks
   - Full Access: Complete visibility through Full Disk Access

2. **Permission Persistence**:
   - Security-scoped bookmarks for persistent access
   - Permission state tracking in directory table
   - Clear visualization of accessible areas

3. **Degradation Strategy**:
   - Function with minimal permissions
   - Clearly communicate limitation boundaries
   - Provide guidance for permission acquisition

### 8.2 Data Security

1. **Local-Only Storage**:
   - No data transmission off-device
   - Integration with FileVault for encryption
   - Secure deletion of temporary files

2. **Privacy Protection**:
   - No telemetry or usage tracking
   - No unique identifiers generated
   - No cloud synchronization of index

3. **Update Security**:
   - Signed and notarized application
   - Sparkle with ed25519 signatures
   - Update verification before installation

## 9. Observability Architecture

### 9.1 Logging Framework

1. **Log Levels**:
   - DEBUG: Detailed developer information
   - INFO: General operational information
   - WARNING: Potential issues that don't block functionality
   - ERROR: Operation failures that impact functionality
   - CRITICAL: System-level failures requiring immediate attention

2. **Log Structure**:
```python
{
    "timestamp": "ISO8601 timestamp",
    "level": "LOG_LEVEL",
    "component": "ComponentName",
    "message": "Human-readable message",
    "context": {
        # Operation-specific context
    }
}
```

3. **Log Storage**:
   - Rolling file logs with size limits
   - Console output in debug mode
   - System log integration for critical errors

### 9.2 Performance Metrics

1. **Core Metrics**:
   - Query Execution Time: Time from query start to results
   - UI Render Time: Frame time for UI updates
   - Indexing Rate: Files processed per second
   - Memory Usage: By component and operation
   - Thread Utilization: Activity across thread pools

2. **Collection Approach**:
   - Instrumentation of critical paths
   - Sampling for high-volume operations
   - Aggregation for trend analysis

3. **Threshold Alerting**:
   - Warning thresholds for core metrics
   - Automatic diagnostics for threshold violations
   - User notification for severe performance issues

## 10. Quality & Testing Architecture

### 10.1 Test Categories

1. **Unit Tests**:
   - Component isolation with mocks
   - Comprehensive coverage (≥95%)
   - Performance validation

2. **Integration Tests**:
   - Component interaction validation
   - Real file system testing
   - Cloud provider simulation

3. **Performance Tests**:
   - Search latency benchmarks
   - Indexing speed measurements
   - Memory consumption tracking
   - CPU utilization profiling

4. **Accessibility Tests**:
   - VoiceOver compatibility
   - Keyboard navigation verification
   - Color contrast compliance
   - Dynamic type support

### 10.2 Quality Gates

1. **Code Quality**:
   - Static analysis with mypy and flake8
   - Cyclomatic complexity limits (max 10)
   - Line length restrictions (max 500 lines per file)
   - Documentation requirements

2. **Performance Gates**:
   - Search latency ≤ 50ms
   - Launch time ≤ 100ms
   - UI rendering ≥ 60fps
   - Memory usage within budgets

3. **Test Coverage**:
   - Unit test coverage ≥ 95%
   - Critical path coverage 100%
   - Edge case validation

## 11. Critical Design Decisions

### 11.1 Technology Stack Selection

1. **Primary Language**: Python 3.11+
   - **Rationale**: Balance of development speed and performance
   - **Alternatives Considered**: Swift (steeper learning curve), Rust (longer development time)
   - **Risks**: Global Interpreter Lock, memory management
   - **Mitigation**: Thread confinement, explicit memory management, critical path optimization
   - **Build Strategy**: 
     * Prototype in PyObjC + Python 3.11+ with minimal dependencies
     * Bundle with py2app using excludes for unused modules
     * Final compilation with Nuitka for self-contained binary
     * Optional UPX compression of .so/.dylib files

2. **UI Framework**: Native AppKit via PyObjC
   - **Rationale**: Native look and feel, optimal performance
   - **Alternatives Considered**: Qt (non-native appearance), Tkinter (limited capabilities)
   - **Risks**: PyObjC memory leaks, API complexity
   - **Mitigation**: Explicit ownership patterns, composition over inheritance

3. **Database**: SQLite
   - **Rationale**: Embedded, zero configuration, proven performance
   - **Alternatives Considered**: Core Data (tighter coupling), LMDB (less Python support)
   - **Risks**: Concurrent access limitations, potential corruption
   - **Mitigation**: Connection pooling, WAL mode, integrity checks

### 11.2 Architectural Style Decisions

1. **Component-Based Architecture**:
   - **Rationale**: Clear responsibility boundaries, modularity
   - **Alternatives Considered**: Layered architecture (less flexible), microkernel (too complex)
   - **Risks**: Interface proliferation, potential overhead
   - **Mitigation**: Strategic interface consolidation, component registries

2. **Event-Driven Communication**:
   - **Rationale**: Decoupling components, async operations
   - **Alternatives Considered**: Direct method calls (tighter coupling), callbacks (callback hell)
   - **Risks**: Event tracking complexity, potential missed events
   - **Mitigation**: Event logging, delivery guarantees, error handling

3. **Service Container Pattern**:
   - **Rationale**: Dependency injection, testability
   - **Alternatives Considered**: Singletons (testing difficulty), global state (maintenance issues)
   - **Risks**: Configuration complexity, startup overhead
   - **Mitigation**: Lazy initialization, service hierarchies

### 11.3 Performance Strategy Decisions

1. **Radix Tree for Path Matching**:
   - **Rationale**: Optimal prefix matching performance
   - **Alternatives Considered**: Trie (more memory), B-tree (slower for prefixes)
   - **Risks**: Implementation complexity, memory usage
   - **Mitigation**: Custom implementation with memory optimization

2. **Thread Confinement for GIL Management**:
   - **Rationale**: Predictable performance, avoid contention
   - **Alternatives Considered**: Process pools (IPC overhead), async (less control)
   - **Risks**: Thread coordination complexity, potential deadlocks
   - **Mitigation**: Clear ownership rules, timeout mechanisms

3. **Virtual UI Rendering**:
   - **Rationale**: Efficient handling of large result sets
   - **Alternatives Considered**: Full table rendering (poor performance), paging (worse UX)
   - **Risks**: Implementation complexity, edge case handling
   - **Mitigation**: Careful view recycling, background preparation

## 12. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Full Disk Access denial | High | High | Graceful degradation to Security-Scoped Bookmarks |
| PyObjC memory management issues | High | Medium | Strict ownership patterns, autorelease pool management |
| Database corruption | Medium | High | Transaction journaling, integrity checks, automated repair |
| FSEvents reliability on network shares | High | Medium | Multiple monitoring strategies, shadow-tree verification |
| Performance degradation at scale | Medium | High | Progressive loading, virtualization, sampling profiler |
| Cloud provider changes | Medium | Medium | Feature detection, fallback mechanisms |
| UI responsiveness during heavy indexing | High | Medium | Background threading, prioritization, throttling |
| GIL contention | High | Medium | Thread confinement, operation batching |
| Accessibility compliance | Medium | Medium | Regular testing, keyboard-first development |
| Path rule complexity | Medium | Medium | Rule compiler, optimization, precomputed matches |

## 13. Conclusion

This architecture provides a pragmatic foundation for the development of Panoptikon, focusing on protecting the most volatile OS touchpoints while avoiding unnecessary abstraction in stable components. By strategically applying bulletproofing techniques to file system monitoring, permission handling, cloud integration, and UI framework interaction, the system achieves an effective balance between immediate development efficiency and long-term maintainability.

The modular design ensures stability over a multi-year horizon while supporting rapid implementation of the Stage 1 MVP. The architecture balances the need for ultra-fast performance with the constraints of Python and PyObjC, implementing strategic optimizations for critical paths and resource management.
