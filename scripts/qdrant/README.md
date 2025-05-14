# Qdrant Integration Scripts

This directory contains all scripts for managing the Qdrant vector database integration for the Panoptikon project.

## Scripts

- `index_docs.py` - Indexes markdown documentation from `/docs` into Qdrant
- `index_docs_mcp.py` - MCP-compatible version with named vectors
- `search_docs.py` - Search the indexed documentation
- `manage.py` - Manage the Qdrant collection (info, clear, recreate, list)
- `test_mcp.py` - Test MCP (Model Context Protocol) integration
- `qdrant.sh` - Convenience wrapper for all operations

## Usage

### Using the wrapper script:

```bash
# Make the script executable (first time only)
chmod +x qdrant.sh

# Index all documentation
./qdrant.sh index

# Index with MCP-compatible named vectors
./qdrant.sh index --mcp

# Search documentation
./qdrant.sh search "connection pool"

# Manage collection
./qdrant.sh manage info
./qdrant.sh manage clear
./qdrant.sh manage recreate
./qdrant.sh manage list

# Test MCP integration
./qdrant.sh test
```

### Direct usage:

```bash
# Index documentation
python index_docs.py

# Search
python search_docs.py "your search query"

# Manage collection
python manage.py info --url $QDRANT_URL --api-key $QDRANT_API_KEY
python manage.py clear --url $QDRANT_URL --api-key $QDRANT_API_KEY

# Test MCP
python test_mcp.py
```

## Configuration

All scripts are configured to use:
- Collection name: `panoptikon`
- Vector model: `all-MiniLM-L6-v2` (384 dimensions)
- Vector name: `fast-all-minilm-l6-v2` (for MCP compatibility)
- Cloud instance: Configured with URL and API key

## MCP Integration

The scripts are designed to work with the MCP server that expects:
- Collection: `panoptikon`
- Named vectors: `fast-all-minilm-l6-v2`
- 384-dimensional embeddings

To verify MCP compatibility, run:
```bash
./qdrant.sh test
```
