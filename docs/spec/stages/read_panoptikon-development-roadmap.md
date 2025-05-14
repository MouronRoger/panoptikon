# Panoptikon Development Roadmap - Pragmatic Approach

> **Terminology:**
> - "Stage" = One of the 4 high-level development units (matches directory and tags)
> - "Stage" = One of the 11 implementation units (formerly called "stages" in older docs)
> - This naming is chosen to maintain consistency with existing documentation and memory systems.

## 1. Overview

This roadmap outlines the development process for Panoptikon, a high-performance macOS filename search utility. It provides a structured approach for a single developer working with Cursor AI to implement the system architecture and deliver the Stage 1 MVP while strategically bulletproofing only the most critical OS-dependent components.

The roadmap is organized into **Development Stages** (timeline-based milestones) and **Stages** (detailed implementation units). Each stage encompasses specific stages, building upon the previous ones while maintaining testability, quality, and focused OS resilience throughout the process.

## 2. Development Stages & Stages

### 2.1 Development Stage 1: Foundation (Weeks 1-2)
*Encompasses Stages 1-4*

**Focus**: Establish the core project structure, development environment, and foundational components.

#### Stage 1: Project Initialization

##### Development Environment Setup

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Environment Configuration | Set up Python 3.11+ with virtual environment | 0.5 day |
| Build System | Create Makefile with development targets | 0.5 day |
| IDE Setup | Configure IDE with linting and type checking | 0.5 day |
| CI Pipeline | Set up basic CI for automated testing | 1 day |

##### Project Structure

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Directory Structure | Create core directory structure and package organization | 0.5 day |
| Testing Framework | Configure pytest with markers and coverage reporting | 0.5 day |
| Linting Configuration | Set up flake8, mypy, black with strict rules | 0.5 day |
| Pre-commit Hooks | Configure hooks for code quality enforcement | 0.5 day |

#### Stage 2: Core Infrastructure

##### Core Architecture Implementation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Service Container | Implement dependency injection container | 1 day |
| Event Bus | Create event publication/subscription system | 1 day |
| Configuration System | Build settings management framework | 1 day |
| Error Handling | Implement error reporting and recovery system | 1 day |
| Application Lifecycle | Create startup/shutdown sequence management | 1 day |

#### Stage 3: Filesystem Abstraction

##### Critical OS Abstraction Implementation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| FSEvents Wrapper | Create isolation layer for file system monitoring | 1.5 days |
| FS Access Abstraction | Implement permission-aware file system operations | 1.5 days |
| Cloud Detection | Build provider-agnostic cloud storage detection | 1 day |
| Permission Management | Create security-scoped bookmark handling | 1 day |
| Path Management | Implement path normalization and handling | 1 day |

#### Stage 4: Database Foundation

##### Database Implementation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Schema Creation | Implement core database schema | 1 day |
| Connection Pool | Create thread-safe connection management | 1 day |
| Migration System | Build simple schema migration framework | 1 day |
| Query Optimization | Design and implement prepared statements | 1 day |
| Data Integrity | Configure WAL journaling and integrity checks | 1 day |

##### Milestone: Foundation Ready

**Deliverables**:
- Functional development environment with automated testing
- Service container with dependency registration
- Event bus with publish/subscribe capabilities
- Key OS abstraction layers for critical components
- SQLite database with schema versioning
- Basic configuration system

**Quality Gates**:
- 95% test coverage for all components
- All linters pass with zero warnings
- Documentation for all public interfaces
- Successful database migrations
- FSEvents wrapper properly isolated

### 2.2 Development Stage 2: Core Engine (Weeks 3-5)
*Encompasses Stages 5-6*

**Focus**: Implement the core search and indexing capabilities that form the heart of the application.

#### Stage 5: Search Engine

##### Search Engine Implementation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Query Parser | Implement filename pattern parsing | 2 days |
| Search Algorithm | Build optimized search implementation | 3 days |
| Result Management | Create result collection and organization | 1 day |
| Sorting System | Implement flexible result sorting | 1 day |
| Filtering System | Build filter application framework | 2 days |

##### File System Integration

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Path Rule System | Build include/exclude rule evaluation | 2 days |
| Result Caching | Implement search result caching | 1 day |
| Search Optimization | Optimize for common search patterns | 2 days |

#### Stage 6: Indexing System

##### Indexing Implementation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Initial Scanner | Build recursive directory scanning | 2 days |
| Incremental Updates | Implement change-based index updates | 2 days |
| Batch Processing | Create efficient batch database operations | 1 day |
| Progress Tracking | Implement indexing progress monitoring | 1 day |
| Priority Management | Build intelligent scanning prioritization | 1 day |

##### Metadata Extraction

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| File Metadata | Create file metadata extraction | 2 days |
| File Type Detection | Implement file type identification | 1 day |
| Cloud Metadata | Support cloud provider metadata | 1 day |

##### File System Monitoring

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| FSEvents Implementation | Create native FSEvents integration | 1 day |
| Fallback Monitoring | Build polling-based alternative for reliability | 2 days |
| Event Processing | Implement event coalescing and filtering | 1 day |
| Shadow Verification | Design verification for network storage | 1 day |

