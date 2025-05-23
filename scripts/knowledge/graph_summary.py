#!/usr/bin/env python3
"""Generate summary statistics for knowledge graph."""
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

MEMORY_PATH = Path("/Users/james/Library/Application Support/Claude/panoptikon/memory.jsonl")


def summarize() -> None:
    """Generate summary of knowledge graph contents."""
    if not MEMORY_PATH.exists():
        print("Error: Knowledge graph not found")
        return
    
    entities_by_type = defaultdict(list)
    relations_by_type = Counter()
    entity_degrees = defaultdict(lambda: {"in": 0, "out": 0})
    
    # Load and analyze
    with open(MEMORY_PATH, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            
            entry = json.loads(line)
            if entry.get("type") == "entity":
                entity_type = entry.get("entityType", "Unknown")
                name = entry.get("name", "Unnamed")
                entities_by_type[entity_type].append(name)
            elif entry.get("type") == "relation":
                rel_type = entry.get("relationType", "unknown")
                from_id = entry.get("from", "")
                to_id = entry.get("to", "")
                
                relations_by_type[rel_type] += 1
                entity_degrees[from_id]["out"] += 1
                entity_degrees[to_id]["in"] += 1
    
    # Print entity summary
    print("=== Entity Summary ===")
    total_entities = 0
    for entity_type, names in sorted(entities_by_type.items()):
        total_entities += len(names)
        print(f"\n{entity_type} ({len(names)}):")
        for name in sorted(names)[:5]:
            print(f"  - {name}")
        if len(names) > 5:
            print(f"  ... and {len(names) - 5} more")
    
    print(f"\nTotal entities: {total_entities}")
    
    # Print relationship summary
    print("\n=== Relationship Summary ===")
    total_relations = sum(relations_by_type.values())
    for rel_type, count in sorted(relations_by_type.items(), key=lambda x: -x[1]):
        print(f"  {rel_type}: {count}")
    print(f"\nTotal relationships: {total_relations}")
    
    # Print top entities by degree
    print("\n=== Top 10 Entities by Connections ===")
    entity_total_degree = {
        entity: deg["in"] + deg["out"] 
        for entity, deg in entity_degrees.items()
    }
    
    for entity, degree in sorted(entity_total_degree.items(), key=lambda x: -x[1])[:10]:
        in_deg = entity_degrees[entity]["in"]
        out_deg = entity_degrees[entity]["out"]
        print(f"  {entity}: {degree} connections (in: {in_deg}, out: {out_deg})")


if __name__ == "__main__":
    summarize()
