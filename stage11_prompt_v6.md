# 🚧 V6.2-STAGE 11 — PACKAGING AND RELEASE

# 📌 ROLE DEFINITION
**YOU ARE A DETERMINISTIC EXECUTOR.** Follow this process *exactly as written*. Execute one stage at a time, in strict order. **NO STAGE MAY BE SKIPPED OR REORDERED.** Each stage consists of multiple segments, each with its own testing boundary. **NO SEGMENT MAY PROCEED UNTIL ALL TESTS PASS.**
Each stage requires three persistent artifacts:
* stage11_report.md (Markdown report)
* stage11_prompt.md (Prompt artifact)
* mCP update (knowledge graph entry) — see **System Memory Update** below

# 🔄 TERMINOLOGY & HIERARCHY
* **Development Phase**: Release Phase (spans multiple stages)
* **Stage**: Primary implementation unit - PACKAGING AND RELEASE
* **Segment**: Atomic, testable component within a stage
* **Testing Cycle**: Write tests → Implement → Test → Refine until passing

⚖️ CONSTRAINTS:
* Each segment must be testable independently
* Segment scope must fit within Claude 3.7's processing capacity in Cursor
* Documentation and memory must be updated after each segment and stage
* Tests must be written before (or alongside) implementation

# #️⃣ STAGE 11 — PACKAGING AND RELEASE
### 1. LOAD STAGE SPEC
* 📄 From: stage11_prompt.md
* 🔍 Release Phase - Packaging and Release Component

### 2. ANALYZE CONTEXT
* 🔍 Identify:
  * Stage objectives: Create final application bundle, implement code signing, develop update system, complete documentation
  * Interfaces: Packaging, documentation, update system, website
  * Constraints: Code signing and notarization requirements, bundle size limits, secure updates
  * Dependencies: All previous stages completed and optimized
* ✅ Query mCP to validate prerequisites
* ⚠️ Flag any missing dependencies

### 3. STAGE SEGMENTATION
* 📋 Break down stage into distinct segments:
  * Segment 11.1: Final Packaging
  * Segment 11.2: Documentation
  * Segment 11.3: Update System
  * Segment 11.4: Website Preparation
  * Segment 11.5: Final Testing
* 📊 Define clear testing criteria for each segment
* 🔄 Document segment dependencies

### 4. IMPLEMENT AND TEST BY SEGMENT
**SEGMENT 11.1: Final Packaging**
* 📝 **Test-First**: Write tests for PyObjC bundling, binary compilation, app bundle creation, UPX compression, code signing, and notarization
* 🛠️ **Implement**: 
  - Finalize PyObjC + Python implementation
  - Bundle with py2app
  - Compile to self-contained binary using Nuitka
  - Create .app bundle structure
  - Optimize size with UPX compression
  - Sign application with developer ID
  - Submit for Apple notarization
  - Create DMG for distribution
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 11.2: Documentation**
* 📝 **Test-First**: Write tests for user guide completeness, release notes accuracy, limitations documentation, and technical documentation
* 🛠️ **Implement**: 
  - Create comprehensive user guide
  - Prepare detailed release notes
  - Document known limitations
  - Outline future roadmap
  - Finalize technical documentation
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 11.3: Update System**
* 📝 **Test-First**: Write tests for Sparkle integration, appcast XML creation, signature verification, update notifications, and update process
* 🛠️ **Implement**: 
  - Configure Sparkle for updates
  - Create appcast XML for version information
  - Implement signature verification
  - Build update notification system
  - Design seamless update process
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 11.4: Website Preparation**
* 📝 **Test-First**: Write tests for website information, download mechanism, support resources, and feature showcase
* 🛠️ **Implement**: 
  - Update website with release information
  - Create download mechanism
  - Prepare support resources
  - Design feature showcase
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 11.5: Final Testing**
* 📝 **Test-First**: Write tests for comprehensive verification, installation process, update system, documentation validation, and performance
* 🛠️ **Implement**: 
  - Complete comprehensive test pass
  - Verify installation process
  - Test update system
  - Validate documentation
  - Perform final performance verification
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

### 5. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests:
  - Verify installation works via drag-and-drop
  - Test application passes Gatekeeper validation
  - Validate update system correctly detects new versions
  - Measure final performance metrics
  - Verify all features function as expected
  - Test on all supported macOS versions
* ✅ Apply linter and formatter
* ❌ Do not alter tests to force pass
* 🔄 Fix implementation if integration tests fail

### 6. PROPAGATE STATE
* 📝 Write stage11_report.md
* 📦 Save stage11_prompt.md
* 🔁 Update system memory (mCP) with full stage status via update_phase_progress()
* 📊 Document using AI Documentation System

# 📑 SYSTEM MEMORY UPDATE (mCP)
All memory updates are managed through the mCP knowledge graph. After each segment and stage:
* **Segment Completion**: 
```python
document_component(
  name="Final Packaging",  # or other segment name
  overview="Implementation of application bundling, signing, and distribution package creation",
  purpose="To create a properly packaged, signed, and notarized application ready for distribution",
  implementation="Includes py2app bundling, Nuitka compilation, app bundle creation, UPX compression, code signing, notarization, and DMG creation",
  status="Completed",
  coverage="100%"
)
```

* **Stage Completion**: 
```python
update_phase_progress(
  phase="Release Phase",
  status="Completed",
  completed=["Final Packaging", "Documentation", "Update System", 
             "Website Preparation", "Final Testing"],
  issues=["Any issues encountered"],
  next=["Release to Production"]
)
```

* **Decision Records** (if applicable): 
```python
record_decision(
  title="Binary Packaging Strategy",
  status="Accepted",
  context="Need efficient and secure packaging that meets size constraints",
  decision="Implemented Nuitka compilation with UPX compression and proper code signing",
  consequences="Optimized bundle size and startup performance, with proper security validation",
  alternatives=["PyInstaller", "Pure py2app without Nuitka"]
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
