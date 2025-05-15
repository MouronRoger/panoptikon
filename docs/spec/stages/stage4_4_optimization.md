# ⚡ STAGE 4.4: QUERY OPTIMIZATION SYSTEM (V6 FORMAT)
# 📝 OBJECTIVES
* Implement prepared statement management
* Create query parameterization helpers
* Build query performance monitoring
* Establish statement caching system

⠀🔧 IMPLEMENTATION STRATEGY
### 1. LOAD STAGE SPEC
* 📄 From: stage4_4_optimization.md
* 🔍 This stage belongs to Development Phase 1: Foundation

⠀2. ANALYZE CONTEXT
* 🔍 Dependencies:
  * Stage 4.2: Connection pool (execution context)
  * Stage 4.1: Schema (query targets)
  * Stage 2: Logging system (performance logs)
  * Stage 2: Metrics collection (timing data)
* ✅ Query mCP to validate prerequisites are complete
* ⚠️ Flag any missing dependencies before proceeding

⠀3. STAGE SEGMENTATION
**SEGMENT 1: Prepared Statement Framework**
* **Implementation Tasks:**
  * Create StatementRegistry for centralized prepared statement management
  * Implement parameter binding system with type safety
  * Build statement caching mechanism with lifecycle management
  * Develop cleanup routines for statement finalization
* **Testing Criteria:**
  * Verify statements properly compile and execute
  * Test parameter binding with various data types
  * Measure statement cache hit rates
  * Validate proper cleanup of statements
* **Documentation Update:**
  * Record component implementation details
  * Document caching strategy decisions

⠀**SEGMENT 2: Query Builder Utilities**
* **Implementation Tasks:**
  * Create safe parameterization helpers
  * Implement SQL injection prevention
  * Build dynamic query composition tools
  * Create type-safe binding interface
* **Testing Criteria:**
  * Verify SQL injection prevention
  * Test dynamic query building
  * Validate parameter substitution
  * Check edge cases (NULL values, special characters)
* **Documentation Update:**
  * Document query builder API
  * Record any security decisions

⠀**SEGMENT 3: Performance Monitoring**
* **Implementation Tasks:**
  * Implement query execution timing
  * Create EXPLAIN QUERY PLAN analysis
  * Build index usage tracking
  * Develop slow query identification
  * Implement query frequency analysis
* **Testing Criteria:**
  * Verify timing accuracy
  * Test EXPLAIN plan parsing
  * Validate slow query detection
  * Check performance impact of monitoring
* **Documentation Update:**
  * Document monitoring configuration options
  * Record performance baseline metrics

⠀**SEGMENT 4: Optimization Strategies**
* **Implementation Tasks:**
  * Implement index hints for SQLite query planner
  * Create query rewriting for common patterns
  * Build batch operation support
  * Develop result caching strategy
* **Testing Criteria:**
  * Measure performance improvements with optimizations
  * Test batch operations vs. individual queries
  * Validate cache invalidation
  * Check optimization compatibility with transactions
* **Documentation Update:**
  * Document optimization strategies and when to use each
  * Record performance gains from optimizations

⠀4. STAGE INTEGRATION TEST
* ✅ Run full stage integration tests
* ✅ Apply linter and formatter
* ❌ Do not alter tests to match code
* ✅ Verify all success criteria:
  * Parameterized queries prevent SQL injection
  * Statement caching reduces parse time by 50%+
  * Query monitoring identifies slow queries
  * Batch operations 10x faster than individual operations
  * EXPLAIN analysis provides actionable insights

⠀5. PROPAGATE STATE
* 📝 Write stage4_4_report.md
* 📦 Save stage4_4_prompt.md
* 🔁 Update mCP with full stage status
* 📊 Document using AI Documentation System
