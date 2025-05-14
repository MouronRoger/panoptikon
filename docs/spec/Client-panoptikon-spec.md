# 📑 **Panoptikon Client Specification**

## 📋 **Release Strategy and Core Philosophy**

**Stage 1 Focus - Minimal "Everything" Clone**: The initial release of Panoptikon will deliver a focused, high-performance file search application that indexes and searches by filename only, similar to the popular Windows utility "Everything". This approach prioritizes speed, reliability, and immediate utility while establishing the architectural foundation for future enhancements.

**Core Design Philosophy**: "The idea of the Panoptikon is that it knows where everything is. It has no blindspots." The application must provide comprehensive visibility across all file storage locations with zero configuration, delivering instant results regardless of where files are stored.

**Deferred Capabilities**: Content indexing, OCR, full-text search, advanced boolean operators, intelligent ranking, CLI integration, watch queries, and metadata filtering are explicitly deferred to future releases. The architecture will be designed with extension points to ensure these capabilities can be added later without significant refactoring.

**Essential Core Features**: The initial release will focus exclusively on ultra-fast filename search, customizable tabs, basic filtering options, seamless cloud integration, flexible column customization, and native macOS integration with Finder.

## 🚀 **Purpose and Scope**

Panoptikon is a fast, lightweight file-search application for macOS, designed to help individual users reclaim control over scattered data. By day one, it must deliver an intuitive, high-performance search experience that locates files by name across local disks, network shares, and popular cloud services. This document captures, in concrete terms, every requirement Panoptikon must deliver before any technical architecture work begins. Its language is precise and measurable, ensuring no requirement remains open to interpretation.

## 🎯 **Target Audience**

Panoptikon serves three primary user groups: students managing research papers and lecture notes; home users organizing personal documents and media; and home-office workers handling reports, spreadsheets, and contracts. It explicitly excludes specialized workflows such as film editing, music production, or real-time collaboration.

## 🖥️ **Context of Use**

A user invokes Panoptikon via a global hotkey, the menu-bar icon, or the Dock. Within a fraction of a second, a minimalist window appears with the search field focused. As the user types a filename fragment, matching entries populate instantly in a familiar list view. Users accustomed to macOS drag-and-drop and Finder context menus feel at home immediately; those switching from Windows recognize the responsiveness reminiscent of "Everything."

## 🎨 **User Interface and Design**

**Tabbed Layout**: Search results display within a tabbed interface at the top of the window. Tabs default to categories (All Files, Documents, Spreadsheets, PDFs, Folders, Images, Audio, Video, Archive, Apps, Custom) and can be user-defined. Switching tabs filters results by predefined or custom criteria without losing the search query.

**Customizable Tabs (Preset, Not Hardcoded)**: The default tab set (All Files, Documents, PDFs, etc.) is provided as a starting point but is not fixed. Users can rename, delete, reorder, or add tabs via contextual interaction. Each tab maps to a saved filter configuration—by file type, extension, or path rules—which the user can modify directly. Tab definitions persist across sessions and reflect user preferences without requiring reconfiguration.

**Columns and Context Menus**: The default columns—Name, Type, Extension, Size, Date Created, Date Modified, Path, and Cloud Status—appear in a sortable list. Users may reveal, hide, and reorder columns through direct manipulation of the header. Right-clicking or two-finger tapping any row exposes Finder-consistent commands: Open, Open With…, Reveal in Finder, Quick Look, Copy Path, and Move to Trash. All commands apply seamlessly to multiple selected rows.

***Dual Input Method Support***: The interface provides ***equal emphasis on keyboard shortcuts for Mac power users alongside comprehensive right-click context menus for Windows migrants***. ***Mouse hover tooltips assist Windows users unfamiliar with Mac conventions***, while ***visual indicators clearly show all available actions accessible via both mouse and keyboard methods***. This dual-input design ensures both user groups can operate efficiently according to their established habits.

***Interaction Consistency***: The application ***maintains Mac interface conventions while simultaneously providing familiar Windows equivalents***. Drag-and-drop operations ***behave exactly as expected in Finder while offering familiar feedback for Windows users***. The interface includes a ***status bar with information presentation familiar to Windows users without compromising Mac aesthetics***. The application ***supports both Mac trackpad gestures and Windows-style mouse wheel behaviors*** for navigation and interaction.

## ⚙️ **Functional Requirements**

