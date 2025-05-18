# 🚧 STAGE 9: SYSTEM INTEGRATION

## 📝 OBJECTIVES
- Implement system-wide activation with global hotkey
- Create menu bar integration with status item
- Build dock icon behavior and integration
- Develop permissions management and guidance
- Implement Finder integration
- Enhance dual-window support with system integration

## 🔧 IMPLEMENTATION TASKS

1. **Global Hotkey**:
   - Implement system-wide activation hotkey
   - Create fallback mechanisms for different permission levels
   - Build customizable shortcut configuration
   - Design activation animation and feedback

2. **Menu Bar Icon**:
   - Create status item with menu
   - Implement quick actions
   - Build status visualization
   - Support alternative activation path

3. **Dock Integration**:
   - Build proper dock icon behavior
   - Implement badge notifications
   - Create dock menu with actions
   - Support drag and drop to dock icon

4. **Permissions Management**:
   - Create Full Disk Access guidance
   - Implement permission detection
   - Build progressive permission requests
   - Design permission-aware operation routing

5. **Finder Integration**:
   - Implement reveal in Finder function
   - Create file selection preservation
   - Build contextual operations with Finder
   - Support drag and drop between applications

6. **Dual-Window System Enhancement**:
   - Add window toggle to menu bar icon menu
   - Implement window toggle keyboard shortcut (Cmd+N)
   - Create window positioning for multi-monitor setups
   - Build window state persistence between app launches
   - Support drag-and-drop between Finder and both windows

## 🧪 TESTING REQUIREMENTS
- Verify hotkey works reliably
- Test with different permission levels
- Validate menu bar functions correctly
- Measure dock integration behavior
- Verify permissions guidance helps users
- Test Finder integration across operations
- Maintain graceful behavior with limited permissions
- Validate dual-window operations across monitors
- Test window toggle from system menu and keyboard shortcut

## 🚫 CONSTRAINTS
- Design for resilience against system service failures
- Support fallback mechanisms for each integration
- Maintain functionality with minimal permissions
- Handle system service variations gracefully
- Preserve binary window model (main + secondary)
- Ensure cross-window operations work reliably with system integration

## 📋 DEPENDENCIES
- Stage 2 service container
- Stage 3 filesystem operations
- Stage 3 permission bookmarks
- Stage 7 UI framework
- Stage 7 dual-window implementation
