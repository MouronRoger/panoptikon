# Panoptikon Technical Specification

## 1. Project Overview

### 1.1 Product Vision

Panoptikon is a high-performance, lightweight file search application designed to enable users to instantly find files by name across their entire system. The application directly emulates the Windows "Everything" search utility for macOS, with special emphasis on cloud storage integration.

### 1.2 Land Rover Philosophy

Panoptikon follows the "Land Rover philosophy" of simplicity, robustness, and fitness for purpose:

- **Simplicity**: Focus on core functionality without unnecessary complexity
- **Robustness**: Operate reliably under all conditions
- **Fitness for Purpose**: Optimize for the primary use case of fast file searching

### 1.3 Target Platforms

The application targets desktop environments with macOS as the primary platform. The architecture allows for potential future expansion to other platforms while maintaining core performance requirements.

## 2. Technical Architecture

### 2.1 Technology Stack

- **Backend**: Python 3.9+
- **Database**: SQLite
- **Frontend**: PyObjC (Native macOS UI)
- **Build System**: Poetry/Hatch
- **Quality Tools**: ruff, black, mypy, pytest

### 2.2 Component Architecture

![Component Architecture](assets/component-architecture.png)

The application consists of the following main components:

1. **File Indexing System**: Responsible for scanning the file system and collecting metadata
2. **Database Module**: Manages metadata storage and retrieval
3. **Search Engine**: Processes user queries and returns relevant results
4. **Cloud Integration**: Detects and tracks cloud storage status
5. **UI Components**: Provides native macOS interface
6. **Configuration System**: Manages application settings

### 2.3 Data Flow

1. The Indexing System scans the file system and collects metadata
2. Metadata is stored in the SQLite database
3. User enters search terms in the UI
4. Search Engine processes the query against the database
5. Results are displayed to the user in the UI
6. File operations are performed using native macOS APIs

## 3. Core Components Specification

### 3.1 File Indexing System

#### 3.1.1 Responsibilities
- Recursively scan directories for files
- Extract file metadata
- Monitor file system for changes
- Handle file system permissions
- Support throttled, background indexing

#### 3.1.2 Key Modules
- `index/crawler.py`: Directory traversal
- `index/metadata.py`: File metadata extraction
- `index/monitor.py`: File system change detection
- `index/exclusion.py`: Directory/file exclusion patterns

#### 3.1.3 Performance Requirements
- Index at least 1,000 files per second on reference hardware
- Support incremental indexing
- Maintain an index-to-data size ratio below 10%
- Minimal impact on system performance during indexing

### 3.2 Database Module

#### 3.2.1 Responsibilities
- Store file metadata efficiently
- Provide fast query capabilities
- Support schema migrations
- Manage database connections
- Optimize for search performance

#### 3.2.2 Key Modules
- `db/schema.py`: Database schema definition
- `db/connection.py`: Connection management
- `db/operations.py`: CRUD operations
- `db/migrations.py`: Schema version management

#### 3.2.3 Schema Design
The database includes the following primary tables:
- `files`: Core file metadata
- `directories`: Included/excluded directories
- `settings`: Application configuration
- `search_history`: Past searches
- `cloud_providers`: Cloud provider information

### 3.3 Search Engine

#### 3.3.1 Responsibilities
- Process search queries efficiently
- Support advanced search syntax
- Rank results by relevance
- Provide filtering capabilities
- Support incremental search results

#### 3.3.2 Key Modules
- `search/engine.py`: Core search coordination
- `search/parser.py`: Query parsing
- `search/filters.py`: Filter implementation
- `search/ranker.py`: Result ranking
- `search/results.py`: Result management

#### 3.3.3 Search Syntax
The search engine supports:
- Simple text search
- Boolean operators (AND, OR, NOT)
- Property filters (e.g., size:>1MB)
- Wildcard patterns
- Cloud provider filters

#### 3.3.4 Performance Requirements
- Search results under 200ms for basic queries
- Support for 100,000+ files in the index
- Responsive UI during search operations

### 3.4 Cloud Integration

#### 3.4.1 Responsibilities
- Detect cloud storage providers
- Track file download status
- Support cloud-specific search filters
- Monitor cloud storage changes

#### 3.4.2 Key Modules
- `cloud/detector.py`: Provider detection
- `cloud/status.py`: Download status tracking
- `cloud/providers/`: Provider-specific implementations
- `cloud/metadata.py`: Cloud-specific metadata

#### 3.4.3 Supported Providers
- iCloud
- Dropbox
- Google Drive
- OneDrive
- Box

### 3.5 UI Components