**Search Filtering by Filename**: The search field filters by filename alone, updating results with no perceptible lag and smooth, flicker-free rendering. As the core functionality of Stage 1, this capability must be optimized for maximum performance and reliability.

**Basic Search Capabilities**: Panoptikon supports simple, intuitive search patterns that focus on filename matching. Core search functionality includes:

* Wildcard patterns (\*, ?) for flexible filename matching
* Case-sensitive or case-insensitive matching via a simple toggle
* Whole word matching via a simple toggle
* Extension filtering via a dedicated adjacent field for quick `*.extension` searches

Complex boolean operators and special syntax are intentionally omitted to maintain simplicity and performance.

**Bookmarks and Favorites**: Users can bookmark frequently accessed files, folders, or searches for rapid access. Bookmarks persist across sessions and can be organized within the interface. This feature provides quick access to important items without requiring complex search history management.

**Path Inclusion/Exclusion Logic**: Users can define include and exclude rules for file paths. Include rules accept specific folders or volumes; exclude rules omit specified directories, subtrees, or mount points. The UI exposes a preferences panel where users add, edit, and reorder path rules. Exclude rules take precedence over include rules.

**File Type Inclusion/Exclusion Filters**: Beyond tabs, users can create custom file-type filters by specifying extensions or MIME types. These filters integrate with tabs and can be toggled in the preferences panel, enabling or disabling types globally or per tab.

**Granular Inclusion/Exclusion Control**: The system allows for fine-grained control where users can exclude specific paths, files, and filetypes while including others. ***Importantly, the system supports hierarchical overrides where a child directory can be explicitly included even when its parent directory is excluded***. This capability is especially relevant for cloud storage files typically stored in system locations like the .library folder, allowing users to include cloud documents without indexing the entire system directory structure.

**Indexing Progress Indicator**: During initial indexing or manual updates, a non-intrusive progress indicator displays percent-complete and estimated time remaining. Users may pause or throttle indexing threads via preferences to control resource usage.

***Visual Disambiguation***: The interface provides ***clear visual distinction for files with identical names in different locations***, ensuring users can immediately identify the specific file they need. ***Path information is immediately visible without requiring additional clicks or hover actions***. The system provides ***instant visual feedback when typing matches zero files***, and includes ***progressive loading indicators for very large result sets*** to maintain responsive feel.

## ☁️ **Cloud and Network Integration**

Panoptikon's index includes files on internal drives, connected external volumes, network shares, and supported cloud providers—iCloud, Dropbox, Google Drive, OneDrive, and Box. Files downloaded to disk display on a neutral background; placeholders for cloud-only items appear tinted, with a tooltip explaining that the file must be hydrated before opening. Rows for unavailable network volumes appear dimmed and revive instantly once the volume reconnects.

**Seamless Cloud Delegation**: Panoptikon does not directly integrate each cloud provider's API. Instead, it delegates file hydration and opening to the system's native integration or provider-specific helper, invoking a single standard call to reveal or open a file path. This approach ensures a transparent, consistent user experience where cloud document downloads and opening are deferred seamlessly and invisibly to Finder. The user should never need to consider whether a file is cloud-based or local—Panoptikon knows where everything is with no blindspots, and handles the details transparently.

## 🗄️ **Database and Caching**

Panoptikon maintains a local, lightweight database to store file index metadata. This database persists between launches, supports incremental updates driven by filesystem events, and caches information about offline or cloud-only files to avoid costly full re-indexing. When a network or cloud file is unavailable, its metadata remains accessible in the database so that the app can display placeholder entries instantly and hydrate files on demand without delaying search results.

**Future-Proof Database Design**: While the initial release focuses on filename indexing only, the database schema will be designed with extensibility in mind, including provisions for future content-based search capabilities. This forward-looking approach ensures that future enhancements can be added without requiring database migration or redesign.

## ⚡ **Performance and Resource Constraints**

Initial indexing of up to 250,000 files shall complete in under one minute on an Apple Silicon MacBook Air, consuming no more than twenty percent of a single CPU core and 500 MB of RAM. Incremental updates driven by filesystem events must never block the UI and must process batches in under fifty milliseconds. From final keystroke to fully rendered results, search latency must remain below fifty milliseconds for indexes up to 250,000 entries. Launch time from invoking the hotkey to a focused search field must stay under one hundred milliseconds under normal system load. When idle, Panoptikon's resident memory footprint must remain below fifty megabytes and CPU usage must be negligible.