##### Milestone: Functional Core

**Deliverables**:
- Working search engine with wildcard support
- File system monitoring with resilience strategy
- Complete indexing system with incremental updates
- Path inclusion/exclusion rule evaluation
- Permission-aware file operations
- Basic file operations

**Quality Gates**:
- Search completes in <50ms for 10k test files
- Indexing processes >1000 files/second
- File monitoring correctly captures changes with multiple strategies
- Path rules correctly filter files
- Permission handling works with different access levels
- 95% test coverage maintained

### 2.3 Development Stage 3: UI Framework (Weeks 6-8)
*Encompasses Stage 7*

**Focus**: Create the native user interface and interaction model that provides the dual-paradigm experience.

#### Stage 7: UI Framework

##### Window and Controls

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Main Window | Implement primary application window | 2 days |
| Search Field | Create search input with real-time filtering | 1 day |
| Tab Bar | Build category filtering system | 2 days |
| Results Table | Implement virtual table view for results | 3 days |
| Column Management | Create customizable column system | 2 days |

##### Interaction Model

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Keyboard Shortcuts | Implement comprehensive keyboard navigation | 1 day |
| Context Menus | Create right-click operation menus | 2 days |
| Drag and Drop | Implement drag support for files | 2 days |
| Selection Management | Build multiple item selection handling | 1 day |
| Double-Click Actions | Implement default file actions | 0.5 day |

##### UI Component Abstraction

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Component Composition | Implement composition over inheritance for UI | 2 days | 
| Presentation-Logic Separation | Create clear boundary between UI and business logic | 1 day |
| Accessibility Framework | Implement VoiceOver compatibility | 2 days |
| Layout Adaptation | Build support for different screen densities | 1 day |

##### Progress and Feedback

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Progress Overlay | Create non-intrusive progress visualization | 1 day |
| Status Bar | Implement informational status display | 1 day |
| Tooltips | Add contextual information tooltips | 1 day |
| Error Presentation | Build user-friendly error notifications | 1 day |
| Animation System | Create smooth transitions and indicators | 1 day |

##### Milestone: Interactive UI

**Deliverables**:
- Complete user interface with search field, tabs, and results
- Dual-paradigm interaction supporting keyboard and mouse
- Context menus with file operations
- Progress visualization for background operations
- Drag and drop support
- Resilient UI implementation for key components

**Quality Gates**:
- UI renders at 60fps during normal operations
- All functions accessible via keyboard and mouse
- Interface follows macOS Human Interface Guidelines
- VoiceOver compatibility for accessibility
- Tooltips provide clear guidance for both paradigms
- Component abstraction properly isolates UI framework dependencies

### 2.4 Development Stage 4: Integration (Weeks 9-10)
*Encompasses Stages 8-9*

**Focus**: Connect all components and implement cloud provider integration, preferences, and system integration.

#### Stage 8: Cloud Integration

##### Cloud Provider Integration

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Provider Detection | Implement cloud storage identification | 2 days |
| Status Visualization | Create indicators for cloud files | 1 day |
| Operation Delegation | Build provider-specific handling | 2 days |
| Placeholder Support | Implement cloud-only file indicators | 1 day |
| Offline Handling | Create graceful offline experience | 1 day |

##### Preferences System

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Preferences Panel | Build configuration interface | 2 days |
| Path Rule Editor | Create include/exclude rule management | 2 days |
| Tab Customization | Implement tab creation and editing | 1 day |
| Column Settings | Build column visibility and order control | 1 day |
| Settings Persistence | Implement preference saving/loading | 1 day |

#### Stage 9: System Integration

##### System Integration Implementation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Global Hotkey | Implement system-wide activation with fallbacks | 1.5 days |
| Menu Bar Icon | Create status item with menu | 1 day |
| Dock Integration | Build proper dock icon behavior | 0.5 day |
| Finder Integration | Implement reveal in Finder function | 1 day |
| Permissions Management | Create Full Disk Access guidance | 1.5 days |
| Multi-Window Support | Implement multiple window management | 2 days |

##### Milestone: Complete Integration

**Deliverables**:
- Full cloud provider support (iCloud, Dropbox, OneDrive, Google Drive, Box)
- Comprehensive preferences management
- System integration with hotkey, menu bar, and dock
- Permissions handling with graceful degradation
- Complete file operations across all storage types
- Multi-window support with independent searches

**Quality Gates**:
- Cloud files correctly identified and handled
- Preferences correctly persisted between launches
- System integration functions as expected
- Graceful behavior with limited permissions
- Operations work consistently across storage types
- Alternative system integration methods work when primary fails
- Multi-window drag-and-drop operations work reliably

### 2.5 Development Stage 5: Optimization (Weeks 11-12)
*Encompasses Stage 10*

**Focus**: Fine-tune performance, memory usage, and user experience to meet or exceed all targets.

#### Stage 10: Optimization

##### Performance Optimization

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Launch Time | Optimize application startup to <100ms | 2 days |
| Search Latency | Fine-tune search to consistently <50ms | 2 days |
| UI Responsiveness | Ensure 60fps rendering at all times | 2 days |
| Indexing Speed | Optimize to handle 250k files in <60s | 2 days |
| Resource Usage | Minimize memory and CPU footprint | 2 days |

