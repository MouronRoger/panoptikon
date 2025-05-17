#!/usr/bin/env python3
"""Dual re-indexing script for Panoptikon documentation:
- Indexes all markdown docs in Qdrant (semantic search)
- Exports all docs as JSON-LD nodes for knowledge graph ingestion
"""

import hashlib
import json
import logging
from pathlib import Path
import shutil
from typing import Any, Dict, List

import frontmatter  # type: ignore[import-untyped]
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

QDRANT_URL: str = (
    "https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io"
)
QDRANT_API_KEY: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
)
COLLECTION_NAME: str = "panoptikon"
DOCS_DIR: Path = Path(__file__).parent.parent / "docs"
KG_EXPORT_DIR: Path = DOCS_DIR / "kg_export"


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


def ensure_qdrant_collection(client: QdrantClient) -> None:
    """Ensure the Qdrant collection exists."""
    try:
        client.get_collection(COLLECTION_NAME)
        logging.info(f"Qdrant collection '{COLLECTION_NAME}' exists.")
    except Exception as e:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        logging.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        logging.error(f"Exception during collection check: {e}")


def scan_markdown_docs(docs_dir: Path) -> List[Path]:
    """Recursively find all markdown files in docs_dir."""
    files: List[Path] = [
        p for p in docs_dir.rglob("*.md") if not p.name.startswith(".")
    ]
    logging.info(f"Scanned {len(files)} markdown files in {docs_dir}")
    return files


def index_in_qdrant(
    docs: List[Dict[str, Any]], client: QdrantClient, model: SentenceTransformer
) -> None:
    """Index all docs in Qdrant."""
    points: List[PointStruct] = []
    for doc in docs:
        try:
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
                logging.info(f"Indexed {len(points)} docs in Qdrant (batch)")
                points = []
        except Exception as e:
            logging.error(f"Failed to index doc {doc['path']}: {e}")
    if points:
        try:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            logging.info(f"Indexed {len(points)} docs in Qdrant (final batch)")
        except Exception as e:
            logging.error(f"Failed to index final batch: {e}")


def export_jsonld(docs: List[Dict[str, Any]], export_dir: Path) -> None:
    """Export all docs as JSON-LD nodes for the knowledge graph."""
    try:
        export_dir.mkdir(parents=True, exist_ok=True)
        nodes: List[Dict[str, Any]] = []
        for doc in docs:
            node: Dict[str, Any] = {
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
        logging.info(f"Exported {len(nodes)} docs as JSON-LD to {export_path}")
    except Exception as e:
        logging.error(f"Failed to export JSON-LD: {e}")


def parse_markdown_doc(md_path: Path) -> Dict[str, Any]:
    """Parse a markdown file into a doc dict."""
    try:
        post = frontmatter.load(md_path)
        return {
            "path": str(md_path.relative_to(DOCS_DIR)),
            "title": post.get("title", md_path.stem.replace("-", " ").title()),
            "content": post.content,
            "metadata": post.metadata,
        }
    except Exception as e:
        logging.error(f"Failed to parse {md_path}: {e}")
        return {
            "path": str(md_path.relative_to(DOCS_DIR)),
            "title": md_path.stem.replace("-", " ").title(),
            "content": "",
            "metadata": {},
        }


def main() -> None:
    """Dual re-index all markdown docs into Qdrant and export as JSON-LD for KG."""
    setup_logging()
    logging.info(f"Scanning markdown docs in {DOCS_DIR}")
    md_files: List[Path] = scan_markdown_docs(DOCS_DIR)
    logging.info(f"Found {len(md_files)} markdown files")
    docs: List[Dict[str, Any]] = [parse_markdown_doc(md) for md in md_files]
    logging.info(f"Parsed {len(docs)} docs")

    logging.info("Connecting to Qdrant...")
    client: QdrantClient = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    logging.info("Connected to Qdrant.")

    ensure_qdrant_collection(client)
    logging.info("Ensured Qdrant collection exists.")

    logging.info("Loading embedding model...")
    model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
    logging.info("Model loaded.")

    logging.info("Indexing in Qdrant...")
    index_in_qdrant(docs, client, model)
    logging.info("Qdrant indexing complete.")

    logging.info("Exporting to JSON-LD for knowledge graph...")
    export_jsonld(docs, KG_EXPORT_DIR)
    logging.info("KG export complete.")

    # Automatically sync to MCP KG server memory file
    mcp_memory_path: Path = Path(
        "/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl"
    )
    kg_jsonld_path: Path = KG_EXPORT_DIR / "kg_nodes.jsonld"
    try:
        shutil.copyfile(kg_jsonld_path, mcp_memory_path)
        logging.info(f"Synced {kg_jsonld_path} to MCP KG server at {mcp_memory_path}")
    except Exception as e:
        logging.error(f"Failed to sync KG export to MCP memory file: {e}")

    # Reconcile formats: convert JSON-LD to MCP NDJSON
    try:
        with open(kg_jsonld_path, encoding="utf-8") as f:
            nodes: List[Dict[str, Any]] = json.load(f)
        with open(mcp_memory_path, "w", encoding="utf-8") as out:
            for node in nodes:
                entity: Dict[str, Any] = {
                    "type": "entity",
                    "name": node.get("name"),
                    "entityType": node.get("@type", "CreativeWork"),
                    "observations": [node.get("text", "")],
                }
                out.write(json.dumps(entity) + "\n")
        logging.info(f"Reconciled and wrote MCP NDJSON format to {mcp_memory_path}")
    except Exception as e:
        logging.error(f"Failed to reconcile and write MCP NDJSON format: {e}")

    # Cross-reference summary
    cross_refs: List[Any] = [
        (doc["title"], doc["metadata"].get("superseded_by"))
        for doc in docs
        if doc["metadata"].get("superseded_by")
    ]
    if cross_refs:
        logging.info("Cross-references (superseded_by):")
        for title, ref in cross_refs:
            logging.info(f"- {title} superseded by {ref}")
    else:
        logging.info("No cross-references found.")

    logging.info("Dual re-indexing complete.")


if __name__ == "__main__":
    main()
