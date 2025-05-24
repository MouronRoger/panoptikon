# 🚧 V6.2-STAGE 5 — SEARCH ENGINE

# 📌 ROLE DEFINITION
**YOU ARE A DETERMINISTIC EXECUTOR.** Follow this process *exactly as written*. Execute one stage at a time, in strict order. **NO STAGE MAY BE SKIPPED OR REORDERED.** Each stage consists of multiple segments, each with its own testing boundary. **NO SEGMENT MAY PROCEED UNTIL ALL TESTS PASS.**
Each stage requires three persistent artifacts:
* stage5_report.md (Markdown report)
* stage5_prompt.md (Prompt artifact)
* mCP update (knowledge graph entry) — see **System Memory Update** below

# 🔄 TERMINOLOGY & HIERARCHY
* **Development Phase**: Infrastructure Phase (spans multiple stages)
* **Stage**: Primary implementation unit - SEARCH ENGINE
* **Segment**: Atomic, testable component within a stage
* **Testing Cycle**: Write tests → Implement → Test → Refine until passing

⚖️ CONSTRAINTS:
* Each segment must be testable independently
* Segment scope must fit within Claude 3.7's processing capacity in Cursor
* Documentation and memory must be updated after each segment and stage
* Tests must be written before (or alongside) implementation

# #️⃣ STAGE 5 — SEARCH ENGINE
### 1. LOAD STAGE SPEC
* 📄 From: stage5_prompt.md
* 🔍 Infrastructure Phase - Search Engine Component

### 2. ANALYZE CONTEXT
* 🔍 Identify:
  * Stage objectives: Implement high-performance filename search engine
  * Interfaces: Query processing, search algorithm, result management
  * Constraints: Performance optimization, thread safety, incremental delivery
  * Dependencies: Stage 2 service container, Stage 3 path management, Stage 4 database access
* ✅ Query mCP to validate prerequisites
* ⚠️ Flag any missing dependencies

### 3. STAGE SEGMENTATION
* 📋 Break down stage into distinct segments:
  * Segment 5.1: Query Parser
  * Segment 5.2: Search Algorithm
  * Segment 5.3: Result Management
  * Segment 5.4: Sorting System
  * Segment 5.5: Filtering System
* 📊 Define clear testing criteria for each segment
* 🔄 Document segment dependencies

### 4. IMPLEMENT AND TEST BY SEGMENT
**SEGMENT 5.1: Query Parser**
* 📝 **Test-First**: Write tests for filename pattern parsing, wildcard support, query optimization, and search operators
* 🛠️ **Implement**: 
  - Implement filename pattern parsing
  - Create wildcard and glob support
  - Build query optimization
  - Support advanced search operators
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 5.2: Search Algorithm**
* 📝 **Test-First**: Write tests for search performance, index-based search, memory-efficiency, and caching
* 🛠️ **Implement**: 
  - Build optimized search implementation
  - Create index-based search for performance
  - Implement memory-efficient matching
  - Design caching for frequent searches
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 5.3: Result Management**
* 📝 **Test-First**: Write tests for result collection, virtual paging, caching, and grouping
* 🛠️ **Implement**: 
  - Create result collection and organization
  - Implement virtual result paging
  - Build result caching and invalidation
  - Support result annotation and grouping
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 5.4: Sorting System**
* 📝 **Test-First**: Write tests for result sorting, multi-key sort, sort direction, and custom sort functions
* 🛠️ **Implement**: 
  - Implement flexible result sorting
  - Create multi-key sort support
  - Build sort direction control
  - Support custom sort functions
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

**SEGMENT 5.5: Filtering System**
* 📝 **Test-First**: Write tests for filter framework, file type filters, date range filtering, and filter chains
* 🛠️ **Implement**: 
  - Build filter application framework
  - Implement file type and attribute filters
  - Create date range filtering
  - Support custom filter chains
* ✅ **Verify**: Run segment-specific tests
* 🔄 **Refine**: Fix implementation until all tests pass
* 🚫 **HALT** if any tests fail after refinement attempts
* 📝 Document completion in mCP via document_component()

### 5. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests:
  - Verify search completes in <50ms for 10k test files
  - Test query parser with various pattern types
  - Validate result accuracy across search terms
  - Measure search performance with benchmarks
  - Verify filtering correctly reduces result sets
  - Test sorting with various criteria
  - Maintain 95% code coverage
* ✅ Apply linter and formatter
* ❌ Do not alter tests to force pass
* 🔄 Fix implementation if integration tests fail

### 6. PROPAGATE STATE
* 📝 Write stage5_report.md
* 📦 Save stage5_prompt.md
* 🔁 Update system memory (mCP) with full stage status via update_phase_progress()
* 📊 Document using AI Documentation System

# 📑 SYSTEM MEMORY UPDATE (mCP)
All memory updates are managed through the mCP knowledge graph. After each segment and stage:
* **Segment Completion**: 
```python
document_component(
  name="Query Parser",  # or other segment name
  overview="Implementation of search query parsing with pattern support",
  purpose="To transform user search queries into optimized search patterns",
  implementation="Includes pattern parsing, wildcard support, query optimization, and advanced operators",
  status="Completed",
  coverage="95%"
)
```

* **Stage Completion**: 
```python
update_phase_progress(
  phase="Infrastructure Phase",
  status="In Progress",
  completed=["Query Parser", "Search Algorithm", "Result Management", "Sorting System", "Filtering System"],
  issues=["Any issues encountered"],
  next=["Stage 6: Indexing System"]
)
```

* **Decision Records** (if applicable): 
```python
record_decision(
  title="Search Algorithm Pattern Matching Approach",
  status="Accepted",
  context="Need efficient pattern matching for filenames",
  decision="Implemented regex-based matching with precompiled patterns and caching",
  consequences="Better performance but increased memory usage during search",
  alternatives=["String matching", "Naive implementation"]
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
