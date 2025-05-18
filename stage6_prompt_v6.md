# 🚧 V6.2-STAGE 6 — INDEXING SYSTEM

# 📌 ROLE DEFINITION
**YOU ARE A DETERMINISTIC EXECUTOR.** Follow this process *exactly as written*. Execute one stage at a time, in strict order. **NO STAGE MAY BE SKIPPED OR REORDERED.** Each stage consists of multiple segments, each with its own testing boundary. **NO SEGMENT MAY PROCEED UNTIL ALL TESTS PASS.**
Each stage requires three persistent artifacts:
* stage6_report.md (Markdown report)
* stage6_prompt.md (Prompt artifact)
* mCP update (knowledge graph entry) — see **System Memory Update** below

# 🔄 TERMINOLOGY & HIERARCHY
* **Development Phase**: Infrastructure Phase (spans multiple stages)
* **Stage**: Primary implementation unit - INDEXING SYSTEM
* **Segment**: Atomic, testable component within a stage
* **Testing Cycle**: Write tests → Implement → Test → Refine until passing

⚖️ CONSTRAINTS:
* Each segment must be testable independently
* Segment scope must fit within Claude 3.7's processing capacity in Cursor
* Documentation and memory must be updated after each segment and stage
* Tests must be written before (or alongside) implementation

# #️⃣ STAGE 6 — INDEXING SYSTEM
### 1. LOAD STAGE SPEC
* 📄 From: stage6_prompt.md
* 🔍 Infrastructure Phase - Indexing System Component

### 2. ANALYZE CONTEXT
* 🔍 Identify:
  * Stage objectives: Implement file system scanning and indexing with metadata extraction
  * Interfaces: Scanner, metadata extraction, incremental updates, priority management
  * Constraints: Low system impact, background operation, incremental progress persistence
  * Dependencies: Stage 2 service container, Stage 2 event bus, Stage 3 filesystem operations, Stage 3 FSEvents wrapper, Stage 4 database schema
* ✅ Query mCP to validate prerequisites
* ⚠️ Flag any missing dependencies

### 3. STAGE SEGMENTATION
* 📋 Break down stage into distinct segments:
  * Segment 6.1: Initial Scanner
  * Segment 6.2: Metadata Extraction
  * Segment 6.3: Incremental Updates
  * Segment 6.4: Priority Management
  * Segment 6.5: Progress Tracking
  * Segment 6.6: Folder Size Calculation
* 📊 Define clear testing criteria for each segment
* 🔄 Document segment dependencies

### 4. IMPLEMENT AND TEST BY SEGMENT
**SEGMENT 6.1: Initial Scanner**
* 📝 **Test-First**: Write tests for directory scanning, path rule evaluation, batch processing, and throttling
* 🛠️ **Implement**: 
  - Build recursive directory scanning
  - Implement path rule evaluation during scan
  - Create batch processing for efficiency
  - Design throttling for system impact
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 6.2: Metadata Extraction**
* 📝 **Test-First**: Write tests for file metadata extraction, file type identification, attribute harvesting, and cloud metadata handling
* 🛠️ **Implement**: 
  - Implement file metadata extraction
  - Create file type identification
  - Build attribute harvesting
  - Support cloud metadata handling
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 6.3: Incremental Updates**
* 📝 **Test-First**: Write tests for change-based updates, event-driven indexing, diff detection, and conflict resolution
* 🛠️ **Implement**: 
  - Implement change-based index updates
  - Create event-driven indexing
  - Build diff detection for efficient updates
  - Design conflict resolution
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 6.4: Priority Management**
* 📝 **Test-First**: Write tests for scanning prioritization, user focus areas, frequency-based prioritization, and manual overrides
* 🛠️ **Implement**: 
  - Build intelligent scanning prioritization
  - Implement user focus areas
  - Create frequency-based prioritization
  - Support manual priority overrides
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 6.5: Progress Tracking**
* 📝 **Test-First**: Write tests for progress monitoring, status reporting, ETA calculation, and cancellation/pausing
* 🛠️ **Implement**: 
  - Implement indexing progress monitoring
  - Create status reporting
  - Build ETA calculation
  - Support cancellation and pausing
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 6.6: Folder Size Calculation**
* 📝 **Test-First**: Write tests for recursive folder size calculation, incremental updates, and special case handling
* 🛠️ **Implement**: 
  - Implement recursive folder size calculation for all indexed directories
  - Store calculated folder sizes in the `folder_size` column
  - Update folder sizes incrementally as files change
  - Handle symlinks, hard links, and permission errors
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

### 5. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests:
  - Verify indexing processes >1000 files/second
  - Test incremental updates with various changes
  - Validate metadata extraction accuracy
  - Measure indexing performance with benchmarks
  - Verify prioritization correctly orders operations
  - Test progress tracking accuracy
  - Verify folder size calculation accuracy
  - Maintain 95% code coverage
* ✅ Apply linter and formatter
* ❌ Do not alter tests to force pass
* 🔄 Fix implementation if integration tests fail

### 6. PROPAGATE STATE
* 📝 Write stage6_report.md
* 📦 Save stage6_prompt.md
* 🔁 Update system memory (mCP) with full stage status via update_phase_progress()
* 📊 Document using AI Documentation System

# 📑 SYSTEM MEMORY UPDATE (mCP)
All memory updates are managed through the mCP knowledge graph. After each segment and stage:
* **Segment Completion**: 
```python
document_component(
  name="Initial Scanner",  # or other segment name
  overview="Implementation of recursive directory scanner with path rule evaluation",
  purpose="To efficiently traverse and index the filesystem with minimal system impact",
  implementation="Includes recursive scanning, rule evaluation, batch processing, and throttling",
  status="Completed",
  coverage="95%"
)
```

* **Stage Completion**: 
```python
update_phase_progress(
  phase="Infrastructure Phase",
  status="In Progress",
  completed=["Initial Scanner", "Metadata Extraction", "Incremental Updates", 
             "Priority Management", "Progress Tracking", "Folder Size Calculation"],
  issues=["Any issues encountered"],
  next=["Stage 7: UI Framework"]
)
```

* **Decision Records** (if applicable): 
```python
record_decision(
  title="Folder Size Calculation Strategy",
  status="Accepted",
  context="Need efficient and accurate folder size calculation",
  decision="Implemented incremental calculation with change-based updates",
  consequences="Instant folder size display at the cost of additional database storage",
  alternatives=["On-demand calculation", "Approximate sizing"]
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
