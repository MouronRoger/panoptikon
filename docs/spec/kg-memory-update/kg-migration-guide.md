# Panoptikon Knowledge Graph Migration Guide

## 🎯 Overview

This guide walks you through upgrading the Panoptikon knowledge graph from a simple name-based system to a professional, type-safe, ID-based system with full validation and CI/CD integration.

## 📋 Pre-Migration Checklist

Before starting, ensure you have:
- [ ] Python 3.11+ installed
- [ ] Access to `/Users/james/Documents/GitHub/panoptikon`
- [ ] Backup of any existing knowledge graph data
- [ ] About 30-45 minutes for the migration

## 🚀 Migration Steps

### Step 1: Create the Core Files (10 minutes)

First, create the essential new files in the knowledge scripts directory:

```bash
cd /Users/james/Documents/GitHub/panoptikon/scripts/knowledge
```

#### 1.1 Create `models.py`
This file defines the type-safe data structures for entities and relationships.

**What it does:**
- Defines `Entity` and `Relation` classes with Pydantic validation
- Normalizes names (lowercase, consistent spacing)
- Generates deterministic UUIDs for each entity
- Ensures "UI Framework" and "ui framework" are treated as the same entity

#### 1.2 Create `validate_graph.py`
A simple validator that checks your knowledge graph integrity.

**What it does:**
- Finds orphaned relationships (pointing to non-existent entities)
- Detects duplicate entity names
- Reports issues clearly

#### 1.3 Create `graph_summary.py`
Provides statistics about your knowledge graph.

**What it does:**
- Shows entity counts by type (Phase, Component, etc.)
- Lists relationship types and counts
- Displays the most connected entities

### Step 2: Add the Enhanced Tools (10 minutes)

#### 2.1 Create `relationship_extractor_typed.py`
An upgraded version of the extractor that uses the new type system.

**Key improvements:**
- Generates IDs for all entities
- Prevents duplicate entries
- Normalizes all names automatically
- Shows clear [Add]/[Skip] status for each operation

#### 2.2 Create `add_inverse_relations.py`
Automatically creates bidirectional relationships.

**What it does:**
- If A "belongs_to" B, it adds B "contains" A
- If A "depends_on" B, it adds B "used_by" A
- Makes the graph more navigable

#### 2.3 Create `memory_manager_typed.py` (Optional)
Type-safe version of the memory manager CLI.

**Benefits:**
- Uses the same ID generation as the extractor
- Ensures consistency across manual additions
- Better error handling

### Step 3: Update Configuration Files (5 minutes)

#### 3.1 Update `requirements.txt`
Add this line:
```
pydantic>=2.5.0
```

#### 3.2 Update `pyproject.toml`
Add the mypy, black, isort, and ruff configurations provided in the implementation files.

#### 3.3 Update `rebuild_graph.sh`
Replace with the new version that includes:
- `--auto-sync` flag for CI/CD
- `--skip-validation` flag for faster runs
- Automatic detection of typed vs legacy extractors

### Step 4: Run the Migration (10 minutes)

Now for the actual migration:

```bash
# 1. Make scripts executable
chmod +x *.py rebuild_graph.sh

# 2. Test the new extractor in dry-run mode
python relationship_extractor_typed.py --dry-run ../../docs/phases/*.md

# 3. If everything looks good, run the full rebuild
./rebuild_graph.sh
```

**What happens during rebuild:**
1. **Backup**: Creates timestamped backup of existing graph
2. **Clear**: Empties the current graph
3. **Extract**: Processes all markdown files in order:
   - Phase documentation first
   - Component documentation second
   - Decision documentation (if exists)
4. **Core Entities**: Adds system-level entities
5. **Inverse Relations**: Creates bidirectional links
6. **Validation**: Checks for issues
7. **Summary**: Shows statistics

### Step 5: Verify the Migration (5 minutes)

Check that everything worked:

```bash
# 1. Validate the graph
python validate_graph.py

# 2. View summary statistics
python graph_summary.py

# 3. Check a few entities have IDs
python memory_manager_typed.py list-entities | head -10
```

You should see:
- ✅ "All relationships valid"
- Entity counts for each type
- Entities with UUIDs like `[ID: 123e4567-e89b-12d3-a456-426614174000]`

### Step 6: Set Up Automation (5 minutes)

#### 6.1 Create GitHub Actions Workflow
Add `.github/workflows/knowledge-graph.yml` to automatically rebuild on documentation changes.

#### 6.2 Add Pre-commit Hook (Optional)
Update `.pre-commit-config.yaml` to extract relationships when markdown files change.

## 🔧 Troubleshooting

### Issue: "Module not found" errors
**Solution**: The typed scripts add the project root to Python path automatically. If issues persist, run from the project root.

### Issue: Validation shows orphaned relationships
**Solution**: This means a relationship points to a non-existent entity. Either:
- Create the missing entity documentation
- Remove the invalid relationship from the source markdown

### Issue: Duplicate entities after migration
**Solution**: The new system prevents future duplicates. For existing ones:
1. Identify duplicates with `validate_graph.py`
2. Manually remove from the JSONL file
3. Re-run the rebuild

## 🎉 Post-Migration Benefits

With the migration complete, you now have:

1. **Type Safety**: All entities have validated structure
2. **No Duplicates**: Case-insensitive matching prevents "UI Framework" vs "ui framework"
3. **Unique IDs**: Every entity has a deterministic UUID
4. **Bidirectional Relations**: Navigate the graph in both directions
5. **CI/CD Ready**: Automated rebuilds on documentation changes
6. **Professional Tooling**: Black, mypy, ruff for code quality

## 📊 What Changed

| Before | After |
|--------|-------|
| Name-based entities | UUID-based entities with normalized names |
| Manual duplicate checking | Automatic deduplication |
| One-way relationships | Bidirectional relationships |
| No validation | Comprehensive validation |
| Manual rebuilds | Automated CI/CD pipeline |
| Basic Python scripts | Type-safe, linted, production code |

## 🚦 Quick Commands Reference

```bash
# Full rebuild
./rebuild_graph.sh

# Rebuild without validation (faster)
./rebuild_graph.sh --skip-validation

# Rebuild with auto-sync to Qdrant
./rebuild_graph.sh --auto-sync

# Add a single entity
python memory_manager_typed.py add-entity "New Component" "Component"

# Add a relationship
python memory_manager_typed.py add-relation "New Component" "Panoptikon" "belongs_to"

# Check graph health
python validate_graph.py && python graph_summary.py
```

## ✅ Migration Complete!

Your knowledge graph is now:
- **Robust**: Handles edge cases and prevents data corruption
- **Scalable**: Ready for thousands of entities and relationships
- **Maintainable**: Clear code with type hints and validation
- **Automated**: Updates itself as documentation changes

The "Land Rover philosophy" in action - simple to use, robust in operation, perfectly fit for purpose!