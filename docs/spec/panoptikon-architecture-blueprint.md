# Panoptikon Architecture Blueprint

## 1. System Architecture

### 1.1 High-Level Architecture

Panoptikon follows a modular architecture with clear separation of concerns between components:

```
┌─────────────────────────────────────────────────────────────┐
│                       User Interface                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Search UI    │  │ Results UI   │  │ Preferences UI   │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Core Components                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Search       │  │ Indexing     │  │ Cloud            │   │
│  │ Engine       │◄─┤ System       │◄─┤ Integration      │   │
│  └─────┬────────┘  └─────┬────────┘  └────────┬─────────┘   │
│        │                 │                    │             │
│        │                 │                    │             │
│  ┌─────▼─────────────────▼────────────────────▼─────────┐   │
│  │                   Database                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                         File System                          │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Component Interfaces

The architecture strictly enforces separation between components through well-defined interfaces:

1. **UI to Core**: ViewModels expose interfaces to the UI layer
2. **Core to Database**: Repository pattern encapsulates database operations
3. **Indexing to File System**: File system access is isolated through interfaces
4. **Cloud to Providers**: Provider-specific code is hidden behind abstractions

### 1.3 Data Flow Architecture

```
                    ┌──────────────┐
              ┌────►│   UI Layer   │◄─────┐
              │     └──────────────┘      │
              │                           │
        Search│                      File │
        Request                  Operations
              │                           │
              │                           │
              │     ┌──────────────┐      │
              └────►│  Application │◄─────┘
                    │    Layer     │
                    └──────┬───────┘
                           │
                       Database
                     Operations
                           │
                           ▼
                    ┌──────────────┐
                    │   Database   │
                    │    Layer     │
                    └──────┬───────┘
                           │
                       Indexing
                      Operations
                           │
                           ▼
                    ┌──────────────┐
                    │ File System  │
                    └──────────────┘
```

## 2. Module Structure

### 2.1 Package Layout

```
panoptikon/
├── panoptikon/
│   ├── __init__.py
│   ├── index/           # File indexing system
│   │   ├── __init__.py
│   │   ├── crawler.py   # File system traversal
│   │   ├── monitor.py   # File system change detection
│   │   ├── metadata.py  # File metadata extraction
│   │   └── exclusion.py # Directory/file exclusion
│   ├── db/              # Database operations
│   │   ├── __init__.py
│   │   ├── schema.py    # Database schema
│   │   ├── operations.py # CRUD operations
│   │   ├── migrations.py # Schema migrations
│   │   └── connection.py # Connection management
│   ├── search/          # Search functionality
│   │   ├── __init__.py
│   │   ├── engine.py    # Search core
│   │   ├── parser.py    # Query parsing
│   │   ├── filters.py   # Filter implementation
│   │   ├── ranker.py    # Result ranking
│   │   ├── results.py   # Result management
│   │   └── history.py   # Search history tracking
│   ├── cloud/           # Cloud provider integration
│   │   ├── __init__.py
│   │   ├── detector.py  # Provider detection
│   │   ├── status.py    # Status tracking
│   │   ├── monitor.py   # Status change monitoring
│   │   ├── metadata.py  # Cloud-specific metadata
│   │   └── providers/   # Provider-specific implementations
│   │       ├── __init__.py
│   │       ├── icloud.py
│   │       ├── dropbox.py
│   │       ├── gdrive.py
│   │       ├── onedrive.py
│   │       └── box.py
│   ├── ui/              # PyObjC interface
│   │   ├── __init__.py
│   │   ├── app.py       # Application container
│   │   ├── window.py    # Main window controller
│   │   ├── menubar.py   # Menu bar integration
│   │   ├── operations.py # File operations
│   │   ├── components/  # UI components
│   │   │   ├── __init__.py
│   │   │   ├── search_field.py  # Search field
│   │   │   ├── results_list.py  # Results list
│   │   │   ├── context_menu.py  # Context menu
│   │   │   └── preview.py       # File preview
│   │   ├── viewmodels/  # View models (MVVM pattern)
│   │   │   ├── __init__.py
│   │   │   ├── search_vm.py    # Search view model
│   │   │   └── results_vm.py   # Results view model
│   │   ├── controllers/ # UI controllers
│   │   │   ├── __init__.py
│   │   │   └── search_controller.py # Search controller
│   │   └── preferences/ # Preference panels
│   │       ├── __init__.py
│   │       ├── general.py
│   │       ├── indexing.py
│   │       ├── search.py
│   │       └── cloud.py
│   ├── config/          # Application configuration
│   │   ├── __init__.py
│   │   └── settings.py  # Settings management
│   └── utils/           # Common utilities
│       ├── __init__.py
│       ├── paths.py     # Path operations
│       ├── logger.py    # Logging system
│       ├── threading.py # Threading utilities
│       ├── memory.py    # Memory optimizations
│       └── io.py        # I/O optimizations
├── tests/               # Test suite
│   ├── test_index/
│   ├── test_db/
│   ├── test_search/
│   ├── test_cloud/
│   ├── test_ui/
│   └── test_config/
├── scripts/             # Build and utility scripts
│   ├── bundle_app.py    # Application bundling
│   ├── sign_app.py      # Code signing
│   ├── create_dmg.py    # DMG creation
│   └── check_file_length.py # Quality checks
├── assets/              # Application resources
│   ├── icons/
│   └── images/
├── pyproject.toml       # Project configuration
├── README.md
└── .github/             # CI configuration
```

### 2.2 Component Dependencies

```
ui
 ├─► search
 ├─► cloud
 ├─► config
 └─► utils

