#!/usr/bin/env python3
"""One-time script to add 'document' field to existing points
"""
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from tqdm import tqdm

# Initialize client with your credentials
client = QdrantClient(
    url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
)

collection_name = "panoptikon"

print(f"Fetching all points from collection '{collection_name}'...")
offset = None
all_points = []

while True:
    points, next_offset = client.scroll(
        collection_name=collection_name,
        offset=offset,
        limit=100,
        with_payload=True,
        with_vectors=True
    )
    
    all_points.extend(points)
    offset = next_offset
    
    if offset is None:
        break

print(f"Found {len(all_points)} points to update")

# Update points with the 'document' field
print("\nUpdating points...")
updated_points = []

for point in tqdm(all_points):
    payload = point.payload
    
    # Add 'document' field with content from 'content' field
    if 'content' in payload and 'document' not in payload:
        payload['document'] = payload['content']
    
    # Create updated point - handle both dict and object vector formats
    vector = point.vector
    if hasattr(vector, 'fast-all-minilm-l6-v2'):
        # If vector is an object with named vectors
        vector = vector.get('fast-all-minilm-l6-v2')
    
    updated_point = PointStruct(
        id=point.id,
        vector={'fast-all-minilm-l6-v2': vector} if isinstance(vector, list) else vector,
        payload=payload
    )
    updated_points.append(updated_point)

# Batch update points
print("\nUploading updated points...")
batch_size = 50
for i in tqdm(range(0, len(updated_points), batch_size)):
    batch = updated_points[i:i + batch_size]
    client.upsert(
        collection_name=collection_name,
        points=batch
    )

print(f"\nSuccessfully updated {len(updated_points)} points!")

# Test the MCP connection
print("\nTesting with MCP...")
print("Please test the qdrant-find tool to see if it works now")
