#!/usr/bin/env python3
"""Dual re-indexing script for Panoptikon documentation:
- Indexes all markdown docs in Qdrant (semantic search)
- Exports all docs as JSON-LD nodes for knowledge graph ingestion
"""

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

import frontmatter  # type: ignore[import-untyped]
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

QDRANT_URL = (
    "https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io"
)
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
COLLECTION_NAME = "panoptikon"
DOCS_DIR = Path(__file__).parent.parent / "docs"
KG_EXPORT_DIR = DOCS_DIR / "kg_export"


def ensure_qdrant_collection(client: QdrantClient) -> None:
    """Ensure the Qdrant collection exists."""
    try:
        client.get_collection(COLLECTION_NAME)
    except Exception:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"Created Qdrant collection: {COLLECTION_NAME}")


def scan_markdown_docs(docs_dir: Path) -> list[Path]:
    """Recursively find all markdown files in docs_dir."""
    return [p for p in docs_dir.rglob("*.md") if not p.name.startswith(".")]


def index_in_qdrant(
    docs: list[dict[str, Any]], client: QdrantClient, model: SentenceTransformer
) -> None:
    """Index all docs in Qdrant."""
    points = []
    for doc in docs:
        embedding = model.encode(doc["content"])
        doc_id = hashlib.md5(f"{doc['path']}-0".encode()).hexdigest()
        point = PointStruct(
            id=doc_id,
            vector={"fast-all-minilm-l6-v2": embedding.tolist()},
            payload={
                "path": doc["path"],
                "title": doc["title"],
                "document": doc["content"],
                "content": doc["content"][:500],
                "metadata": doc["metadata"],
                **{
                    k: v
                    for k, v in doc["metadata"].items()
                    if k in ["status", "superseded_by"]
                },
            },
        )
        points.append(point)
        if len(points) >= 100:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f"Indexed {len(points)} docs in Qdrant (batch)")
            points = []
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Indexed {len(points)} docs in Qdrant (final batch)")


def export_jsonld(docs: list[dict[str, Any]], export_dir: Path) -> None:
    """Export all docs as JSON-LD nodes for the knowledge graph."""
    export_dir.mkdir(parents=True, exist_ok=True)
    nodes = []
    for doc in docs:
        node = {
            "@context": "https://schema.org/",
            "@type": "CreativeWork",
            "name": doc["title"],
            "identifier": doc["path"],
            "text": doc["content"],
            "status": doc["metadata"].get("status", "active"),
            "supersededBy": doc["metadata"].get("superseded_by"),
            "inCategory": doc["metadata"].get("category"),
            "dateModified": doc["metadata"].get("updated"),
            "dateCreated": doc["metadata"].get("created"),
            "crossReferences": doc["metadata"].get("cross_references", []),
        }
        nodes.append(node)
    export_path = export_dir / "kg_nodes.jsonld"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2)
    print(f"Exported {len(nodes)} docs as JSON-LD to {export_path}")


def parse_markdown_doc(md_path: Path) -> dict[str, Any]:
    """Parse a markdown file into a doc dict."""
    post = frontmatter.load(md_path)
    return {
        "path": str(md_path.relative_to(DOCS_DIR)),
        "title": post.get("title", md_path.stem.replace("-", " ").title()),
        "content": post.content,
        "metadata": post.metadata,
    }


def main() -> None:
    """Dual re-index all markdown docs into Qdrant and export as JSON-LD for KG."""
    print(f"Scanning markdown docs in {DOCS_DIR}")
    md_files = scan_markdown_docs(DOCS_DIR)
    print(f"Found {len(md_files)} markdown files")
    docs = [parse_markdown_doc(md) for md in md_files]
    print(f"Parsed {len(docs)} docs")

    print("Connecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("Connected to Qdrant.")

    ensure_qdrant_collection(client)
    print("Ensured Qdrant collection exists.")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model loaded.")

    print("Indexing in Qdrant...")
    index_in_qdrant(docs, client, model)
    print("Qdrant indexing complete.")

    print("Exporting to JSON-LD for knowledge graph...")
    export_jsonld(docs, KG_EXPORT_DIR)
    print("KG export complete.")

    # Automatically sync to MCP KG server memory file
    mcp_memory_path = Path(
        "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
    )
    kg_jsonld_path = KG_EXPORT_DIR / "kg_nodes.jsonld"
    try:
        shutil.copyfile(kg_jsonld_path, mcp_memory_path)
        print(f"Synced {kg_jsonld_path} to MCP KG server at {mcp_memory_path}")
    except Exception as e:
        print(f"Failed to sync KG export to MCP memory file: {e}")

    # Reconcile formats: convert JSON-LD to MCP NDJSON
    try:
        with open(kg_jsonld_path, encoding="utf-8") as f:
            nodes = json.load(f)
        with open(mcp_memory_path, "w", encoding="utf-8") as out:
            for node in nodes:
                entity = {
                    "type": "entity",
                    "name": node.get("name"),
                    "entityType": node.get("@type", "CreativeWork"),
                    "observations": [node.get("text", "")],
                }
                out.write(json.dumps(entity) + "\n")
        print(f"Reconciled and wrote MCP NDJSON format to {mcp_memory_path}")
    except Exception as e:
        print(f"Failed to reconcile and write MCP NDJSON format: {e}")

    # Cross-reference summary
    cross_refs = [
        (doc["title"], doc["metadata"].get("superseded_by"))
        for doc in docs
        if doc["metadata"].get("superseded_by")
    ]
    if cross_refs:
        print("Cross-references (superseded_by):")
        for title, ref in cross_refs:
            print(f"- {title} superseded by {ref}")
    else:
        print("No cross-references found.")

    print("Dual re-indexing complete.")


if __name__ == "__main__":
    main()
