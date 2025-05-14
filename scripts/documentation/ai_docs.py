#!/usr/bin/env python3
"""AI-Accessible Documentation System.

Allows AI to read, update, and maintain project documentation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import frontmatter  # type: ignore[import]
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class AIDocumentationSystem:
    """System for managing AI-accessible project documentation."""

    def __init__(self, docs_root: str = "docs") -> None:
        """Initialize the documentation system."""
        self.docs_root = Path(docs_root)
        self.ensure_structure()
        # For indexing
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant = QdrantClient(
            url=(
                "https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-"
                "west3-0.gcp.cloud.qdrant.io"
            ),
            api_key=(
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0."
                "9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
            ),
        )
        self.ensure_collection()

    def ensure_structure(self) -> None:
        """Create standard documentation structure."""
        dirs = [
            "architecture",
            "components",
            "phases",
            "testing",
            "api",
            "guides",
            "decisions",
            "progress",
        ]
        for dir_name in dirs:
            (self.docs_root / dir_name).mkdir(parents=True, exist_ok=True)

    def ensure_collection(self) -> None:
        """Ensure Qdrant collection exists."""
        from qdrant_client.models import Distance, VectorParams

        try:
            self.qdrant.get_collection("panoptikon")
        except Exception:
            self.qdrant.create_collection(
                collection_name="panoptikon",
                vectors_config={
                    "fast-all-minilm-l6-v2": VectorParams(
                        size=384, distance=Distance.COSINE
                    )
                },
            )
            print("Created Qdrant collection: panoptikon with named vectors")

    def create_document(
        self,
        category: str,
        title: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Path:
        """Create a new documentation file in the specified category. Validates category."""
        self.validate_category(category)
        if metadata is None:
            metadata = {}
        filename = title.lower().replace(" ", "-") + ".md"
        filepath = self.docs_root / category / filename
        meta = {
            "title": title,
            "category": category,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "ai_generated": True,
            **metadata,
        }
        post = frontmatter.Post(content, **meta)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        self.index_document(filepath)
        return filepath

    def update_document(self, filepath: Path, updates: dict[str, Any]) -> bool:
        """Update existing documentation."""
        if not filepath.exists():
            return False
        with open(filepath, encoding="utf-8") as f:
            post = frontmatter.load(f)
        if "content" in updates:
            post.content = updates["content"]
        if "metadata" in updates:
            post.metadata.update(updates["metadata"])
        post.metadata["updated"] = datetime.now().isoformat()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        self.index_document(filepath)
        return True

    def search_docs(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search documentation using semantic search via Qdrant."""
        query_vector = self.model.encode(query).tolist()
        results = self.qdrant.search(
            collection_name="panoptikon", query_vector=query_vector, limit=limit
        )
        return [
            {
                "path": r.payload["path"],
                "title": r.payload["title"],
                "score": r.score,
                "content": r.payload.get("content", ""),
            }
            for r in results
            if r.payload is not None
        ]

    def index_document(self, filepath: Path) -> None:
        """Index a single document in Qdrant."""
        if not filepath.exists():
            return
        with open(filepath, encoding="utf-8") as f:
            post = frontmatter.load(f)
        content = f"{post.metadata.get('title', '')}\n\n{post.content}"
        embedding = self.model.encode(content).tolist()
        path_str = str(filepath.relative_to(self.docs_root))
        doc_id = abs(hash(path_str)) % (10**8)
        payload = {
            "path": str(filepath.relative_to(self.docs_root)),
            "title": post.metadata.get("title", filepath.stem),
            "content": post.content[:500],
            "document": post.content[:500],  # MCP expects this field
            "category": filepath.parent.name,
            "metadata": post.metadata,
        }
        from qdrant_client.models import PointStruct

        self.qdrant.upsert(
            collection_name="panoptikon",
            points=[
                PointStruct(
                    id=doc_id,
                    vector={"fast-all-minilm-l6-v2": embedding},
                    payload=payload,
                )
            ],
        )
        print(f"Indexed: {filepath.name}")

    def create_component_doc(
        self, component_name: str, details: dict[str, Any]
    ) -> Path:
        """Create documentation for a component."""
        self.validate_category("components")
        content = f"""# {component_name}

## Overview
{details.get("overview", "No overview provided.")}

## Purpose
{details.get("purpose", "No purpose defined.")}

## Implementation
{details.get("implementation", "Implementation details not available.")}

## API
{details.get("api", "API documentation pending.")}

## Testing
{details.get("testing", "Testing information not available.")}

## Dependencies
{details.get("dependencies", "No dependencies listed.")}

## Status
- Implementation: {details.get("status", "Unknown")}
- Test Coverage: {details.get("coverage", "Unknown")}
- Last Updated: {datetime.now().strftime("%Y-%m-%d")}
"""
        return self.create_document(
            category="components",
            title=component_name,
            content=content,
            metadata={
                "component_type": details.get("type", "Unknown"),
                "phase": details.get("phase", "Unknown"),
            },
        )

    def create_phase_doc(self, phase_name: str, details: dict[str, Any]) -> Path:
        """Create documentation for a project phase."""
        self.validate_category("phases")
        content = f"""# {phase_name}

## Objectives
{details.get("objectives", "No objectives defined.")}

## Components
{details.get("components", "No components listed.")}

## Status
{details.get("status", "Not started")}

## Progress
{details.get("progress", "No progress information.")}

## Issues
{details.get("issues", "No known issues.")}

## Next Steps
{details.get("next_steps", "Next steps not defined.")}
"""
        return self.create_document(
            category="phases",
            title=phase_name,
            content=content,
            metadata={
                "phase_number": details.get("number", 0),
                "status": details.get("status", "Unknown"),
            },
        )

    def create_decision_record(self, title: str, decision: dict[str, Any]) -> Path:
        """Create an Architecture Decision Record (ADR)."""
        self.validate_category("decisions")
        content = f"""# {title}

## Status
{decision.get("status", "Proposed")}

## Context
{decision.get("context", "No context provided.")}

## Decision
{decision.get("decision", "No decision recorded.")}

## Consequences
{decision.get("consequences", "No consequences documented.")}

## Alternatives Considered
{decision.get("alternatives", "No alternatives documented.")}

## Date
{datetime.now().strftime("%Y-%m-%d")}
"""
        return self.create_document(
            category="decisions",
            title=f"ADR-{datetime.now().strftime('%Y%m%d')}-{title}",
            content=content,
            metadata={
                "adr": True,
                "status": decision.get("status", "Proposed"),
            },
        )

    def update_progress(self, phase: str, updates: dict[str, Any]) -> bool:
        """Update progress documentation."""
        self.validate_category("progress")
        filepath = self.docs_root / "progress" / f"{phase.lower()}-progress.md"
        if not filepath.exists():
            content = f"# {phase} Progress\n\n"
            self.create_document("progress", f"{phase} Progress", content)
        with open(filepath, encoding="utf-8") as f:
            post = frontmatter.load(f)
        new_entry = f"""
## {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Status**: {updates.get("status", "In Progress")}
- **Completed**: {updates.get("completed", [])}
- **Issues**: {updates.get("issues", [])}
- **Next**: {updates.get("next", [])}
- **Notes**: {updates.get("notes", "")}

---
"""
        post.content = new_entry + post.content
        return self.update_document(filepath, {"content": post.content})

    def validate_category(self, category: str) -> None:
        """Raise ValueError if category is not valid."""
        VALID_CATEGORIES = [
            "architecture",
            "components",
            "phases",
            "testing",
            "api",
            "guides",
            "decisions",
            "progress",
        ]
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Valid categories: {', '.join(VALID_CATEGORIES)}"
            )


