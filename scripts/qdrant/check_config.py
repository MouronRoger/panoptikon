#!/usr/bin/env python3
"""Check Qdrant collection configuration"""

from qdrant_client import QdrantClient

# Initialize client
client = QdrantClient(
    url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
)

try:
    info = client.get_collection("panoptikon")
    print("Collection configuration:")
    print(f"Vectors config: {info.config.params.vectors}")
    print(f"Points count: {info.points_count}")
except Exception as e:
    print(f"Error: {e}")
