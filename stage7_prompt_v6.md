# 🚧 V6.2-STAGE 7 — UI FRAMEWORK

# 📌 ROLE DEFINITION
**YOU ARE A DETERMINISTIC EXECUTOR.** Follow this process *exactly as written*. Execute one stage at a time, in strict order. **NO STAGE MAY BE SKIPPED OR REORDERED.** Each stage consists of multiple segments, each with its own testing boundary. **NO SEGMENT MAY PROCEED UNTIL ALL TESTS PASS.**
Each stage requires three persistent artifacts:
* stage7_report.md (Markdown report)
* stage7_prompt.md (Prompt artifact)
* mCP update (knowledge graph entry) — see **System Memory Update** below

# 🔄 TERMINOLOGY & HIERARCHY
* **Development Phase**: UI Phase (spans multiple stages)
* **Stage**: Primary implementation unit - UI FRAMEWORK
* **Segment**: Atomic, testable component within a stage
* **Testing Cycle**: Write tests → Implement → Test → Refine until passing

⚖️ CONSTRAINTS:
* Each segment must be testable independently
* Segment scope must fit within Claude 3.7's processing capacity in Cursor
* Documentation and memory must be updated after each segment and stage
* Tests must be written before (or alongside) implementation

# #️⃣ STAGE 7 — UI FRAMEWORK
### 1. LOAD STAGE SPEC
* 📄 From: stage7_prompt.md
* 🔍 UI Phase - UI Framework Component

### 2. ANALYZE CONTEXT
* 🔍 Identify:
  * Stage objectives: Implement native macOS UI with AppKit via PyObjC, dual-paradigm interface, dual-window support
  * Interfaces: Window controls, interaction model, UI components, UI-core integration
  * Constraints: Use composition over inheritance, clear separation of concerns, support equal keyboard and mouse workflows
  * Dependencies: Stage 2 service container, Stage 2 event bus, Stage 4 database access, Stage 5 search engine, Stage 6 indexing system
* ✅ Query mCP to validate prerequisites
* ⚠️ Flag any missing dependencies

### 3. STAGE SEGMENTATION
* 📋 Break down stage into distinct segments:
  * Segment 7.1: Window and Controls
  * Segment 7.2: Dual-Window Support
  * Segment 7.3: Interaction Model
  * Segment 7.4: UI Component Abstraction
  * Segment 7.5: Progress and Feedback
  * Segment 7.6: UI-Core Integration
  * Segment 7.7: Folder Size Display in UI
* 📊 Define clear testing criteria for each segment
* 🔄 Document segment dependencies

### 4. IMPLEMENT AND TEST BY SEGMENT
**SEGMENT 7.1: Window and Controls**
* 📝 **Test-First**: Write tests for window implementation, search input, tab bar, virtual table view, and column management
* 🛠️ **Implement**: 
  - Implement main application window
  - Create search input with real-time filtering
  - Build tab bar for category filtering
  - Implement virtual table view for results
  - Create column management system
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 7.2: Dual-Window Support**
* 📝 **Test-First**: Write tests for window management, window state, toggle functionality, positioning, and cross-window operations
* 🛠️ **Implement**: 
  - Implement DualWindowManager service
  - Create WindowState for window-specific state management
  - Build window toggle functionality (button and Cmd+N shortcut)
  - Implement smart window positioning algorithm
  - Create active/inactive window visual states
  - Enable cross-window drag-and-drop operations
  - Implement resource management for active/inactive windows
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 7.3: Interaction Model**
* 📝 **Test-First**: Write tests for keyboard navigation, context menus, drag and drop, selection management, and default actions
* 🛠️ **Implement**: 
  - Implement comprehensive keyboard navigation
  - Create context menus for operations
  - Build drag and drop support
  - Implement selection management
  - Design default file actions
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 7.4: UI Component Abstraction**
* 📝 **Test-First**: Write tests for composition pattern, UI-logic separation, accessibility, and layout adaptation
* 🛠️ **Implement**: 
  - Implement composition pattern for UI
  - Create separation between UI and business logic
  - Build accessibility support for VoiceOver
  - Design layout adaptation for screen densities
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 7.5: Progress and Feedback**
* 📝 **Test-First**: Write tests for progress visualization, status bar, tooltips, error notifications, and animations
* 🛠️ **Implement**: 
  - Create non-intrusive progress visualization
  - Implement status bar for information
  - Add contextual tooltips
  - Build user-friendly error notifications
  - Create smooth animations and transitions
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 7.6: UI-Core Integration**
* 📝 **Test-First**: Write tests for search integration, result binding, operation delegation, and state synchronization
* 🛠️ **Implement**: 
  - Implement search integration
  - Create result display binding
  - Build operation delegation
  - Design state synchronization
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 7.7: Folder Size Display in UI**
* 📝 **Test-First**: Write tests for folder size column, size formatting, and sorting functionality
* 🛠️ **Implement**: 
  - Add "Folder Size" column to the results table for directories
  - Format folder sizes in human-readable units (KB/MB/GB)
  - Enable sorting by folder size in the UI
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

