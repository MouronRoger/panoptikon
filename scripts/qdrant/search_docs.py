#!/usr/bin/env python3
"""Search your MKDocs documentation using Qdrant."""

import sys
from typing import Optional

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class DocSearcher:
    """Semantic search for documentation in Qdrant."""

    def __init__(
        self,
        collection_name: str = "panoptikon",
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
    ) -> None:
        """Initialize the DocSearcher with Qdrant and embedding model."""
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        if qdrant_url and qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = collection_name

    def search(self, query: str, limit: int = 5) -> None:
        """Search for relevant documentation."""
        query_vector = self.model.encode(query).tolist()
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=(
                "fast-all-minilm-l6-v2",
                query_vector,
            ),
            limit=limit,
        )
        print(f"\nSearch results for: '{query}'\n")
        for i, result in enumerate(results):
            if result.payload is not None:
                print(f"{i + 1}. {result.payload.get('title', 'N/A')}")
                print(f"   Path: {result.payload.get('path', 'N/A')}")
                print(f"   Score: {result.score:.3f}")
                preview = result.payload.get("content", "")
                print(f"   Preview: {preview[:150]}...")
                print()
            else:
                print(f"{i + 1}. [No payload returned]")


def main() -> None:
    """Entry point for the Qdrant documentation search script."""
    if len(sys.argv) < 2:
        print("Usage: python search_docs.py <query>")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    searcher = DocSearcher(
        collection_name="panoptikon",
        qdrant_url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
        qdrant_api_key=(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0."
            "9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
        ),
    )
    searcher.search(query)


if __name__ == "__main__":
    main()