***Speed Benchmarks From User Perspective***: To ensure the application feels instantaneous to users, the following metrics must be met: ***"no perceptible lag" is defined as under 16ms (one frame) response time between user action and visible feedback***; ***"instant appearance" requires first results to be visible within 50ms of keystroke***; ***complete result set updates must occur within 100ms maximum***; and ***UI rendering must maintain minimum 60fps during typing and scrolling operations***. These benchmarks ensure the application feels native and responsive to both Mac and Windows users accustomed to high-performance search.

## 🌐 **Accessibility, Internationalization, and Localization**

Every control carries an accessibility label and is fully operable via VoiceOver and keyboard alone, enabling users to perform searches, apply filters, execute context commands, switch tabs, and quit the app without a pointing device. All user-visible text loads from localization files; the initial languages supported are English, French, and German. The interface respects system settings for Dark Mode, increased contrast, and dynamic type sizes.

## 🔒 **Privacy, Permissions, and Security**

Panoptikon's entire index resides locally within the user's Library container and, if FileVault is enabled, benefits from disk encryption. Under no circumstances does the app transmit filenames, paths, or usage metrics off-device. On first launch, Panoptikon requests Full Disk Access through standard macOS entitlements. If the user declines, the app continues to index accessible locations and displays a non-intrusive banner explaining reduced visibility, with a link to help documentation. The application bundle is notarized, sandboxed, and signed with a Developer ID certificate. Updates are delivered securely via Sparkle with ed25519 verification.

## 🧩 **Platform Support and Non-Functional Constraints**

Panoptikon supports macOS 13 (Ventura) and later, on both Apple Silicon and Intel architectures. Continuous integration tests enforce all performance metrics and fail the build on regression. User data structures are resilient to sudden power loss; index rebuilds occur only on first launch or after a verified corruption event. The codebase adheres to native Apple Human Interface Guidelines, ensuring a polished, familiar experience.

## 🏗️ **Architectural Decisions**

**Stage 1 Focus**: Stage 1 will implement fast, filename-only search with all advanced search filters—boolean logic, date range, and size range. The architecture will establish clear boundaries between index management, search operations, and UI components, with well-defined interfaces to support future capabilities.

**Deferred Features**: Content indexing, OCR, and full-text search capabilities are deliberately deferred to future stages. However, the architecture will be designed with these capabilities in mind, with clear extension points identified during the design phase.

**Technical Foundations**: Offline network volumes and cloud‑only files leverage the lightweight database cache to guarantee sub‑100 ms response times. Duplicate filenames remain separate entries; grouping modes and further UI refinements will be revisited in post‑1.0 updates.

## ⭐ **Additional User-Centric Features**

**Inline Preview Pane**: A resizable side panel displays Quick Look previews (text, PDF, image, audio waveforms, video thumbnails) for the selected file without opening a separate window.

**Content Search Option (Future Phase)**: In future releases, Panoptikon will expand beyond filename search to include content indexing capabilities. This will enable users to search within file contents (text, PDF, Office docs) with appropriate resource management controls. Similarly, OCR-powered text extraction for images and scanned PDFs will be implemented in a future phase. The Stage 1 architecture will be designed with these capabilities in mind to ensure smooth integration when implemented.

**Drag and Drop Support**: Comprehensive drag and drop functionality is supported throughout the application:
* Drag files from results to Finder or other applications
* Drag files between multiple Panoptikon windows
* Drag files to the Dock, Desktop, or folders
This integration with macOS's native drag and drop capabilities ensures seamless workflow integration.

**File Information Display**: Basic file metadata (size, dates, extension, type) is displayed in the results list through customizable columns. Advanced metadata filtering and tag-based searches are deferred to future releases to maintain focus on core filename search functionality.

**Favorites and Pinned Searches**: Users can mark folders or files as favorites for rapid access and pin saved searches to the UI toolbar. Keyboard shortcuts allow quick jumping to favorites or pinned queries.

**Keyboard-Driven Workflow**: Complete operation via keyboard: global hotkey to invoke search, arrow keys to navigate results, Return to open, spacebar to Quick Look, and customizable shortcuts for context commands.

**Rich Context Menu Options**: Right-click context menus provide essential file operations including:
* Open
* Open with...
* Reveal in Finder
* Copy path (full path to clipboard)
* Copy filename (just the filename to clipboard)
* Move to Trash
These operations apply seamlessly to multiple selected files.