def read_documentation(category: str, title: str) -> Optional[dict[str, Any]]:
    """Read a specific documentation file."""
    docs = AIDocumentationSystem()
    docs.validate_category(category)
    filepath = docs.docs_root / category / f"{title.lower().replace(' ', '-')}.md"
    if not filepath.exists():
        return None
    with open(filepath, encoding="utf-8") as f:
        post = frontmatter.load(f)
    return {
        "title": post.metadata.get("title"),
        "content": post.content,
        "metadata": post.metadata,
        "path": str(filepath),
    }


def update_documentation(category: str, title: str, updates: dict[str, Any]) -> bool:
    """Update existing documentation."""
    docs = AIDocumentationSystem()
    docs.validate_category(category)
    filepath = docs.docs_root / category / f"{title.lower().replace(' ', '-')}.md"
    return docs.update_document(filepath, updates)


def create_documentation(
    category: str, title: str, content: str, **metadata: Any
) -> str:
    """Create new documentation."""
    docs = AIDocumentationSystem()
    docs.validate_category(category)
    filepath = docs.create_document(category, title, content, metadata)
    return str(filepath)


def search_documentation(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search all documentation."""
    docs = AIDocumentationSystem()
    return docs.search_docs(query, limit)


def document_component(name: str, **details: Any) -> str:
    """Document a new component."""
    docs = AIDocumentationSystem()
    docs.validate_category("components")
    filepath = docs.create_component_doc(name, details)
    return str(filepath)


def document_phase(name: str, **details: Any) -> str:
    """Document a project phase."""
    docs = AIDocumentationSystem()
    docs.validate_category("phases")
    filepath = docs.create_phase_doc(name, details)
    return str(filepath)


def record_decision(title: str, **decision_details: Any) -> str:
    """Record an architecture decision."""
    docs = AIDocumentationSystem()
    docs.validate_category("decisions")
    filepath = docs.create_decision_record(title, decision_details)
    return str(filepath)


def update_phase_progress(phase: str, **updates: Any) -> bool:
    """Update phase progress."""
    docs = AIDocumentationSystem()
    docs.validate_category("progress")
    return docs.update_progress(phase, updates)


if __name__ == "__main__":
    print("AI Documentation System Ready")
    doc_path = document_component(
        "DatabaseConnectionPool",
        overview="Thread-safe connection pooling for SQLite",
        purpose="Manage database connections efficiently",
        status="Implemented",
        coverage="76%",
    )
    print(f"Created: {doc_path}")