search
 ├─► db
 └─► utils

cloud
 ├─► db
 └─► utils

index
 ├─► db
 └─► utils

db
 └─► utils

config
 ├─► db
 └─► utils
```

## 3. Database Architecture

### 3.1 Schema Design

```
┌────────────┐      ┌────────────┐
│  files     │      │ directories│
├────────────┤      ├────────────┤
│ id         │      │ id         │
│ name       │      │ path       │
│ path       │      │ included   │
│ size       │      │ recursive  │
│ created_at │      └────────────┘
│ modified_at│          │
│ extension  │          │
│ cloud_id   │◄─────────┘
└────────────┘
       ▲
       │
┌──────┴─────┐      ┌────────────┐
│cloud_files │      │   settings │
├────────────┤      ├────────────┤
│ id         │      │ key        │
│ file_id    │      │ value      │
│ provider   │      │ type       │
│ status     │      └────────────┘
│ sync_status│
└────────────┘
                    ┌────────────┐
                    │search_hist │
                    ├────────────┤
                    │ id         │
                    │ query      │
                    │ timestamp  │
                    │ saved      │
                    └────────────┘
```

### 3.2 Key Tables

1. **files**: Core file metadata including paths, names, and timestamps
2. **directories**: Included/excluded directories for indexing
3. **cloud_files**: Cloud-specific information for files
4. **settings**: Application configuration
5. **search_history**: Past searches and saved queries

### 3.3 Indexing Strategy

The database uses the following indexes to optimize search performance:

1. `idx_files_name`: Optimizes filename searches
2. `idx_files_path`: Optimizes path searches
3. `idx_files_extension`: Optimizes extension filtering
4. `idx_files_cloud_id`: Optimizes cloud status lookups
5. `idx_cloud_files_provider`: Optimizes provider filtering
6. `idx_cloud_files_status`: Optimizes download status filtering

## 4. UI Architecture

### 4.1 MVVM Pattern Implementation

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     View     │◄───►│  ViewModel   │◄───►│    Model     │
│ (PyObjC UI)  │     │ (Python)     │     │ (Core Data)  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  UI Controls │     │ Data Binding │     │  Repository  │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 4.2 PyObjC Integration Points

1. **NSApplication**: `ui/app.py` wraps the application lifecycle
2. **NSWindow**: `ui/window.py` manages window creation and interaction
3. **NSSearchField**: `ui/components/search_field.py` handles search input
4. **NSTableView**: `ui/components/results_list.py` displays search results
5. **NSMenu**: `ui/components/context_menu.py` provides context menus
6. **NSStatusItem**: `ui/menubar.py` implements menu bar integration

### 4.3 Memory Management

PyObjC memory management follows these principles:

1. All Objective-C objects are properly retained/released
2. Delegates are managed to prevent reference cycles
3. Python callbacks are properly bridged to Objective-C
4. Resource cleanup is explicit and documented

## 5. Search Engine Architecture

### 5.1 Query Processing Pipeline

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Input   │────►│  Parser  │────►│  Filters │────►│  Executor│
│  Query   │     │          │     │          │     │          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                        │
                      ┌──────────┐     ┌──────────┐     │
                      │  Result  │◄────┤  Ranker  │◄────┘
                      │  Display │     │          │
                      └──────────┘     └──────────┘
```

### 5.2 Query Language Grammar

```
query        ::= expression | expression boolean_op query
expression   ::= term | property_filter | group
term         ::= WORD | QUOTED_STRING | wildcard
property_filter ::= property_name ":" comparison
property_name ::= "name" | "path" | "ext" | "size" | "date" | "cloud" | "status"
comparison   ::= operator value | value
operator     ::= ">" | ">=" | "<" | "<=" | "=" | "!="
group        ::= "(" query ")"
boolean_op   ::= "AND" | "OR" | "NOT"
wildcard     ::= TEXT_WITH_WILDCARD
```

### 5.3 Filter Types

1. **TextFilter**: Matches text in filenames or paths
2. **PropertyFilter**: Matches specific file properties
3. **SizeFilter**: Matches file sizes with comparisons
4. **DateFilter**: Matches creation/modification dates
5. **CloudFilter**: Matches cloud provider or status

### 5.4 Ranking Algorithm

