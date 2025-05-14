# Multi-Window Implementation Specification

## 🎯 Core Requirements

### Purpose
Enable users to work with multiple Panoptikon windows for enhanced file management workflows, particularly drag-and-drop operations between different search contexts.

### Unique Selling Point (USP)
**Cross-window drag-and-drop** - Unlike Everything (which doesn't support this), Panoptikon enables dragging files between search windows, creating powerful workflows for file organization across different search contexts.

### Key Specifications
- **Window Creation**: Primary via interface button, keyboard shortcuts (Cmd+N) also supported
- **Initial Positioning**: New windows appear alongside existing window as dual-pane layout
- **Independence**: Windows can be moved freely across screens after creation
- **Resource Management**: Only one window is active at a time
- **Singleton Architecture**: Single instances of core services shared across windows
- **Primary Use Case**: Drag files from one window to folders displayed in another
- **No Position Persistence**: Fresh window arrangement on each app launch
- **No Creation Effects**: Simple appearance without animation or sound

## 🛠️ Proposed Solution Architecture

### 1. Window State Management

```
WindowState {
  - windowId: UUID
  - isActive: Boolean
  - searchQuery: String  // Always visible in search field
  - activeTab: TabIdentifier
  - selectedFiles: Array<FileReference>
  - scrollPosition: CGPoint
  - columnConfiguration: ColumnSettings
  - filterState: FilterConfiguration
}
```

**Implementation Strategy**:
- Maintain WindowState objects for all windows
- Persist search query in UI to maintain context
- Use NSWindowController pattern for window lifecycle
- Default positioning for new windows beside existing

### 2. Active Window Coordination

```
WindowManager (Singleton) {
  - activeWindow: WindowIdentifier
  - windows: Dictionary<WindowIdentifier, WindowState>
  - activateWindow(id: WindowIdentifier)
  - suspendWindow(id: WindowIdentifier)
  - coordinateDragOperation(source: WindowIdentifier, target: WindowIdentifier)
}
```

**Activation Triggers**:
- User clicks in window
- Drag operation initiated from window
- Window brought to foreground

### 3. Resource Management Strategy

**When Window Becomes Active**:
- Resume file system monitoring
- Refresh search results if needed
- Restore scroll position and selection

**When Window Becomes Inactive**:
- Pause file system event processing
- Cache current result set
- Suspend background operations
- Maintain UI responsiveness for drop targets

### 4. Drag-and-Drop Coordination

**Cross-Window Operations**:
1. Drag initiated from inactive window → activate source window
2. Track source window ID in drag session
3. Drop in target window → process through active window's services
4. Log transaction with source and target window context

## ⚠️ Potential Issues & Mitigation

### 1. State Synchronization
**Issue**: File system changes while window inactive  
**Mitigation**: 
- Mark inactive windows as "stale"
- Quick refresh on reactivation
- Visual indicator for outdated results

### 2. Resource Contention
**Issue**: Multiple windows competing for file handles/locks  
**Mitigation**:
- Centralized file operation queue
- Read operations can be concurrent
- Write operations serialize through active window

### 3. User Confusion
**Issue**: Which window is active may be unclear  
**Mitigation**:
- Active window displays with full color styling
- Inactive windows shift to monochrome/grayscale appearance
- Instant visual feedback on window activation
- No additional UI elements needed - the color state is the indicator

### 4. Memory Usage
**Issue**: Large result sets cached in inactive windows  
**Mitigation**:
- Implement result set size limits
- Lazy loading for cached results
- Periodic memory pressure cleanup

### 5. Window Proliferation
**Issue**: Users creating too many windows  
**Mitigation**:
- Soft limit (e.g., 5 windows) with warning
- Window management menu showing all windows
- "Close inactive windows" option

## 🎨 UI/UX Considerations

### Visual Design
- **Window Chrome**: Standard macOS window controls (close/minimize/maximize)
- **Distinct from Finder**: Custom appearance to create visual distance
- **Search Field**: Always displays current query for context
- **No Effects**: Simple window appearance without animations
- **Active/Inactive States**: 
  - Active window: Full color interface
  - Inactive windows: Monochrome/grayscale appearance
  - Immediate visual transition on focus change

### Window Positioning
- **Initial Layout**: New window appears beside existing (dual-pane style)
- **Smart Positioning**: 
  - If screen space permits: side-by-side
  - If not: cascade with offset
  - Multi-monitor aware
- **User Control**: Full freedom to reposition after creation

### Keyboard Support
- **Window Creation**: Cmd+N (standard macOS convention)
- **Window Switching**: Cmd+` (standard macOS window cycling)
- **Search Focus**: Cmd+F or auto-focus on type

## 📊 Implementation Stages

### Stage 1: Basic Multi-Window
- Window creation via button and Cmd+N
- Dual-pane positioning logic
- Independent search states
- Basic active/inactive management

### Stage 2: Drag-Drop Support
- Cross-window drag coordination
- Transaction tracking
- Drop target highlighting
- Multi-monitor awareness

### Stage 3: Resource Optimization
- Smart state caching
- Background operation suspension
- Memory management
- Performance monitoring

### Stage 4: Polish
- Visual state indicators
- Refined positioning algorithm
- Window management UI
- Performance optimizations

## 🏆 Success Criteria

1. **Performance**: Window switching < 100ms
2. **Memory**: Inactive windows use < 10MB cached state
3. **Reliability**: Zero data loss during cross-window operations
4. **Usability**: Clear active window indication
5. **Scalability**: Handles 5+ windows gracefully
6. **USP Delivery**: Seamless drag-drop between windows (not available in Everything)

## 🔄 Alternative Approaches Considered

### Rejected: True Multi-Instance
- **Why**: Complex singleton synchronization
- **Why**: Duplicate resource usage
- **Why**: Potential race conditions

### Rejected: Single Window with Tabs
- **Why**: Doesn't support drag between contexts
- **Why**: Less flexible workflow

### Rejected: Process-per-Window
- **Why**: IPC overhead
- **Why**: Complex state sharing
- **Why**: Higher memory footprint

## 📝 Open Questions

1. **Window Positioning Algorithm**: Exact offset for cascade when side-by-side isn't possible?
2. **Maximum Windows**: Hard limit or just performance warning?
3. **Visual Distinction**: Specific design elements to differentiate from Finder?
4. **Active Window Indicator**: Title bar highlight, border, or other method?
5. **Multi-Monitor Behavior**: Which screen gets new windows by default?