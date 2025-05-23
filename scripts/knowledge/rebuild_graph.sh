#!/bin/bash
# CI-friendly automated knowledge graph rebuild script

set -e  # Exit on error

echo "=== Panoptikon Knowledge Graph Rebuild ==="
echo "Started at: $(date)"

# Configuration
MEMORY_PATH="/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$(cd "$SCRIPTS_DIR/../../docs" && pwd)"

# Parse arguments
AUTO_SYNC="${AUTO_SYNC:-false}"
SKIP_VALIDATION="${SKIP_VALIDATION:-false}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-sync)
            AUTO_SYNC="true"
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION="true"
            shift
            ;;
        --help)
            echo "Usage: $0 [--auto-sync] [--skip-validation]"
            echo "  --auto-sync       Automatically sync to Qdrant without prompting"
            echo "  --skip-validation Skip validation phase"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Phase 1: Backup and Clear
echo -e "\n[Phase 1] Backup and Clear"
if [ -f "$MEMORY_PATH" ]; then
    BACKUP_PATH="${MEMORY_PATH%.jsonl}_backup_$(date +%Y%m%d_%H%M%S).jsonl"
    cp "$MEMORY_PATH" "$BACKUP_PATH"
    echo "  Backup created: $BACKUP_PATH"
fi
echo "" > "$MEMORY_PATH"
echo "  Knowledge graph cleared"

# Phase 2: Extract from Documentation
echo -e "\n[Phase 2] Document Extraction"

# Check for typed extractor, fall back to original
EXTRACTOR="$SCRIPTS_DIR/relationship_extractor.py"
if python -c "import scripts.knowledge.models" 2>/dev/null && [ -f "$SCRIPTS_DIR/relationship_extractor_typed.py" ]; then
    EXTRACTOR="$SCRIPTS_DIR/relationship_extractor_typed.py"
    echo "  Using typed extractor"
else
    echo "  Using original extractor"
fi

# Extract phases
echo "  Extracting Phase entities..."
find "$DOCS_DIR/phases" -name "*.md" -type f | sort | while read -r file; do
    python "$EXTRACTOR" "$file"
done

# Extract components
echo "  Extracting Component entities..."
find "$DOCS_DIR/components" -name "*.md" -type f | sort | while read -r file; do
    python "$EXTRACTOR" "$file"
done

# Extract decisions (if directory exists)
if [ -d "$DOCS_DIR/decisions" ]; then
    echo "  Extracting Decision entities..."
    find "$DOCS_DIR/decisions" -name "*.md" -type f | sort | while read -r file; do
        python "$EXTRACTOR" "$file"
    done
fi

# Phase 3: Add Core Entities
echo -e "\n[Phase 3] Core Entity Addition"

# Check for typed memory manager, fall back to original
MEMORY_MANAGER="$SCRIPTS_DIR/memory_manager.py"
if [ -f "$SCRIPTS_DIR/memory_manager_typed.py" ]; then
    MEMORY_MANAGER="$SCRIPTS_DIR/memory_manager_typed.py"
    echo "  Using typed memory manager"
fi

python "$MEMORY_MANAGER" add-entity "Panoptikon" "System" \
    --observation "High-performance macOS filename search utility"

python "$MEMORY_MANAGER" add-entity "Search Engine" "Component" \
    --observation "Core search functionality implementation"

python "$MEMORY_MANAGER" add-entity "Indexing System" "Component" \
    --observation "File system scanning and database population"

python "$MEMORY_MANAGER" add-entity "UI Framework" "Component" \
    --observation "Native macOS user interface implementation"

# Add core relationships
python "$MEMORY_MANAGER" add-relation "Search Engine" "Panoptikon" "belongs_to"
python "$MEMORY_MANAGER" add-relation "Indexing System" "Panoptikon" "belongs_to"
python "$MEMORY_MANAGER" add-relation "UI Framework" "Panoptikon" "belongs_to"

# Phase 4: Add Inverse Relations
echo -e "\n[Phase 4] Inverse Relations"
if [ -f "$SCRIPTS_DIR/add_inverse_relations.py" ]; then
    python "$SCRIPTS_DIR/add_inverse_relations.py"
else
    echo "  [Info] Inverse relations script not found, skipping"
fi

# Phase 5: Validation (unless skipped)
if [ "$SKIP_VALIDATION" != "true" ]; then
    echo -e "\n[Phase 5] Validation"
    if [ -f "$SCRIPTS_DIR/validate_graph.py" ]; then
        python "$SCRIPTS_DIR/validate_graph.py" || {
            echo "  [Error] Validation failed"
            exit 1
        }
    else
        echo "  [Warn] validate_graph.py not found"
    fi
else
    echo -e "\n[Phase 5] Validation - SKIPPED"
fi

# Phase 6: Summary
echo -e "\n[Phase 6] Summary"
if [ -f "$SCRIPTS_DIR/graph_summary.py" ]; then
    python "$SCRIPTS_DIR/graph_summary.py"
else
    echo "  [Warn] graph_summary.py not found"
fi

# Optional: Sync to Qdrant
if [ -f "$SCRIPTS_DIR/../dual_reindex.py" ]; then
    if [ "$AUTO_SYNC" == "true" ]; then
        echo -e "\n[Phase 7] Qdrant Sync"
        python "$SCRIPTS_DIR/../dual_reindex.py"
    elif [ -t 0 ]; then  # Only prompt if interactive terminal
        read -p "Sync to Qdrant? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Running dual_reindex.py..."
            python "$SCRIPTS_DIR/../dual_reindex.py"
        fi
    else
        echo -e "\n[Phase 7] Qdrant Sync - Skipped (non-interactive)"
    fi
fi

echo -e "\n=== Rebuild Complete ==="
echo "Finished at: $(date)"
exit 0