Result ranking considers:

1. Exact filename matches (highest weight)
2. Filename contains match
3. Path contains match
4. File recency (newer files ranked higher)
5. User interaction history (previously selected results ranked higher)

## 6. Indexing Architecture

### 6.1 Indexing Process

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Directory│────►│  Crawler │────►│ Metadata │────►│  Storage │
│ Scanner  │     │          │     │ Extractor│     │  Manager │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      ▲                                                 │
      │                                                 │
      │          ┌──────────┐     ┌──────────┐         │
      └──────────┤  Change  │◄────┤ Database │◄────────┘
                 │ Monitor  │     │ Manager  │
                 └──────────┘     └──────────┘
```

### 6.2 Incremental Indexing

The system uses a two-phase indexing approach:

1. **Initial Indexing**: Full scan of all included directories
2. **Incremental Updates**: Monitor file system changes

File system changes are tracked using:
- FSEvents on macOS
- Watchdog fallback on other platforms

### 6.3 Throttling Mechanism

Indexing is throttled based on:

1. System CPU load
2. Battery status (reduced on battery)
3. User activity (reduced when active)
4. Time of day (more aggressive during idle periods)

### 6.4 Cloud Detection

Cloud providers are detected through a multi-stage process:

1. Known path patterns for each provider
2. Special file markers
3. Extended attributes where available
4. Provider-specific APIs when possible

## 7. Security Architecture

### 7.1 Permissions Model

The application follows the principle of least privilege:

1. Requests only necessary file system permissions
2. Uses secure APIs for file operations
3. Explicitly handles permission errors
4. Gracefully degrades when permissions are limited

### 7.2 Secure Storage

Sensitive data is stored securely:

1. Search history is stored in the SQLite database
2. No user authentication data is stored
3. No file contents are stored, only metadata

### 7.3 Update Security

The update process follows security best practices:

1. Updates are signed with developer certificate
2. Update packages are verified before installation
3. Update sources are restricted to official channels
4. Failed updates can be rolled back

### 7.4 Code Signing

Application distribution follows Apple's security requirements:

1. Code is signed with a developer certificate
2. Hardened runtime is enabled
3. Appropriate entitlements are configured
4. Notarization process is followed

## 8. Performance Optimization Architecture

### 8.1 Database Optimizations

1. **Prepared Statements**: All queries use prepared statements
2. **Indexing Strategy**: Strategic indexes on frequently queried columns
3. **Transaction Batching**: Operations are batched for efficiency
4. **Connection Pooling**: Connections are reused appropriately
5. **Query Planning**: Complex queries are analyzed and optimized

### 8.2 Memory Optimizations

1. **Lazy Loading**: Results are loaded only when needed
2. **Object Pooling**: Common objects are reused when possible
3. **Resource Management**: Explicit cleanup of large resources
4. **Caching Strategy**: Frequently accessed data is cached
5. **Memory Monitoring**: Usage is tracked and optimized

### 8.3 I/O Optimizations

1. **Buffered Reading**: File operations use appropriate buffers
2. **Asynchronous I/O**: Non-blocking operations where possible
3. **Batch Processing**: Operations are grouped to minimize system calls
4. **Throttling**: I/O is throttled to avoid system impact
5. **Prioritization**: Critical operations are prioritized

## 9. Testing Architecture

### 9.1 Test Types

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **Performance Tests**: Verify performance requirements
4. **UI Tests**: Test user interface functionality
5. **End-to-End Tests**: Test complete workflows

### 9.2 Test Infrastructure

1. **pytest**: Core testing framework
2. **coverage.py**: Measure code coverage
3. **mocks**: Isolate components for testing
4. **fixtures**: Provide common test data
5. **benchmarks**: Measure performance metrics

### 9.3 Continuous Integration

1. Every commit runs the test suite
2. Quality checks enforce standards
3. Performance regressions are detected
4. Test coverage is monitored
5. Documentation is verified

## 10. Deployment Architecture

### 10.1 Application Bundle

The macOS application is packaged as a standard .app bundle:

```
Panoptikon.app/
├── Contents/
│   ├── Info.plist          # Application metadata
│   ├── MacOS/              # Executable files
│   │   └── Panoptikon      # Main executable
│   ├── Resources/          # Application resources
│   │   ├── icons/          # Icon files
│   │   └── assets/         # Other assets
│   ├── Frameworks/         # Required frameworks
│   │   └── Python.framework # Embedded Python
│   └── _CodeSignature/     # Code signature
└── ...
```

### 10.2 Update Mechanism

Updates follow this architecture:

1. Check for updates from secure server
2. Download update package with signature
3. Verify package integrity and signature
4. Install update with proper permissions
5. Restart application if necessary

### 10.3 DMG Distribution

The application is distributed via a standard macOS DMG:

1. Contains the application bundle
2. Includes shortcut to Applications folder
3. Custom background and appearance
4. License agreement if necessary
5. Simple drag-and-drop installation
