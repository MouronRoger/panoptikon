# 🚧 V6.2-STAGE 9 — SYSTEM INTEGRATION

# 📌 ROLE DEFINITION
**YOU ARE A DETERMINISTIC EXECUTOR.** Follow this process *exactly as written*. Execute one stage at a time, in strict order. **NO STAGE MAY BE SKIPPED OR REORDERED.** Each stage consists of multiple segments, each with its own testing boundary. **NO SEGMENT MAY PROCEED UNTIL ALL TESTS PASS.**
Each stage requires three persistent artifacts:
* stage9_report.md (Markdown report)
* stage9_prompt.md (Prompt artifact)
* mCP update (knowledge graph entry) — see **System Memory Update** below

# 🔄 TERMINOLOGY & HIERARCHY
* **Development Phase**: Integration Phase (spans multiple stages)
* **Stage**: Primary implementation unit - SYSTEM INTEGRATION
* **Segment**: Atomic, testable component within a stage
* **Testing Cycle**: Write tests → Implement → Test → Refine until passing

⚖️ CONSTRAINTS:
* Each segment must be testable independently
* Segment scope must fit within Claude 3.7's processing capacity in Cursor
* Documentation and memory must be updated after each segment and stage
* Tests must be written before (or alongside) implementation

# #️⃣ STAGE 9 — SYSTEM INTEGRATION
### 1. LOAD STAGE SPEC
* 📄 From: stage9_prompt.md
* 🔍 Integration Phase - System Integration Component

### 2. ANALYZE CONTEXT
* 🔍 Identify:
  * Stage objectives: Implement system-wide activation, menu bar integration, dock integration, permissions, Finder integration
  * Interfaces: Global hotkey, menu bar, dock, permissions, Finder, dual-window system enhancement
  * Constraints: Resilience against system service failures, fallback mechanisms, minimal permissions functionality
  * Dependencies: Stage 2 service container, Stage 3 filesystem operations, Stage 3 permission bookmarks, Stage 7 UI framework, Stage 7 dual-window implementation
* ✅ Query mCP to validate prerequisites
* ⚠️ Flag any missing dependencies

### 3. STAGE SEGMENTATION
* 📋 Break down stage into distinct segments:
  * Segment 9.1: Global Hotkey
  * Segment 9.2: Menu Bar Icon
  * Segment 9.3: Dock Integration
  * Segment 9.4: Permissions Management
  * Segment 9.5: Finder Integration
  * Segment 9.6: Dual-Window System Enhancement
* 📊 Define clear testing criteria for each segment
* 🔄 Document segment dependencies

### 4. IMPLEMENT AND TEST BY SEGMENT
**SEGMENT 9.1: Global Hotkey**
* 📝 **Test-First**: Write tests for system-wide activation, fallback mechanisms, shortcut configuration, and activation feedback
* 🛠️ **Implement**: 
  - Implement system-wide activation hotkey
  - Create fallback mechanisms for different permission levels
  - Build customizable shortcut configuration
  - Design activation animation and feedback
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 9.2: Menu Bar Icon**
* 📝 **Test-First**: Write tests for status item creation, menu functionality, status visualization, and activation paths
* 🛠️ **Implement**: 
  - Create status item with menu
  - Implement quick actions
  - Build status visualization
  - Support alternative activation path
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 9.3: Dock Integration**
* 📝 **Test-First**: Write tests for dock icon behavior, badge notifications, dock menu, and drag-and-drop
* 🛠️ **Implement**: 
  - Build proper dock icon behavior
  - Implement badge notifications
  - Create dock menu with actions
  - Support drag and drop to dock icon
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 9.4: Permissions Management**
* 📝 **Test-First**: Write tests for FDA guidance, permission detection, progressive requests, and permission-aware routing
* 🛠️ **Implement**: 
  - Create Full Disk Access guidance
  - Implement permission detection
  - Build progressive permission requests
  - Design permission-aware operation routing
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 9.5: Finder Integration**
* 📝 **Test-First**: Write tests for reveal functionality, selection preservation, contextual operations, and drag-and-drop
* 🛠️ **Implement**: 
  - Implement reveal in Finder function
  - Create file selection preservation
  - Build contextual operations with Finder
  - Support drag and drop between applications
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 9.6: Dual-Window System Enhancement**
* 📝 **Test-First**: Write tests for menu bar toggle, keyboard shortcut, window positioning, state persistence, and drag-and-drop
* 🛠️ **Implement**: 
  - Add window toggle to menu bar icon menu
  - Implement window toggle keyboard shortcut (Cmd+N)
  - Create window positioning for multi-monitor setups
  - Build window state persistence between app launches
  - Support drag-and-drop between Finder and both windows
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

### 5. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests:
  - Verify hotkey works reliably
  - Test with different permission levels
  - Validate menu bar functions correctly
  - Measure dock integration behavior
  - Verify permissions guidance helps users
  - Test Finder integration across operations
  - Maintain graceful behavior with limited permissions
  - Validate dual-window operations across monitors
  - Test window toggle from system menu and keyboard shortcut
* ✅ Apply linter and formatter
* ❌ Do not alter tests to force pass
* 🔄 Fix implementation if integration tests fail

### 6. PROPAGATE STATE
* 📝 Write stage9_report.md
* 📦 Save stage9_prompt.md
* 🔁 Update system memory (mCP) with full stage status via update_phase_progress()
* 📊 Document using AI Documentation System

# 📑 SYSTEM MEMORY UPDATE (mCP)
All memory updates are managed through the mCP knowledge graph. After each segment and stage:
* **Segment Completion**: 
```python
document_component(
  name="Dual-Window System Enhancement",  # or other segment name
  overview="Implementation of system-level integration for dual-window functionality",
  purpose="To enhance the dual-window feature with system-level integration and multi-monitor support",
  implementation="Includes menu bar toggle, keyboard shortcut, window positioning, state persistence, and enhanced drag-and-drop",
  status="Completed",
  coverage="96%"
)
```

* **Stage Completion**: 
```python
update_phase_progress(
  phase="Integration Phase",
  status="In Progress",
  completed=["Global Hotkey", "Menu Bar Icon", "Dock Integration", 
             "Permissions Management", "Finder Integration", "Dual-Window System Enhancement"],
  issues=["Any issues encountered"],
  next=["Stage 10: Optimization"]
)
```

* **Decision Records** (if applicable): 
```python
record_decision(
  title="Permission Management Strategy",
  status="Accepted",
  context="Need to handle different permission levels gracefully",
  decision="Implemented progressive permission model with graceful degradation",
  consequences="Application works at all permission levels with clear guidance for enhancing functionality",
  alternatives=["Binary permission model", "Mandatory FDA requirement"]
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
