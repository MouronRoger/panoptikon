#!/usr/bin/env python3
"""Unified Documentation System for Panoptikon
Provides both AI and manual documentation management
"""
from pathlib import Path
import subprocess
import sys


def run_command(cmd, description):
    """Run a command with nice output"""
    print(f"\n🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ {description} complete!")
    return True


def main():
    """Documentation management CLI"""
    if len(sys.argv) < 2:
        print("📚 Panoptikon Documentation System")
        print("=" * 35)
        print("\nUsage: python docs.py <command>")
        print("\nCommands:")
        print("  index    - Index all documentation in Qdrant")
        print("  search   - Search documentation")
        print("  migrate  - Migrate knowledge graph to docs")
        print("  status   - Check documentation status")
        print("  help     - Show this help message")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "index":
        print("📚 Indexing documentation...")
        # Use MCP-compatible indexing by default
        run_command("python scripts/qdrant/index_docs_mcp.py", "Indexing documents (MCP-compatible)")
        
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            print("Usage: python docs.py search <query>")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        print(f"🔍 Searching for: {query}")
        run_command(f"python scripts/qdrant/search_docs.py '{query}'", "Searching")
        
    elif command == "migrate":
        print("🔄 Migrating knowledge graph to documentation...")
        run_command("python scripts/documentation/migrate_complete.py", "Migration")
        
    elif command == "status":
        print("📊 Documentation Status")
        run_command("python scripts/qdrant/manage.py info --url $QDRANT_URL --api-key $QDRANT_API_KEY", "Checking Qdrant status")
        
        # Check docs directory
        docs_path = Path("docs")
        if docs_path.exists():
            categories = list(docs_path.iterdir())
            print(f"\n📁 Documentation categories: {len(categories)}")
            for cat in categories:
                if cat.is_dir():
                    files = list(cat.glob("*.md"))
                    print(f"  - {cat.name}: {len(files)} files")
        
    elif command == "help":
        main()  # Show help again
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python docs.py help' for usage")
        sys.exit(1)


if __name__ == "__main__":
    # Set environment variables for Qdrant
    import os
    os.environ["QDRANT_URL"] = "https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io"
    os.environ["QDRANT_API_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
    
    main()
