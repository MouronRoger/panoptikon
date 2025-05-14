#!/usr/bin/env python3
"""
Search your MKDocs documentation using Qdrant
"""
import sys
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


class DocSearcher:
    def __init__(self, 
                 collection_name: str = "panoptikon",
                 qdrant_url: str = None,
                 qdrant_api_key: str = None):
        
        # Initialize embedding model (same as indexing)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Qdrant client
        if qdrant_url and qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.client = QdrantClient(host="localhost", port=6333)
        
        self.collection_name = collection_name
    
    def search(self, query: str, limit: int = 5):
        """Search for relevant documentation"""
        # Generate query embedding
        query_vector = self.model.encode(query).tolist()
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        # Display results
        print(f"\nSearch results for: '{query}'\n")
        for i, result in enumerate(results):
            print(f"{i+1}. {result.payload['title']}")
            print(f"   Path: {result.payload['path']}")
            print(f"   Score: {result.score:.3f}")
            print(f"   Preview: {result.payload['content'][:150]}...")
            print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python search_docs.py <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    searcher = DocSearcher(
        collection_name="panoptikon",
        qdrant_url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
        qdrant_api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
    )
    
    searcher.search(query)


if __name__ == "__main__":
    main()
