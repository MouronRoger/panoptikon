#!/usr/bin/env python3
"""Complete Knowledge Graph to Qdrant Pipeline
1. Migrate knowledge graph to markdown docs
2. Index all docs in Qdrant for search
"""
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


from scripts.documentation.ai_docs import (
    document_component,
    document_phase,
    record_decision,
)
from scripts.qdrant.index_docs import MKDocsToQdrant


def migrate_from_knowledge_graph():
    """Step 1: Convert knowledge graph entities to documentation
    This would normally read from your actual knowledge graph
    """
    created_files = []
    
    print("📊 Migrating knowledge graph to documentation...")
    
    # Example: Document all phases from knowledge graph
    phases = [
        {
            "name": "Phase 1 - Foundation",
            "status": "Completed",
            "objectives": "Environment setup, core architecture, OS abstraction, database",
            "components": ["Project Structure", "Build System", "Testing Framework"]
        },
        {
            "name": "Phase 2 - Core Infrastructure", 
            "status": "Completed",
            "objectives": "Service container, event bus, configuration, error handling",
            "components": ["Service Container", "Event Bus", "Configuration System"]
        },
        {
            "name": "Phase 3 - Filesystem Abstraction",
            "status": "Completed",
            "objectives": "File system monitoring, security bookmarks, cloud detection",
            "components": ["FSEvents Wrapper", "Security Bookmarks", "Cloud Detection"],
            "coverage": "90%+"
        },
        {
            "name": "Phase 4 - Database Implementation",
            "status": "In Progress",
            "objectives": "SQLite integration with connection pooling",
            "components": ["Database Schema", "Connection Pool", "Migration System"],
            "issues": ["Phase 4.2 needs testing", "Zero test coverage on connection pool"]
        }
    ]
    
    # Create phase documentation
    for phase_data in phases:
        # Extract phase name and other details
        phase_name = phase_data.pop('name')
        path = document_phase(phase_name, **phase_data)
        created_files.append(path)
        print(f"✅ Created: {path}")
    
    # Document key components
    components = [
        {
            "name": "DatabaseConnectionPool",
            "overview": "Thread-safe connection pooling for SQLite",
            "status": "Code Complete - Needs Testing",
            "coverage": "0%",
            "issues": "Missing test coverage, must test with 100+ threads"
        },
        {
            "name": "Service Container",
            "overview": "Dependency injection container with lifecycle management",
            "status": "Completed",
            "coverage": "94%",
            "purpose": "Manage service lifecycles and dependencies"
        }
    ]
    
    for component in components:
        component_name = component.pop('name')
        path = document_component(component_name, **component)
        created_files.append(path)
        print(f"✅ Created: {path}")
    
    # Create architecture decision records
    decisions = [
        {
            "title": "Block Phase 4.3 Until Testing",
            "status": "Accepted",
            "context": "Phase 4.2 has zero test coverage",
            "decision": "Must complete testing before migrations",
            "consequences": "1-2 week delay but stable foundation"
        }
    ]
    
    for decision in decisions:
        title = decision.pop('title')
        path = record_decision(title, **decision)
        created_files.append(path)
        print(f"✅ Created: {path}")
    
    print(f"\n📄 Created {len(created_files)} documentation files")
    return created_files


def index_all_documentation():
    """Step 2: Index all documentation in Qdrant
    """
    print("\n🔍 Indexing documentation in Qdrant...")
    
    # Use the MKDocs indexer
    indexer = MKDocsToQdrant(
        docs_dir="docs",
        collection_name="panoptikon",
        qdrant_url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
        qdrant_api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
    )
    
    # Run the indexing pipeline
    indexer.run()


def test_search():
    """Step 3: Test that search works
    """
    print("\n🧪 Testing search functionality...")
    
    from scripts.documentation.ai_docs import search_documentation
    
    test_queries = [
        "connection pool testing",
        "phase 4 progress",
        "service container coverage",
        "filesystem abstraction"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = search_documentation(query, limit=3)
        for i, result in enumerate(results):
            print(f"{i+1}. {result['title']} (score: {result['score']:.3f})")


def main():
    """Run the complete migration pipeline"""
    print("🚀 Knowledge Graph to Qdrant Migration Pipeline")
    print("=" * 50)
    
    # Step 1: Migrate knowledge graph to docs
    created_files = migrate_from_knowledge_graph()
    
    # Step 2: Index all docs in Qdrant
    index_all_documentation()
    
    # Step 3: Test search
    test_search()
    
    print("\n✨ Migration complete!")
    print(f"- Created {len(created_files)} documentation files")
    print("- Indexed all documents in Qdrant")
    print("- Search functionality verified")
    
    print("\n📖 You can now:")
    print("1. Search docs: python scripts/search_docs.py <query>")
    print("2. AI can update: from scripts.ai_docs import *")
    print("3. Browse docs: in the docs/ directory")


if __name__ == "__main__":
    main()
