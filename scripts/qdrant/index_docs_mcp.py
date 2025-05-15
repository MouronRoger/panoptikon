#!/usr/bin/env python3
"""MKDocs to Qdrant pipeline for panoptikon collection
Uploads documentation to the panoptikon collection with MCP-compatible configuration
"""
import hashlib
from pathlib import Path
from typing import Dict, List

import frontmatter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer


class MKDocsToQdrant:
    def __init__(self, 
                 docs_dir: str = "docs",
                 collection_name: str = "panoptikon",  # Changed to panoptikon
                 qdrant_url: str = None,
                 qdrant_api_key: str = None,
                 vector_name: str = "fast-all-minilm-l6-v2"):  # Match MCP config
        
        # Initialize embedding model - matching the vector name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Qdrant client
        if qdrant_url and qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.client = QdrantClient(host="localhost", port=6333)
        
        self.docs_dir = Path(docs_dir)
        self.collection_name = collection_name
        self.vector_name = vector_name
        
    def setup_collection(self):
        """Create or recreate the collection with named vectors"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Deleted existing collection: {self.collection_name}")
        except:
            pass
        
        # Create collection with named vector configuration to match MCP
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                self.vector_name: VectorParams(size=384, distance=Distance.COSINE)
            }
        )
        print(f"Created collection: {self.collection_name} with vector '{self.vector_name}'")
    
    def scan_docs(self) -> List[Dict]:
        """Scan MKDocs directory for markdown files"""
        documents = []
        
        for md_file in self.docs_dir.rglob("*.md"):
            # Skip index files or other special files if needed
            if md_file.name.startswith('.'):
                continue
                
            try:
                with open(md_file, encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    
                # Create document metadata
                doc = {
                    'path': str(md_file.relative_to(self.docs_dir)),
                    'title': post.get('title', md_file.stem.replace('-', ' ').title()),
                    'content': post.content,
                    'metadata': post.metadata,
                    'url': self._path_to_url(md_file)
                }
                
                documents.append(doc)
                print(f"Found: {doc['path']}")
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
        
        return documents
    
    def _path_to_url(self, file_path: Path) -> str:
        """Convert file path to MKDocs URL"""
        relative = file_path.relative_to(self.docs_dir)
        url_path = str(relative).replace('.md', '/')
        return url_path
    
    def chunk_document(self, doc: Dict, chunk_size: int = 1000) -> List[Dict]:
        """Split document into chunks for better search"""
        content = doc['content']
        chunks = []
        
        # Simple paragraph-based chunking
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    **doc,
                    'content': current_chunk.strip(),
                    'chunk_id': len(chunks)
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append({
                **doc,
                'content': current_chunk.strip(),
                'chunk_id': len(chunks)
            })
        
        return chunks if chunks else [doc]
    
    def index_documents(self, documents: List[Dict]):
        """Generate embeddings and store in Qdrant with named vectors"""
        points = []
        
        for i, doc in enumerate(documents):
            # Generate embedding
            embedding = self.model.encode(doc['content'])
            
            # Create unique ID
            doc_id = hashlib.md5(f"{doc['path']}-{doc.get('chunk_id', 0)}".encode()).hexdigest()
            
            # Create point with named vector
            point = PointStruct(
                id=doc_id,
                vector={
                    self.vector_name: embedding.tolist()  # Use named vector
                },
                payload={
                    'path': doc['path'],
                    'title': doc['title'],
                    'content': doc['content'][:500],  # Store preview
                    'document': doc['content'][:500],  # ADD THIS - MCP expects 'document'
                    'url': doc['url'],
                    'chunk_id': doc.get('chunk_id', 0),
                    'source': 'mkdocs',  # Add source identifier
                    **doc.get('metadata', {})
                }
            )
            points.append(point)
            
            # Upload in batches
            if len(points) >= 100:
                self.client.upsert(collection_name=self.collection_name, points=points)
                print(f"Indexed {len(points)} documents")
                points = []
        
        # Upload remaining
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"Indexed {len(points)} documents")
    
    def run(self):
        """Run the complete pipeline"""
        print("Starting MKDocs to Qdrant pipeline (panoptikon collection)...")
        
        # Setup collection
        self.setup_collection()
        
        # Scan documents
        documents = self.scan_docs()
        print(f"Found {len(documents)} documents")
        
        # Chunk documents
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        print(f"Created {len(all_chunks)} chunks")
        
        # Index in Qdrant
        self.index_documents(all_chunks)
        print("Pipeline complete!")
        
        # Verify
        info = self.client.get_collection(self.collection_name)
        print(f"Collection has {info.points_count} points")


def main():
    # Use your cloud Qdrant instance with panoptikon collection
    project_root = Path(__file__).parent.parent.parent
    docs_path = project_root / "docs"
    
    pipeline = MKDocsToQdrant(
        docs_dir=str(docs_path),
        collection_name="panoptikon",  # Changed from panoptikon_docs
        qdrant_url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
        qdrant_api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw",
        vector_name="fast-all-minilm-l6-v2"  # Match MCP configuration
    )
    
    pipeline.run()


if __name__ == "__main__":
    main()