### 5. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests:
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
  - Test folder size display and sorting
* ✅ Apply linter and formatter
* ❌ Do not alter tests to force pass
* 🔄 Fix implementation if integration tests fail

### 6. PROPAGATE STATE
* 📝 Write stage7_report.md
* 📦 Save stage7_prompt.md
* 🔁 Update system memory (mCP) with full stage status via update_phase_progress()
* 📊 Document using AI Documentation System

# 📑 SYSTEM MEMORY UPDATE (mCP)
All memory updates are managed through the mCP knowledge graph. After each segment and stage:
* **Segment Completion**: 
```python
document_component(
  name="Dual-Window Support",  # or other segment name
  overview="Implementation of dual-window management with active/inactive states",
  purpose="To provide a unique selling point feature allowing independent search contexts and cross-window operations",
  implementation="Includes DualWindowManager service, window state management, toggle functionality, window positioning, and cross-window drag-and-drop",
  status="Completed",
  coverage="98%"
)
```

* **Stage Completion**: 
```python
update_phase_progress(
  phase="UI Phase",
  status="In Progress",
  completed=["Window and Controls", "Dual-Window Support", "Interaction Model", 
             "UI Component Abstraction", "Progress and Feedback", "UI-Core Integration", 
             "Folder Size Display in UI"],
  issues=["Any issues encountered"],
  next=["Stage 8: Cloud Integration"]
)
```

* **Decision Records** (if applicable): 
```python
record_decision(
  title="Dual-Window Resource Management Strategy",
  status="Accepted",
  context="Need to manage resources efficiently between active and inactive windows",
  decision="Implemented resource throttling with visual state differentiation (color vs. grayscale)",
  consequences="Better performance with clear UX indication of active window, at cost of some UI complexity",
  alternatives=["Equal resource allocation", "Window minimization"]
)
```

Each call automatically syncs with the MCP server (Qdrant cloud). Do not bypass or duplicate memory operations.

# 🔁 TEST-IMPLEMENT-VERIFY CYCLE
Each segment follows a strict development cycle:
### ┌───────────────┐
### │ 1. WRITE TESTS│◄─────────────┐
### └───────┬───────┘              │
###         ▼                      │
### ┌───────────────┐              │
### │2. IMPLEMENT   │              │
### └───────┬───────┘              │
###         ▼                      │
### ┌───────────────┐              │
### │3. RUN TESTS   │──┐           │
### └───────────────┘  │           │
###                    ▼           │
###            ┌─── Tests pass? ───┐
###            │                   │
###            No                 Yes
###            │                   │
###            ▼                   │
### ┌───────────────┐     ┌────────────────┐
### │4. FIX CODE    │     │5. DOCUMENT     │
### └───────┬───────┘     │  & PROCEED     │
###         │             └────────────────┘
###         └─────────────┘
**IMPORTANT**: This cycle applies both within segments and between segments.

# 🚨 GLOBAL RULES — APPLY AT ALL TIMES
### 🔒 1. ZERO LINT ERRORS BEFORE PROCEEDING
### 🔒 2. NO MODIFICATION OF TESTS TO FORCE PASS
### 🔒 3. STRICT ADHERENCE TO ARCHITECTURE & SPECS
### 🔒 4. EXPLICIT DEPENDENCY VERIFICATION AT EVERY SEGMENT BOUNDARY
### 🔒 5. TEST-FIRST DEVELOPMENT AT ALL STAGES
### 🔒 6. DOCUMENTATION & MEMORY UPDATED AFTER EACH SEGMENT
### 🔒 7. CONTINUOUS mCP STATE SYNCHRONIZATION
### 🔒 8. FOLLOW STAGE-SEGMENT IMPLEMENTATION ORDER EXACTLY
### 🔒 9. NEVER PROCEED WITH FAILING TESTS
