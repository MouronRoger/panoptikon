#!/usr/bin/env python3
"""
Simple documentation system without embeddings
Just creates markdown docs that can be manually indexed later
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import frontmatter


class SimpleDocumentationSystem:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.ensure_structure()
    
    def ensure_structure(self):
        """Create standard documentation structure"""
        dirs = [
            "architecture",
            "components", 
            "phases",
            "testing",
            "api",
            "guides",
            "decisions",
            "progress"
        ]
        
        for dir_name in dirs:
            (self.docs_root / dir_name).mkdir(parents=True, exist_ok=True)
    
    def create_document(self, 
                       category: str,
                       title: str,
                       content: str,
                       metadata: Dict = None) -> Path:
        """Create a new documentation file"""
        # Generate filename
        filename = title.lower().replace(' ', '-') + '.md'
        filepath = self.docs_root / category / filename
        
        # Prepare frontmatter
        meta = {
            'title': title,
            'category': category,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'ai_generated': True,
            **(metadata or {})
        }
        
        # Create document
        post = frontmatter.Post(content, **meta)
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        print(f"Created: {filepath}")
        return filepath
    
    def create_component_doc(self, component_name: str, details: Dict) -> Path:
        """Create documentation for a component"""
        content = f"""# {component_name}

## Overview
{details.get('overview', 'No overview provided.')}

## Purpose
{details.get('purpose', 'No purpose defined.')}

## Implementation
{details.get('implementation', 'Implementation details not available.')}

## Testing
{details.get('testing', 'Testing information not available.')}

## Status
- Implementation: {details.get('status', 'Unknown')}
- Test Coverage: {details.get('coverage', 'Unknown')}
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        return self.create_document(
            category='components',
            title=component_name,
            content=content,
            metadata={
                'component_type': details.get('type', 'Unknown'),
                'phase': details.get('phase', 'Unknown')
            }
        )
    
    def create_phase_doc(self, phase_name: str, details: Dict) -> Path:
        """Create documentation for a project phase"""
        content = f"""# {phase_name}

## Objectives
{details.get('objectives', 'No objectives defined.')}

## Components
{details.get('components', 'No components listed.')}

## Status
{details.get('status', 'Not started')}

## Progress
{details.get('progress', 'No progress information.')}

## Issues
{details.get('issues', 'No known issues.')}

## Next Steps
{details.get('next_steps', 'Next steps not defined.')}
"""
        
        return self.create_document(
            category='phases',
            title=phase_name,
            content=content,
            metadata={
                'phase_number': details.get('number', 0),
                'status': details.get('status', 'Unknown')
            }
        )


def migrate_knowledge_graph():
    """Convert knowledge graph to documentation"""
    docs = SimpleDocumentationSystem()
    
    print("📊 Migrating knowledge graph to documentation...")
    
    # Document Phase 4 status
    docs.create_phase_doc(
        "Phase 4.2 - Connection Pool Management",
        {
            "objectives": "Implement thread-safe connection pooling for SQLite",
            "components": ["DatabaseConnectionPool", "PoolManager", "DatabasePoolService"],
            "status": "Code Complete - Needs Testing",
            "progress": "Implementation complete but missing critical testing",
            "issues": [
                "Zero test coverage for connection pool",
                "Must test concurrent access with 100+ threads", 
                "Pydantic v1 validators need migration to v2"
            ],
            "next_steps": [
                "Create comprehensive test suite",
                "Migrate Pydantic validators",
                "Run performance benchmarks"
            ]
        }
    )
    
    # Document a component
    docs.create_component_doc(
        "DatabaseConnectionPool",
        {
            "overview": "Thread-safe connection pooling for SQLite",
            "purpose": "Manage database connections efficiently",
            "implementation": "Implemented in src/panoptikon/database/pool.py",
            "status": "Code Complete",
            "coverage": "0% - CRITICAL",
            "testing": "Missing all tests - requires immediate attention"
        }
    )
    
    print("✨ Migration complete!")
    print("Documentation created in docs/ directory")
    print("\nYou can now:")
    print("1. Browse the docs/ directory")
    print("2. Use MKDocs to serve them: mkdocs serve")
    print("3. Index them in Qdrant when ready")


if __name__ == "__main__":
    migrate_knowledge_graph()
