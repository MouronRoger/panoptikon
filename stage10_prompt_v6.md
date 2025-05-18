# 🚧 V6.2-STAGE 10 — OPTIMIZATION

# 📌 ROLE DEFINITION
**YOU ARE A DETERMINISTIC EXECUTOR.** Follow this process *exactly as written*. Execute one stage at a time, in strict order. **NO STAGE MAY BE SKIPPED OR REORDERED.** Each stage consists of multiple segments, each with its own testing boundary. **NO SEGMENT MAY PROCEED UNTIL ALL TESTS PASS.**
Each stage requires three persistent artifacts:
* stage10_report.md (Markdown report)
* stage10_prompt.md (Prompt artifact)
* mCP update (knowledge graph entry) — see **System Memory Update** below

# 🔄 TERMINOLOGY & HIERARCHY
* **Development Phase**: Refinement Phase (spans multiple stages)
* **Stage**: Primary implementation unit - OPTIMIZATION
* **Segment**: Atomic, testable component within a stage
* **Testing Cycle**: Write tests → Implement → Test → Refine until passing

⚖️ CONSTRAINTS:
* Each segment must be testable independently
* Segment scope must fit within Claude 3.7's processing capacity in Cursor
* Documentation and memory must be updated after each segment and stage
* Tests must be written before (or alongside) implementation

# #️⃣ STAGE 10 — OPTIMIZATION
### 1. LOAD STAGE SPEC
* 📄 From: stage10_prompt.md
* 🔍 Refinement Phase - Optimization Component

### 2. ANALYZE CONTEXT
* 🔍 Identify:
  * Stage objectives: Fine-tune performance, optimize memory, verify resilience, refine UX, implement monitoring
  * Interfaces: Performance metrics, memory management, resilience mechanisms, UX components, monitoring systems
  * Constraints: Performance focus, accessibility compliance, minimal resource usage, battery efficiency
  * Dependencies: All previous stages
* ✅ Query mCP to validate prerequisites
* ⚠️ Flag any missing dependencies

### 3. STAGE SEGMENTATION
* 📋 Break down stage into distinct segments:
  * Segment 10.1: Performance Optimization
  * Segment 10.2: Memory Management
  * Segment 10.3: Resilience Verification
  * Segment 10.4: User Experience Refinement
  * Segment 10.5: Monitoring and Diagnostics
* 📊 Define clear testing criteria for each segment
* 🔄 Document segment dependencies

### 4. IMPLEMENT AND TEST BY SEGMENT
**SEGMENT 10.1: Performance Optimization**
* 📝 **Test-First**: Write tests for startup time, search latency, UI rendering, indexing speed, resource footprint, and window switching
* 🛠️ **Implement**: 
  - Fine-tune application startup to <100ms
  - Optimize search latency to consistently <50ms
  - Ensure UI renders at 60fps at all times
  - Improve indexing speed to handle 250k files in <60s
  - Minimize memory and CPU footprint
  - Optimize window switching performance to <100ms
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 10.2: Memory Management**
* 📝 **Test-First**: Write tests for memory leak detection, caching optimization, PyObjC boundary crossing, object ownership, and resource adjustment
* 🛠️ **Implement**: 
  - Profile and fix memory leaks
  - Optimize caching strategies
  - Improve PyObjC boundary crossing patterns
  - Ensure proper object ownership and thread confinement
  - Implement dynamic resource adjustment
  - Reduce inactive window memory usage to <10MB
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 10.3: Resilience Verification**
* 📝 **Test-First**: Write tests for file monitoring, permission behavior, cloud integration, component abstraction, and recovery mechanisms
* 🛠️ **Implement**: 
  - Test file monitoring across various scenarios
  - Validate behavior with different permission levels
  - Verify cloud integration across providers
  - Test component abstraction effectiveness
  - Enhance recovery mechanisms
  - Verify cross-window operations reliability
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 10.4: User Experience Refinement**
* 📝 **Test-First**: Write tests for first-run experience, help system, keyboard shortcuts, UI details, user guidance, and window states
* 🛠️ **Implement**: 
  - Create welcoming first-run experience
  - Implement contextual help system
  - Finalize keyboard shortcuts
  - Polish UI details and animations
  - Add subtle user guidance
  - Refine active/inactive window visual states
  - Enhance cross-window drag-and-drop feedback
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 10.5: Monitoring and Diagnostics**
* 📝 **Test-First**: Write tests for performance tracking, diagnostic logging, crash reporting, usage analytics, and troubleshooting tools
* 🛠️ **Implement**: 
  - Implement performance tracking
  - Create diagnostic logging
  - Build crash reporting mechanism
  - Design usage analytics (opt-in)
  - Develop troubleshooting tools
  - Add window state monitoring and metrics
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

### 5. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests:
  - Verify all performance targets consistently met:
    - Launch time <100ms
    - Search latency <50ms
    - UI rendering at 60fps
    - Indexing 250k files in <60s
    - Idle memory usage <50MB
    - Bundle size <30MB
    - Window switching <100ms
    - Inactive window memory <10MB
  - Test resilience under various conditions
  - Validate user experience with focus groups
  - Verify all features work on target OS versions
  - Validate cross-window operations in all scenarios
  - Test multi-monitor window arrangements
* ✅ Apply linter and formatter
* ❌ Do not alter tests to force pass
* 🔄 Fix implementation if integration tests fail

### 6. PROPAGATE STATE
* 📝 Write stage10_report.md
* 📦 Save stage10_prompt.md
* 🔁 Update system memory (mCP) with full stage status via update_phase_progress()
* 📊 Document using AI Documentation System

# 📑 SYSTEM MEMORY UPDATE (mCP)
All memory updates are managed through the mCP knowledge graph. After each segment and stage:
* **Segment Completion**: 
```python
document_component(
  name="Memory Management",  # or other segment name
  overview="Implementation of optimized memory management and leak prevention",
  purpose="To ensure minimal memory footprint and efficient resource usage across the application",
  implementation="Includes leak detection, caching optimization, PyObjC boundary improvements, object ownership, and inactive window optimization",
  status="Completed",
  coverage="97%"
)
```

* **Stage Completion**: 
```python
update_phase_progress(
  phase="Refinement Phase",
  status="In Progress",
  completed=["Performance Optimization", "Memory Management", "Resilience Verification", 
             "User Experience Refinement", "Monitoring and Diagnostics"],
  issues=["Any issues encountered"],
  next=["Stage 11: Packaging and Release"]
)
```

* **Decision Records** (if applicable): 
```python
record_decision(
  title="Performance Optimization Strategy",
  status="Accepted",
  context="Need to meet performance targets while maintaining reliability",
  decision="Implemented staged startup with priority-based resource allocation",
  consequences="Consistently fast startup and search at the cost of implementation complexity",
  alternatives=["On-demand loading", "Background indexing only"]
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
