# 🔄 STAGE 4.3: SCHEMA MIGRATION FRAMEWORK

## 📝 OBJECTIVES
- Build automated schema versioning system
- Implement forward migration execution
- Create backup and recovery mechanisms
- Support safe rollback capabilities

## 🔧 IMPLEMENTATION TASKS

### 1. Migration System Core 🎯
- **Version Tracking**: Schema version in database
- **Migration Registry**: Ordered migration list
- **Migration Executor**: Safe execution framework
- **Backup Manager**: Pre-migration backups

### 2. Migration Structure 📁
```python
# Migration format:
# - Version number (sequential)
# - Up migration SQL
# - Down migration SQL (optional)
# - Verification queries
# - Migration metadata
```

### 3. Safety Mechanisms 🛡️
1. Pre-migration backup creation
2. Transaction-wrapped migrations
3. Post-migration verification
4. Automatic rollback on failure
5. Migration lock to prevent concurrent runs

### 4. Recovery System 🚑
- **Backup Creation**: Full database backup before migration
- **Integrity Checks**: Verify database consistency
- **Recovery Process**: Restore from backup on failure
- **History Tracking**: Log all migration attempts

## 🧪 TESTING REQUIREMENTS
- Test sequential migration execution
- Verify rollback functionality
- Test recovery from failed migrations
- Validate backup creation and restoration
- Test migration locking mechanism
- Ensure idempotent migrations
- Test with corrupted migration states
- Maintain 95% code coverage

## 🎯 SUCCESS CRITERIA
- Zero data loss during migrations
- Migrations complete < 5 seconds for typical schemas
- Automatic recovery from failures
- Clear migration history tracking
- Support for both up and down migrations

## 🚫 CONSTRAINTS
- Migrations must be atomic (all-or-nothing)
- No external migration tools
- Compatible with SQLite transaction limitations
- Backup size must be manageable

## 📋 DEPENDENCIES
- Stage 4.1: Schema implementation (base schema)
- Stage 4.2: Connection pool (database access)
- Stage 2: Error handling (migration exceptions)
- Stage 2: Configuration (backup location)

## 🏗️ CODE STANDARDS
- **Migration Naming**: Sequential numbering (001_initial.py)
- **SQL Standards**: Consistent formatting, comments
- **Error Messages**: Clear migration failure reasons
- **Logging**: Detailed migration execution logs
- **Testing**: Test each migration independently
- **Documentation**: Migration purpose and impacts

## 📈 MIGRATION: SCHEMA VERSION 1.1.0 (FOLDER SIZE)

- **Purpose:** Add `folder_size` column to `files` table and index for folder size sorting (see Integration Report).
- **Status:** Migration completed and tested in Phase 4.3. See [Folder Size Implementation](../../components/folder-size-implementation.md) for details.
- **Migration Steps:**
    1. `ALTER TABLE files ADD COLUMN folder_size INTEGER;`
    2. `CREATE INDEX IF NOT EXISTS idx_files_folder_size ON files(folder_size);`
    3. `UPDATE schema_version SET version = '1.1.0', updated_at = <now>;`
- **Idempotency:** Migration should be safe to run once and not break if run again.
- **Version Tracking:** Only run if current version < 1.1.0.
- **Dependency:** This migration is required before implementing folder size calculation (Stage 6) and UI display (Stage 7).