#### 3.5.1 Responsibilities
- Provide native macOS interface
- Implement search field with live results
- Support file operations
- Integrate with menu bar
- Manage preferences

#### 3.5.2 Key Modules
- `ui/app.py`: Application container
- `ui/window.py`: Main window controller
- `ui/components/`: UI elements
- `ui/viewmodels/`: View models (MVVM pattern)
- `ui/preferences/`: Preference panels

#### 3.5.3 UI Architecture
The UI follows the MVVM (Model-View-ViewModel) pattern:
- **Models**: Core data structures
- **ViewModels**: Presentation logic
- **Views**: UI components

#### 3.5.4 PyObjC Integration
- Uses PyObjC to interact with AppKit
- Proper memory management documented
- Consistent delegate pattern usage

## 4. Phased Implementation Plan

### 4.1 Phase 0: Project Bootstrapping (Week 1)
- Set up project structure
- Configure quality tools
- Set up test framework
- Create documentation structure

### 4.2 Phase 1: MVP (Weeks 2-4)
- Implement file indexing system
- Create database schema
- Develop basic search functionality
- Build terminal interface for testing

### 4.3 Phase 2: Native macOS UI (Weeks 5-8)
- Implement PyObjC application framework
- Create search interface
- Develop results display
- Add file operations

### 4.4 Phase 3: Cloud Integration (Weeks 9-12)
- Implement cloud provider detection
- Add status tracking
- Extend search functionality
- Create UI for cloud features

### 4.5 Phase 4: Finalization (Weeks 13-16)
- Implement packaging and signing
- Add update mechanism
- Complete user documentation
- Final accessibility and UX pass

## 5. Quality Standards

### 5.1 Code Quality
- **Line Length**: Maximum 120 characters
- **File Size**: Maximum 500 lines per file
- **Function Size**: Maximum 50 lines per function
- **Class Size**: Maximum 200 lines per class
- **Complexity**: Maximum cyclomatic complexity of 10
- **Docstrings**: 95%+ coverage for public APIs
- **Type Hints**: Required for all function parameters and returns
- **Test Coverage**: Minimum 80% code coverage

### 5.2 Architecture Principles
- **Single Responsibility**: Each module has one responsibility
- **Encapsulation**: Implementation details hidden
- **Dependency Direction**: Dependencies point inward
- **No Circular Dependencies**: Prevent dependency cycles
- **Interface Stability**: Clear, stable public interfaces

### 5.3 Testing Strategy
- **Unit Tests**: For individual components
- **Integration Tests**: For component interactions
- **Performance Tests**: For critical performance paths
- **UI Tests**: For interface functionality

## 6. Performance Requirements

### 6.1 Search Performance
- Search results in under 200ms for basic queries
- Complex queries with filters in under 500ms
- UI remains responsive during search operations
- Progressive results for longer operations

### 6.2 Indexing Performance
- Index at least 1,000 files per second
- Minimal system impact during background indexing
- Pausable and resumable indexing
- Accurate progress reporting

### 6.3 Resource Usage
- Less than 200MB memory usage for 100,000 indexed files
- Minimal CPU usage when idle
- Efficient disk I/O patterns
- Proportional database size growth

## 7. Deployment and Distribution

### 7.1 Application Packaging
- Standard macOS .app bundle
- Proper resource inclusion
- Python dependency management
- Size optimization

### 7.2 Code Signing and Notarization
- Developer certificate signing
- Proper entitlements for file access
- Notarization for Gatekeeper compatibility
- Signature verification

### 7.3 Update Mechanism
- Secure update checking
- Package integrity verification
- Seamless update process
- Rollback capability

## 8. Development Workflow

### 8.1 Quality-First Approach
- Automated checks using pre-commit hooks
- Code reviews focused on quality and architecture
- Regular code quality audits
- Technical debt management

### 8.2 Phased Development
- Implement one component at a time
- Verify quality before proceeding
- Test thoroughly at each stage
- Document as you go

### 8.3 Continuous Integration
- Automated testing on commits
- Linting and formatting verification
- Type checking
- Documentation coverage checking

## 9. Acceptance Criteria

### 9.1 Functional Criteria
- All functional requirements implemented
- Successfully index 100,000+ files
- Search through index in under 200ms
- All file operations working correctly
- Cloud storage integration functioning

### 9.2 Performance Criteria
- Search response under 200ms
- Indexing speed above 1,000 files/second
- Memory usage under 200MB for 100,000 files
- Cold start time under 1 second

### 9.3 Quality Criteria
- Code coverage above 80%
- No critical or high-priority bugs
- Stable under load and edge case testing
- Meets all security requirements
- Follows platform UX guidelines
