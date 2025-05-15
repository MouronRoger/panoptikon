#!/usr/bin/env python3
"""Test MCP-compatible Qdrant search
Verifies that documents are properly indexed for MCP access
"""
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


def test_mcp_search():
    # Initialize client
    client = QdrantClient(
        url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
    )
    
    # Check collection info
    collection = "panoptikon"
    try:
        info = client.get_collection(collection)
        print(f"Collection '{collection}' info:")
        print(f"  Points count: {info.points_count}")
        print(f"  Vector config: {info.config.params.vectors}")
        print()
    except Exception as e:
        print(f"Error getting collection info: {e}")
        return
    
    # Test search
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    test_queries = [
        "phase 4 connection pool testing",
        "database implementation",
        "service container",
        "filesystem abstraction"
    ]
    
    for query in test_queries:
        print(f"Testing query: '{query}'")
        
        # Generate embedding
        embedding = model.encode(query)
        
        try:
            # Search with named vector
            results = client.search(
                collection_name=collection,
                query_vector=("fast-all-minilm-l6-v2", embedding.tolist()),
                limit=3
            )
            
            if results:
                for i, result in enumerate(results):
                    print(f"  Result {i+1}:")
                    print(f"    Score: {result.score}")
                    print(f"    Title: {result.payload.get('title', 'N/A')}")
                    print(f"    Path: {result.payload.get('path', 'N/A')}")
                    print(f"    Preview: {result.payload.get('content', '')[:100]}...")
            else:
                print("  No results found")
        except Exception as e:
            print(f"  Search error: {e}")
        
        print()


if __name__ == "__main__":
    test_mcp_search()
