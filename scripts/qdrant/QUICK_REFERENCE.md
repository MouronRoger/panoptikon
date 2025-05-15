# Qdrant Quick Reference

## Essential Commands

```bash
# Index documentation (MCP-compatible, cloud only)
./qdrant.sh index

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

Use `./qdrant.sh index` for MCP-compatible indexing.

## Troubleshooting

1. **MCP search failing**: Make sure you have indexed with the MCP-compatible script
2. **Zero results**: Check collection has data with the MCP test script
3. **Vector mismatch**: Only use the MCP-compatible indexer
