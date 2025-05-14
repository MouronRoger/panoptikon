#!/bin/bash
# Qdrant utilities wrapper script

# Cloud credentials
export QDRANT_URL="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io"
export QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Parse command
case "$1" in
    index)
        echo "Indexing documentation to Qdrant..."
        echo "Use --mcp flag for MCP-compatible indexing with named vectors"
        if [ "$2" = "--mcp" ]; then
            python "$SCRIPT_DIR/index_docs_mcp.py"
        else
            python "$SCRIPT_DIR/index_docs.py"
        fi
        ;;
    search)
        shift
        python "$SCRIPT_DIR/search_docs.py" "$@"
        ;;
    manage)
        shift
        python "$SCRIPT_DIR/manage.py" "$@" --url "$QDRANT_URL" --api-key "$QDRANT_API_KEY"
        ;;
    test)
        echo "Testing MCP integration..."
        python "$SCRIPT_DIR/test_mcp.py"
        ;;
    *)
        echo "Usage: $0 {index|search|manage|test}"
        echo ""
        echo "Commands:"
        echo "  index           - Index all documentation to Qdrant"
        echo "  search <query>  - Search documentation"
        echo "  manage <cmd>    - Manage collection (info|clear|recreate|list)"
        echo "  test           - Test MCP integration"
        exit 1
        ;;
esac
