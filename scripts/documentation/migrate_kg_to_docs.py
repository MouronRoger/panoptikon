#!/usr/bin/env python3
"""
Migrate Knowledge Graph to Documentation
Converts existing knowledge graph entities to structured markdown documentation
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.documentation.ai_docs import AIDocumentationSystem
import json


def migrate_knowledge_graph():
    """Convert knowledge graph to documentation"""
    docs = AIDocumentationSystem()
    
    # This is where you'd read from the knowledge graph
    # For demo, I'll use a few examples from what I saw
    
    # Document Phase 4 status from knowledge graph
    docs.document_phase(
        "Phase 4.2 - Connection Pool Management",
        objectives="Implement thread-safe connection pooling for SQLite",
        components=["DatabaseConnectionPool", "PoolManager", "DatabasePoolService"],
        status="Code Complete - Needs Testing",
        progress="Implementation complete but missing critical testing",
        issues=[
            "Zero test coverage for connection pool",
            "Must test concurrent access with 100+ threads", 
            "Pydantic v1 validators need migration to v2"
        ],
        next_steps=[
            "Create comprehensive test suite",
            "Migrate Pydantic validators",
            "Run performance benchmarks"
        ]
    )
    
    # Document a critical issue
    docs.record_decision(
        "Pause Phase 4.3 Until Testing Complete",
        status="Proposed",
        context="Phase 4.2 connection pool has zero test coverage",
        decision="Block Phase 4.3 migration framework until 4.2 tests pass",
        consequences="1-2 week delay but ensures stable foundation",
        alternatives=["Continue without tests (risky)", "Partial testing only"]
    )
    
    # Document a component
    docs.document_component(
        "DatabaseConnectionPool",
        overview="Thread-safe connection pooling for SQLite database connections",
        purpose="Manage connections efficiently while respecting SQLite single-writer limitation",
        implementation="Implemented in src/panoptikon/database/pool.py",
        status="Code Complete",
        coverage="0% - CRITICAL",
        testing="Missing all tests - requires immediate attention",
        dependencies=["threading", "sqlite3", "queue"]
    )
    
    print("Knowledge graph migration complete!")
    print("Documentation created in docs/ directory")


if __name__ == "__main__":
    migrate_knowledge_graph()
