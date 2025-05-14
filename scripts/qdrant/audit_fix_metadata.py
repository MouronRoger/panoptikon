#!/usr/bin/env python3
"""Audit and fix missing metadata in Qdrant 'panoptikon' collection.
- Checks for missing 'title', 'path', or 'document' fields in each point.
- Attempts to fix by re-parsing the corresponding markdown file in docs/.
- Updates the point in Qdrant if fixable; logs a warning if not.
- Prints a summary of fixes and unresolved issues.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Set

import frontmatter  # type: ignore[import-untyped]
from qdrant_client import QdrantClient
from qdrant_client.models import PointIdsList, PointStruct

QDRANT_URL = (
    "https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io"
)
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
COLLECTION_NAME = "panoptikon"
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

REQUIRED_FIELDS = ["title", "path", "document"]


def get_all_points(client: QdrantClient) -> List[Any]:
    """Fetch all points from the Qdrant collection."""
    offset = None
    all_points = []
    while True:
        points, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            offset=offset,
            limit=100,
            with_payload=True,
            with_vectors=True,
        )
        all_points.extend(points)
        offset = next_offset
        if offset is None:
            break
    return all_points


def parse_markdown(md_path: Path) -> Optional[Dict[str, Any]]:
    """Parse a markdown file and return metadata/content dict."""
    if not md_path.exists():
        return None
    post = frontmatter.load(md_path)
    return {
        "title": post.get("title", md_path.stem.replace("-", " ").title()),
        "path": str(md_path.relative_to(DOCS_DIR)),
        "document": post.content[:500],
        "content": post.content[:500],
        "metadata": post.metadata,
    }


def fix_point(point: Any, docs_dir: Path) -> Optional[PointStruct]:
    """Attempt to fix missing fields in a Qdrant point by re-parsing the markdown file."""
    payload = point.payload
    rel_path = payload.get("path", "")
    md_path = docs_dir / rel_path
    # Skip if path is empty, missing, or not a file
    if not rel_path or not md_path.is_file():
        return None
    doc = parse_markdown(md_path)
    if doc is None:
        return None
    # Update payload with missing fields
    for field in REQUIRED_FIELDS:
        if field not in payload or not payload[field]:
            payload[field] = doc[field]
    # Always update 'metadata' if available
    payload["metadata"] = doc["metadata"]
    # Use the same vector as before
    vector = point.vector
    if hasattr(vector, "fast-all-minilm-l6-v2"):
        vector = vector.get("fast-all-minilm-l6-v2")
    return PointStruct(
        id=point.id,
        vector={"fast-all-minilm-l6-v2": vector}
        if isinstance(vector, list)
        else vector,
        payload=payload,
    )


def delete_points(client: QdrantClient, ids: Set[str]) -> None:
    """Delete points from Qdrant by ID."""
    if not ids:
        print("No points to delete.")
        return
    print(f"Deleting {len(ids)} unresolved points from Qdrant...")
    selector = PointIdsList(points=list(ids))
    client.delete(collection_name=COLLECTION_NAME, points_selector=selector)
    print(f"Deleted {len(ids)} points.")


def main(delete_unresolved: bool = False) -> None:
    """Audit and fix missing metadata in Qdrant. Optionally delete unresolved points."""
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print(f"Fetching all points from collection '{COLLECTION_NAME}'...")
    points = get_all_points(client)
    print(f"Found {len(points)} points.")
    to_fix = []
    unresolved = []
    unresolved_ids = set()
    for point in points:
        payload = point.payload
        missing = [f for f in REQUIRED_FIELDS if f not in payload or not payload[f]]
        if missing:
            fixed = fix_point(point, DOCS_DIR)
            if fixed:
                to_fix.append(fixed)
            else:
                unresolved.append(payload.get("path", f"ID {point.id}"))
                unresolved_ids.add(point.id)
    if to_fix:
        print(f"Fixing {len(to_fix)} points with missing metadata...")
        batch_size = 50
        for i in range(0, len(to_fix), batch_size):
            batch = to_fix[i : i + batch_size]
            client.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"Fixed {len(to_fix)} points.")
    else:
        print("No points needed fixing.")
    if unresolved:
        print("Unresolved points (missing markdown file):")
        for path in unresolved:
            print(f"- {path}")
        if delete_unresolved:
            delete_points(client, unresolved_ids)
        else:
            # Prompt user for deletion if running interactively
            if sys.stdin.isatty():
                resp = (
                    input("Delete unresolved points from Qdrant? [y/N]: ")
                    .strip()
                    .lower()
                )
                if resp == "y":
                    delete_points(client, unresolved_ids)
    else:
        print("All points are now MCP-compatible!")


if __name__ == "__main__":
    # Allow --delete-unresolved as a CLI flag
    delete_flag = "--delete-unresolved" in sys.argv
    main(delete_unresolved=delete_flag)
