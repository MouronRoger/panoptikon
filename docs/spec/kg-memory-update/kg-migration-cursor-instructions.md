# Knowledge Graph Migration - Execution Instructions for Claude

## Context
You're about to execute a knowledge graph migration for the Panoptikon project. The migration upgrades from a name-based system to a UUID-based, type-safe system with full validation. All code has been created and is Python 3.9 compatible (the project uses Python 3.9.18 with Pydantic 2.6.3).

## Pre-Execution Verification

First, verify the migration files exist:
```bash
cd /Users/james/Documents/GitHub/panoptikon/scripts/knowledge
ls -la *.py rebuild_graph.sh
```

You should see these files:
- `models.py` - Type-safe Pydantic models
- `relationship_extractor_typed.py` - Enhanced extractor with UUID support
- `memory_manager_typed.py` - Type-safe CLI wrapper
- `add_inverse_relations.py` - Bidirectional relationship generator
- `validate_graph.py` - Graph validation tool
- `graph_summary.py` - Statistics generator
- `rebuild_graph.sh` - Automated rebuild script

## Step 1: Make Scripts Executable

```bash
chmod +x *.py rebuild_graph.sh
```

## Step 2: Test the Typed Extractor (Dry Run)

Before running the full migration, test that the typed extractor works:

```bash
python relationship_extractor_typed.py --dry-run ../../docs/phases/*.md
```

Expected output:
- Should show `[DRY] Would add entity:` and `[DRY] Would add relation:` lines
- Should NOT show any Python errors or syntax issues
- If you see `ModuleNotFoundError`, ensure you're in the correct directory

## Step 3: Backup Existing Knowledge Graph (if any)

Check if there's an existing graph to backup:

```bash
MEMORY_PATH="/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
if [ -f "$MEMORY_PATH" ]; then
    cp "$MEMORY_PATH" "${MEMORY_PATH}.pre_migration_backup"
    echo "Backup created"
else
    echo "No existing graph found"
fi
```

## Step 4: Run the Full Migration

Execute the rebuild script:

```bash
./rebuild_graph.sh
```

### What This Does:
1. **Phase 1**: Backs up and clears existing graph
2. **Phase 2**: Extracts entities from all markdown documentation
3. **Phase 3**: Adds core system entities (Panoptikon, Search Engine, etc.)
4. **Phase 4**: Generates inverse relationships
5. **Phase 5**: Validates the graph for orphans and duplicates
6. **Phase 6**: Shows summary statistics

### Expected Output Structure:
```
=== Panoptikon Knowledge Graph Rebuild ===
[Phase 1] Backup and Clear
[Phase 2] Document Extraction
  Using typed extractor
  Processing: ../../docs/phases/phase-1-foundation.md
  [Add] Entity: phase 1 - foundation (Phase)
  ...
[Phase 3] Core Entity Addition
[Phase 4] Inverse Relations
[Phase 5] Validation
  Entities: XX
  Relations: XX
  ✅ All relationships valid
[Phase 6] Summary
  === Entity Summary ===
  ...
```

## Step 5: Verify Success

### Check Validation Passed:
```bash
python validate_graph.py
```
Should show "✅ All relationships valid"

### Review Summary:
```bash
python graph_summary.py
```
Should show entity counts by type and top connected entities.

### Spot Check Entities Have UUIDs:
```bash
python memory_manager_typed.py list-entities | head -5
```
Should show entities with UUID format like: `phase 1 - foundation (Phase) – 123e4567-e89b-12d3-a456-426614174000`

## Step 6: Handle Common Issues

### If "Module not found" errors:
```bash
# Ensure you're in the right directory
pwd  # Should be .../panoptikon/scripts/knowledge

# Check Python path is set correctly
python -c "import sys; print(sys.path)"
```

### If validation shows orphaned relationships:
This means a relationship points to a non-existent entity. Either:
1. The entity documentation is missing
2. There's a typo in the relationship section

Check which entities are orphaned and either fix the source markdown or add the missing entity.

### If you see duplicate entities:
The new system prevents future duplicates, but existing ones need manual cleanup:
```bash
# See which entities are duplicated
python validate_graph.py

# You'll need to manually edit the JSONL file to remove duplicates
# Or re-run the migration after fixing source documentation
```

## Step 7: Optional - Sync to Qdrant

If prompted, you can sync to Qdrant (answer 'N' for now unless specifically requested):
```
Sync to Qdrant? (y/N) N
```

## Success Indicators

The migration is successful when:
1. ✅ Validation passes with no orphaned relationships
2. ✅ All entities have UUID identifiers
3. ✅ Summary shows reasonable counts for each entity type
4. ✅ No Python errors during execution

## Post-Migration

The knowledge graph now has:
- **UUID-based entities** preventing duplicates (e.g., "UI Framework" and "ui framework" are the same)
- **Bidirectional relationships** (if A belongs_to B, then B contains A)
- **Type safety** with Pydantic models
- **Validation tools** to maintain integrity

## For CI/CD

The system is now ready for automated rebuilds. The GitHub Actions workflow will run on:
- Any push to `docs/**/*.md` or `scripts/knowledge/**`
- Weekly on Sundays
- Manual workflow dispatch

## Technical Notes

- Uses deterministic UUID5: `uuid5(NAMESPACE_DNS, "EntityType:normalized_name")`
- Name normalization: lowercase with collapsed whitespace
- Backward compatible with legacy name-based entries
- All operations are idempotent (safe to re-run)

If you encounter any issues not covered here, check the Python version (should be 3.9.18) and Pydantic version (should be 2.6.3).

Good luck with the migration! 🚀