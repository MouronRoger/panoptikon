# Qdrant Quick Reference

## Essential Commands

```bash
# Index documentation (standard)
./qdrant.sh index

# Index documentation (MCP-compatible with named vectors)
./qdrant.sh index --mcp

# Search
./qdrant.sh search "your query here"

# Check collection status
./qdrant.sh manage info

# Clear all data
./qdrant.sh manage clear

# Test MCP integration
./qdrant.sh test
```

## Collection Details

- **Name**: `panoptikon`
- **Cloud URL**: `https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io`
- **Vector Dimensions**: 384
- **Vector Model**: `all-MiniLM-L6-v2`
- **Vector Name** (for MCP): `fast-all-minilm-l6-v2`

## MCP Integration

The MCP server expects:
- Collection: `panoptikon`
- Named vectors: `fast-all-minilm-l6-v2`

Use `./qdrant.sh index --mcp` for MCP-compatible indexing.

## Troubleshooting

1. **MCP search failing**: Make sure to use `--mcp` flag when indexing
2. **Zero results**: Check collection has data with `./qdrant.sh manage info`
3. **Vector mismatch**: Use the MCP-compatible indexing script
