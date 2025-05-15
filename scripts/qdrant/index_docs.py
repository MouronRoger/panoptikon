#!/usr/bin/env python3
"""Simple MKDocs to Qdrant pipeline
Automatically indexes your documentation for semantic search
"""
import hashlib
import os
from pathlib import Path
from typing import Dict, List

import frontmatter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer


class MKDocsToQdrant:
    def __init__(self, 
                 docs_dir: str = None,
                 collection_name: str = "panoptikon",
                 qdrant_url: str = None,
                 qdrant_api_key: str = None):
        
        # Initialize embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Qdrant client
        if qdrant_url and qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.client = QdrantClient(host="localhost", port=6333)
        
        # Set docs directory - default to project root/docs
        if docs_dir is None:
            project_root = Path(__file__).parent.parent.parent
            docs_dir = project_root / "docs"
        
        self.docs_dir = Path(docs_dir)
        self.collection_name = collection_name
        
    def setup_collection(self):
        """Create collection if it doesn't exist"""
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
            print(f"Collection {self.collection_name} already exists")
        except:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"Created collection: {self.collection_name}")
    
    def scan_docs(self) -> List[Dict]:
        """Scan MKDocs directory for markdown files"""
        documents = []
        
        print(f"Scanning directory: {self.docs_dir}")
        print(f"Directory exists: {self.docs_dir.exists()}")
        
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
                print(f"Error reading {md_file}: {e}")
        
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
        """Generate embeddings and store in Qdrant"""
        points = []
        
        for i, doc in enumerate(documents):
            # Generate embedding
            embedding = self.model.encode(doc['content'])
            
            # Create unique ID
            doc_id = hashlib.md5(f"{doc['path']}-{doc.get('chunk_id', 0)}".encode()).hexdigest()
            
            # Create point
            point = PointStruct(
                id=doc_id,
                vector=embedding.tolist(),
                payload={
                    'path': doc['path'],
                    'title': doc['title'],
                    'content': doc['content'][:500],  # Store preview
                    'url': doc['url'],
                    'chunk_id': doc.get('chunk_id', 0),
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
        print("Starting MKDocs to Qdrant pipeline...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Docs directory path: {self.docs_dir}")
        print(f"Docs directory absolute: {self.docs_dir.absolute()}")
        
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
    # Use your cloud Qdrant instance
    pipeline = MKDocsToQdrant(
        docs_dir=None,  # Will use default project root/docs
        collection_name="panoptikon",
        qdrant_url="https://29d119a0-8d2b-4275-a712-6dabdea4a8fa.europe-west3-0.gcp.cloud.qdrant.io",
        qdrant_api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9MIfh-2k_Xq-_yHXmlIErv-GaT0xjW5J4jo6j0_VVJw"
    )
    
    pipeline.run()


if __name__ == "__main__":
    main()
