# Panoptikon Implementation Prompts

This directory contains the prompts for implementing various components of the Panoptikon file search application. Each prompt is designed to focus on a specific component to ensure high-quality implementation.

## Available Prompts

### Phase 0: Project Bootstrapping
- [phase0-execution-prompt.md](phase0-execution-prompt.md): Initial project setup and quality configuration

### Phase 1: MVP Implementation
- [phase1-execution-prompt.md](phase1-execution-prompt.md): Complete MVP implementation (not recommended - too large)

### Component-Specific Prompts
- [component1-file-crawler.md](component1-file-crawler.md): FileCrawler component implementation
- [component2-metadata-extractor.md](component2-metadata-extractor.md): MetadataExtractor component implementation
- [component3-database-schema.md](component3-database-schema.md): Database schema implementation

## Using These Prompts

1. Use the component-specific prompts rather than the large phase prompts
2. Implement components in order to minimize dependencies
3. Verify each component with linting and tests before moving to the next
4. Document the implementation as you go

## Creating New Component Prompts

To create a prompt for a new component:

1. Use the [prompt template](../cursor/prompt_template.md) as a starting point
2. Follow the component breakdown in the [implementation plan](../cursor/implementation_plan.md)
3. Be specific about requirements and interfaces
4. Include quality standards and testing expectations

## Implementation Order

For optimal results, implement components in this order:

1. FileCrawler
2. MetadataExtractor
3. Database Schema
4. Connection Manager
5. Database Operations
6. Indexing Manager
7. Search Engine Core
8. Query Parser
9. Filter Builder
10. CLI Interface

This order minimizes dependencies and allows for incremental testing.