##### Memory Management

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Memory Profiling | Identify and fix memory leaks | 2 days |
| Cache Optimization | Fine-tune caching strategies | 1 day |
| PyObjC Boundary | Optimize language crossing patterns | 2 days |
| Thread Confinement | Ensure proper object ownership | 1 day |
| Resource Scaling | Implement dynamic resource adjustment | 1 day |

##### Resilience Verification

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| File Monitoring Testing | Verify correct operation across scenarios | 1 day |
| Permission Testing | Validate behavior with various permission levels | 1 day |
| Cloud Integration Testing | Test across cloud providers and conditions | 1 day |
| UI Framework Testing | Verify component abstraction effectiveness | 1 day |
| Error Recovery | Test and enhance recovery mechanisms | 1 day |

##### User Experience Refinement

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| First-Run Experience | Create welcoming onboarding | 1 day |
| Help System | Implement contextual guidance | 1 day |
| Keyboard Shortcuts | Finalize and document shortcuts | 0.5 day |
| Visual Refinement | Polish UI details and animations | 2 days |
| Feedback Mechanisms | Add subtle user guidance | 0.5 day |

##### Milestone: Production Ready

**Deliverables**:
- Performance-optimized application meeting all targets
- Memory-efficient implementation with no leaks
- Verified resilience for critical OS touchpoints
- Polished user experience with first-run guidance
- Complete help documentation
- Final visual refinements

**Quality Gates**:
- Launch time consistently <100ms
- Search latency consistently <50ms
- UI renders at 60fps under all conditions
- Indexing handles 250k files in <60s
- Idle memory usage <50MB
- Bundle size <30MB
- All tests passing with ≥95% coverage
- File monitoring works reliably across different conditions
- Graceful behavior with permission changes
- Consistent operation with cloud provider variation

### 2.6 Development Stage 6: Packaging and Release (Week 13)
*Encompasses Stage 11*

**Focus**: Create the final application bundle, complete documentation, and prepare for distribution.

#### Stage 11: Packaging and Release

##### Final Packaging

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Prototype Refinement | Finalize PyObjC + Python 3.11+ implementation with minimal dependencies | 1 day |
| py2app Bundling | Bundle with py2app using excludes for unused modules | 1 day |
| Nuitka Compilation | Compile to self-contained binary using Nuitka | 1.5 days |
| Application Wrapping | Wrap with Platypus or build .app bundle manually | 0.5 day |
| Size Optimization | UPX compress .so/.dylib files, clean unused locales/resources | 1 day |
| Code Signing | Sign application with developer ID | 0.5 day |
| Notarization | Submit for Apple notarization | 0.5 day |
| DMG Creation | Package application for distribution | 0.5 day |

##### Documentation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| User Guide | Create comprehensive documentation | 2 days |
| Release Notes | Prepare detailed release information | 0.5 day |
| Known Issues | Document any limitations or issues | 0.5 day |
| Future Roadmap | Outline planned enhancements | 0.5 day |
| Developer Documentation | Finalize technical documentation | 1 day |

##### Release Preparation

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| Final Testing | Complete comprehensive test pass | 1 day |
| Version Management | Set final version numbers | 0.5 day |
| Update System | Configure Sparkle for updates | 1 day |
| Website Preparation | Update website with release info | 1 day |
| Distribution Channel | Prepare distribution mechanism | 0.5 day |

##### Milestone: Initial Release

**Deliverables**:
- Signed and notarized application bundle
- Distribution-ready DMG package
- Complete user and developer documentation
- Configured update system
- Website with release information

**Quality Gates**:
- Installation works via drag-and-drop
- Application passes Gatekeeper validation
- All features function as expected
- Update system correctly detects new versions
- Documentation covers all features and functions

## 3. Stage & Stage Summary

| Development Stage | Weeks | Stages | Focus |
|------------------|-------|--------|-------|
| Stage 1: Foundation | 1-2 | Stages 1-4 | Environment, Infrastructure, Abstractions, Database |
| Stage 2: Core Engine | 3-5 | Stages 5-6 | Search Engine, Indexing System |
| Stage 3: UI Framework | 6-8 | Stage 7 | User Interface & Interaction |
| Stage 4: Integration | 9-10 | Stages 8-9 | Cloud Integration, System Integration |
| Stage 5: Optimization | 11-12 | Stage 10 | Performance & User Experience |
| Stage 6: Packaging | 13 | Stage 11 | Final Build & Release |

## 4. Testing Strategy

[Rest of document continues unchanged...]

## 10. Conclusion

This development roadmap provides a structured approach to delivering Panoptikon using a clear hierarchy of Development Stages (timeline milestones) and Stages (implementation details). By organizing the work into these two levels, the plan offers both high-level progress tracking and detailed implementation guidance.

The emphasis on early implementation of high-risk components, multiple implementation strategies for volatile OS interfaces, and comprehensive testing will ensure a high-quality, performant, and resilient application that delivers on the promise: "it knows where everything is with no blindspots."