**Multi-Window Support**: Users can open multiple Panoptikon windows simultaneously, each with independent search queries and result views. Drag and drop operations are supported both within and between windows, enabling efficient file management workflows.

**Flexible Column Customization**: The results view offers comprehensive column customization:
* Users can show/hide individual columns
* Available columns include: Name, Path, Size, Extension, Type, Date Modified, Date Created, Date Accessed, and Run Count
* Folder size calculation is supported where possible
* Columns are sortable by clicking headers
* Column positions can be changed via drag and drop
* Column preferences persist across sessions

**Import/Export Settings**: Preferences, bookmarks, inclusion/exclusion rules, and column configurations are exportable to a JSON settings file for backup or sharing.

## 📊 **Default Sorting and User Control**

**Simple, Predictable Sorting**: By default, search results are sorted by most recently modified files at the top, followed by alphabetical ordering. This approach ensures the most relevant files typically appear first without complex ranking algorithms.

**User-Controlled Sorting**: Users can manually sort the results by clicking any column header (Name, Date Modified, Size, etc.) to change the sort order. This gives direct control over result organization without automatic or "intelligent" intervention.

**Basic Run Count Tracking**: The system maintains a simple count of file opens to support the "Run Count" column, but does not implement complex usage analytics or predictive sorting.

## ✅ **Success Criteria**

**Stage 1 Success Criteria**: Panoptikon is production-ready when an unbiased tester with 250,000 files can:
1. Launch the search window
2. Find a specified file by filename
3. Open it in under one second end-to-end
4. Successfully work with local, network, and cloud files without configuration
5. Perform the above while macOS's Activity Monitor never flags Panoptikon as a top resource consumer

This criterion focuses exclusively on filename-based search performance and comprehensive file system visibility, aligning with the "no blindspots" philosophy and Stage 1 scope.

**Future Stage Success Criteria**: Success criteria for content indexing and OCR capabilities will be defined in future specification updates. The architecture must be designed to accommodate these capabilities without compromising the core performance metrics established for Stage 1.

**Additional Scalability Goal (Optional)**: The system should handle larger indexes gracefully for power users, scaling up to 1,000,000 files with proportional performance, documented as aspirational targets.

## 🛠️ **System‑Designer Instructions (KISS & Land Rover Philosophy)**

### 🌐 **Target users**

Consumers; students; home and small‑office workers; busy secretaries and administrators; small‑business managers.

### 🚫 **Non‑targets**

Large enterprises; media producers; software developers.

### 🚦 **Guiding principles**

Simplicity; robustness; zero surprises; no bloat; essentials only; every line must be justified by daily utility.

### 🔩 **Coding standards**

Python 3.11 + PyObjC; single‑purpose modules; hard limit 500 lines per file; PEP 8 plus strict linting; cyclomatic complexity < 10 per function; no dead code tolerated; commits rejected if mypy or flake8 emit warnings.

### 🧪 **Testing & build pipeline**

Tests accompany every module; unit coverage ≥ 95 % with pytest; integration smoke test after each merge; CI stops on first error; artefacts versioned and checksummed; refactors forbidden during stabilisation; critical‑path tasks mapped and gated.

### 📦 **Packaging workflow**

Prototype with editable PyObjC sources; strip to essentials; avoid external pip packages unless unavoidable (each usage must be justified and reviewed). Bundle with py2app; exclude unused stdlib modules; set `argv_emulation=False` and `LSUIElement=True` for background mode.

After stabilisation, compile with Nuitka to a self‑contained binary; wrap in Platypus or hand‑craft the .app bundle; remove unreferenced locales, docs, and resources; optionally UPX‑compress .so/.dylib files if size reduction > 10 % and no measurable performance loss.

### 📏 **Size & performance budgets**

Installed .app ≤ 30 MB; cold launch ≤ 300 ms on a 2015 MacBook Air; peak RAM < 150 MB; full‑index search across 100 k files in < 0.5 s.

### 🚫 **Forbidden practices**

No hidden network calls; no telemetry; no reflection magic; no runtime code generation; no monkey‑patching; never break stable APIs once released.

### ✅ **Definition of Done**

Binary reproduces from clean checkout with a single `make` command; all tests green; notarisation and codesigning passed; user installs by drag‑and‑drop and runs without prompts; macOS Gatekeeper accepts; zero console warnings on launch.