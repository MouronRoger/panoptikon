#!/usr/bin/env python3
"""
Qdrant collection management utility for Panoptikon project.
"""
import argparse
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


class QdrantManager:
    def __init__(self, url=None, api_key=None, host="localhost", port=6333, collection_name=None):
        if url and api_key:
            # Cloud instance
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            # Local instance
            self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name if collection_name else "panoptikon"
    
    def info(self):
        """Display collection information."""
        try:
            # First check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            print(f"Available collections: {collection_names}")
            
            if self.collection_name in collection_names:
                try:
                    info = self.client.get_collection(self.collection_name)
                    print(f"\nCollection: {self.collection_name}")
                    print(f"Points count: {info.points_count}")
                    print(f"Config: {info.config}")
                except Exception as validation_error:
                    print(f"\nCollection '{self.collection_name}' exists but encountered validation error:")
                    print(f"Error: {validation_error}")
                    print("\nTrying alternative approach...")
                    # Alternative: get basic info
                    try:
                        # Use raw API call to avoid Pydantic validation
                        response = self.client.count(collection_name=self.collection_name)
                        print(f"Points count: {response.count}")
                    except Exception as e:
                        print(f"Alternative approach failed: {e}")
            else:
                print(f"\nCollection '{self.collection_name}' does not exist.")
                print("Use 'recreate' command to create it.")
        except Exception as e:
            print(f"Error: {e}")
            # Different debug info for cloud vs local
            if hasattr(self.client, '_client'):
                client_type = type(self.client._client).__name__
                print(f"Client type: {client_type}")
                if hasattr(self.client._client, 'host'):
                    print(f"Connection: {self.client._client.host}:{self.client._client.port}")
                elif hasattr(self.client._client, '_base_url'):
                    print(f"Cloud URL: {self.client._client._base_url}")
    
    def clear(self):
        """Clear all points from collection."""
        try:
            from qdrant_client.models import FilterSelector, Filter
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=FilterSelector(filter=Filter())
            )
            print(f"Cleared all points from {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def recreate(self, vector_size=384):
        """Delete and recreate collection with fresh config."""
        try:
            # Delete if exists
            self.client.delete_collection(self.collection_name)
            print(f"Deleted collection {self.collection_name}")
        except:
            pass
        
        # Create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"Created collection {self.collection_name} with vector size {vector_size}")
    
    def list_points(self, limit=10):
        """List sample points from collection."""
        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit
            )
            print(f"Sample points (limit {limit}):")
            for point in results:
                print(f"ID: {point.id}, Payload: {point.payload}")
        except Exception as e:
            print(f"Error listing points: {e}")


def main():
    parser = argparse.ArgumentParser(description="Manage Qdrant collection for Panoptikon")
    parser.add_argument("command", choices=["info", "clear", "recreate", "list"],
                        help="Command to execute")
    parser.add_argument("--url", help="Qdrant Cloud URL")
    parser.add_argument("--api-key", help="Qdrant Cloud API key")
    parser.add_argument("--host", default="localhost", help="Qdrant host (for local)")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant port (for local)")
    parser.add_argument("--vector-size", type=int, default=384, 
                        help="Vector size for recreate command")
    
    args = parser.parse_args()
    
    manager = QdrantManager(url=args.url, api_key=args.api_key, 
                           host=args.host, port=args.port)
    
    if args.command == "info":
        manager.info()
    elif args.command == "clear":
        manager.clear()
    elif args.command == "recreate":
        manager.recreate(vector_size=args.vector_size)
    elif args.command == "list":
        manager.list_points()


if __name__ == "__main__":
    main()
