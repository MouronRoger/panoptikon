# Qdrant Integration Scripts

This directory contains all scripts for managing the Qdrant vector database integration for the Panoptikon project.

## Scripts

- `index_docs_mcp.py` - MCP-compatible indexing with named vectors (cloud only)
- `test_mcp.py` - Test MCP (Model Context Protocol) integration
- `qdrant.sh` - Convenience wrapper for all operations (MCP-compatible only)

## Usage

### Using the wrapper script:

```bash
# Make the script executable (first time only)
chmod +x qdrant.sh

# Index all documentation (MCP-compatible, cloud only)
./qdrant.sh index

# Test MCP integration
./qdrant.sh test
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
