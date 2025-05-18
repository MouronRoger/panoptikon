# 🚧 STAGE 7: UI FRAMEWORK

## 📝 OBJECTIVES
- Implement native macOS UI with AppKit via PyObjC
- Create dual-paradigm interface (keyboard and mouse)
- Build search field, tab bar, and results table
- Implement context menus and file operations
- Develop progress visualization and status displays
- Create dual-window support with cross-window drag-and-drop (USP)

## 🔧 IMPLEMENTATION TASKS

1. **Window and Controls**:
   - Implement main application window
   - Create search input with real-time filtering
   - Build tab bar for category filtering
   - Implement virtual table view for results
   - Create column management system

2. **Dual-Window Support** (Core USP):
   - Implement DualWindowManager service
   - Create WindowState for window-specific state management
   - Build window toggle functionality (button and Cmd+N shortcut)
   - Implement smart window positioning algorithm
   - Create active/inactive window visual states (color vs. grayscale)
   - Enable cross-window drag-and-drop operations
   - Implement resource management for active/inactive windows

3. **Interaction Model**:
   - Implement comprehensive keyboard navigation
   - Create context menus for operations
   - Build drag and drop support
   - Implement selection management
   - Design default file actions

4. **UI Component Abstraction**:
   - Implement composition pattern for UI
   - Create separation between UI and business logic
   - Build accessibility support for VoiceOver
   - Design layout adaptation for screen densities

5. **Progress and Feedback**:
   - Create non-intrusive progress visualization
   - Implement status bar for information
   - Add contextual tooltips
   - Build user-friendly error notifications
   - Create smooth animations and transitions

6. **UI-Core Integration**:
   - Implement search integration
   - Create result display binding
   - Build operation delegation
   - Design state synchronization

## 🧪 TESTING REQUIREMENTS
- Verify UI renders at 60fps during operations
- Test keyboard navigation covers all functions
- Validate context menus work correctly
- Measure UI responsiveness during indexing
- Verify VoiceOver accessibility
- Test UI with large result sets
- Maintain interface compliance with HIG
- Test UI component isolation
- Verify window switching performance (<100ms)
- Validate cross-window drag-and-drop operations
- Test window state independence
- Verify active/inactive window styling is clear and consistent

## 🚫 CONSTRAINTS
- Use composition over inheritance for UI
- Maintain clear separation of concerns
- Design for resilience against UI framework changes
- Support both keyboard and mouse workflows equally
- Limit to binary window model (main + secondary)
- Minimize resource usage in inactive window

## 📋 DEPENDENCIES
- Stage 2 service container
- Stage 2 event bus
- Stage 4 database access
- Stage 5 search engine
- Stage 6 indexing system
- WindowEvent classes from preliminary implementation
- WindowManagerInterface from preliminary implementation

## Folder Size Display in UI

- The "Folder Size" column and sorting depend on the presence of the `folder_size` column (schema 1.1.0, migration complete; see [Folder Size Implementation](../../components/folder-size-implementation.md)).
- Add a "Folder Size" column to the results table, visible for directories (pending).
- Format folder sizes in human-readable units (KB/MB/GB).
- Enable sorting by folder size in the UI.
- This provides instant visibility into space usage and is a unique selling point (see Integration Report).
- Depends on schema and indexing work in earlier stages, and on migration system to ensure all databases are upgraded.

## Dual-Window Implementation

- Implement dual-window support as a key USP (Unique Selling Point) that differentiates Panoptikon from competitors.
- The dual-window feature enables drag-and-drop operations between independent search contexts.
- Follow the binary window model (main + secondary) for simplicity and performance.
- Use visual differentiation (full color vs. grayscale) to indicate active/inactive states.
- Implement resource management to ensure inactive window uses minimal resources.
- Support window toggling via both UI button and keyboard shortcut (Cmd+N).
- This implementation builds upon the preliminary interfaces added in Stage 4.3.
- See [Dual-Window Integration Report](../../components/dual-window-integration-report.md) for detailed implementation guidance.
