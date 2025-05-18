# 🚧 V6.2-STAGE 8 — CLOUD INTEGRATION

# 📌 ROLE DEFINITION
**YOU ARE A DETERMINISTIC EXECUTOR.** Follow this process *exactly as written*. Execute one stage at a time, in strict order. **NO STAGE MAY BE SKIPPED OR REORDERED.** Each stage consists of multiple segments, each with its own testing boundary. **NO SEGMENT MAY PROCEED UNTIL ALL TESTS PASS.**
Each stage requires three persistent artifacts:
* stage8_report.md (Markdown report)
* stage8_prompt.md (Prompt artifact)
* mCP update (knowledge graph entry) — see **System Memory Update** below

# 🔄 TERMINOLOGY & HIERARCHY
* **Development Phase**: Integration Phase (spans multiple stages)
* **Stage**: Primary implementation unit - CLOUD INTEGRATION
* **Segment**: Atomic, testable component within a stage
* **Testing Cycle**: Write tests → Implement → Test → Refine until passing

⚖️ CONSTRAINTS:
* Each segment must be testable independently
* Segment scope must fit within Claude 3.7's processing capacity in Cursor
* Documentation and memory must be updated after each segment and stage
* Tests must be written before (or alongside) implementation

# #️⃣ STAGE 8 — CLOUD INTEGRATION
### 1. LOAD STAGE SPEC
* 📄 From: stage8_prompt.md
* 🔍 Integration Phase - Cloud Integration Component

### 2. ANALYZE CONTEXT
* 🔍 Identify:
  * Stage objectives: Implement cloud provider integration with Finder delegation
  * Interfaces: Provider detection, status visualization, operation delegation, placeholder support
  * Constraints: Provider-agnostic where possible, offline functionality, consistent UX across providers
  * Dependencies: Stage 2 service container, Stage 3 filesystem operations, Stage 3 cloud detection, Stage 7 UI framework
* ✅ Query mCP to validate prerequisites
* ⚠️ Flag any missing dependencies

### 3. STAGE SEGMENTATION
* 📋 Break down stage into distinct segments:
  * Segment 8.1: Provider Detection
  * Segment 8.2: Status Visualization
  * Segment 8.3: Operation Delegation to System/Finder
  * Segment 8.4: Placeholder Support
  * Segment 8.5: Offline Handling
* 📊 Define clear testing criteria for each segment
* 🔄 Document segment dependencies

### 4. IMPLEMENT AND TEST BY SEGMENT
**SEGMENT 8.1: Provider Detection**
* 📝 **Test-First**: Write tests for cloud storage identification, provider-specific logic, path pattern recognition, and provider support
* 🛠️ **Implement**: 
  - Implement cloud storage identification
  - Create provider-specific detection logic
  - Build path pattern recognition
  - Support major providers (iCloud, Dropbox, OneDrive, Google Drive, Box)
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 8.2: Status Visualization**
* 📝 **Test-First**: Write tests for cloud file indicators, status monitoring, download progress, and offline indicators
* 🛠️ **Implement**: 
  - Create indicators for cloud files
  - Implement status change monitoring
  - Build download progress visualization
  - Design offline indicator system
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 8.3: Operation Delegation to System/Finder**
* 📝 **Test-First**: Write tests for system delegation layer, operation routing, fallback mechanisms, and provider-native operations
* 🛠️ **Implement**: 
  - Build system delegation layer using NSWorkspace
  - Implement operation routing that delegates cloud operations to Finder
  - Create fallback mechanisms (e.g., if NSWorkspace fails, use `open` command)
  - Support provider-native operations through system delegation
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 8.4: Placeholder Support**
* 📝 **Test-First**: Write tests for cloud-only file indicators, download triggering, metadata extraction, and operation queueing
* 🛠️ **Implement**: 
  - Implement cloud-only file indicators
  - Create on-demand download triggering
  - Build placeholder metadata extraction
  - Support operation queueing during download
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 8.5: Offline Handling**
* 📝 **Test-First**: Write tests for offline experience, operation queueing, reconnection synchronization, and offline indicators
* 🛠️ **Implement**: 
  - Create graceful offline experience
  - Implement cached operation queuing
  - Build synchronization on reconnection
  - Design offline mode indicators
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

### 5. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests:
  - Verify cloud files correctly identified
  - Test operations across providers
  - Validate placeholder handling
  - Measure performance with cloud-only files
  - Verify offline mode functions correctly
  - Test reconnection synchronization
  - Validate graceful degradation
* ✅ Apply linter and formatter
* ❌ Do not alter tests to force pass
* 🔄 Fix implementation if integration tests fail

### 6. PROPAGATE STATE
* 📝 Write stage8_report.md
* 📦 Save stage8_prompt.md
* 🔁 Update system memory (mCP) with full stage status via update_phase_progress()
* 📊 Document using AI Documentation System

# 📑 SYSTEM MEMORY UPDATE (mCP)
All memory updates are managed through the mCP knowledge graph. After each segment and stage:
* **Segment Completion**: 
```python
document_component(
  name="Operation Delegation to System/Finder",  # or other segment name
  overview="Implementation of cloud operation delegation to native system handlers",
  purpose="To leverage macOS native capabilities for cloud operations rather than implementing provider-specific APIs",
  implementation="Includes NSWorkspace delegation, operation routing, fallback mechanisms, and provider-native operations support",
  status="Completed",
  coverage="95%"
)
```

* **Stage Completion**: 
```python
update_phase_progress(
  phase="Integration Phase",
  status="In Progress",
  completed=["Provider Detection", "Status Visualization", "Operation Delegation to System/Finder", 
             "Placeholder Support", "Offline Handling"],
  issues=["Any issues encountered"],
  next=["Stage 9: System Integration"]
)
```

* **Decision Records** (if applicable): 
```python
record_decision(
  title="Cloud Operation Delegation Strategy",
  status="Accepted",
  context="Need to handle cloud provider operations without implementing provider-specific APIs",
  decision="Implemented full delegation to Finder/NSWorkspace for all cloud operations",
  consequences="Better reliability and future-proofing, at cost of less fine-grained control",
  alternatives=["Direct API implementation", "Hybrid approach"]
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
