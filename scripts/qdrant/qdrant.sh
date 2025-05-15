#!/bin/bash
# Qdrant utilities wrapper script (MCP-compatible only)

# Cloud credentials
export QDRANT_URL="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io"
export QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Parse command
case "$1" in
    index)
        echo "Indexing documentation to Qdrant (MCP-compatible only)..."
        python "$SCRIPT_DIR/index_docs_mcp.py"
        ;;
    test)
        echo "Testing MCP integration..."
        python "$SCRIPT_DIR/test_mcp.py"
        ;;
    *)
        echo "Usage: $0 {index|test}"
        echo ""
        echo "Commands:"
        echo "  index           - Index all documentation to Qdrant (MCP-compatible only)"
        echo "  test            - Test MCP integration"
        exit 1
        ;;
esac
