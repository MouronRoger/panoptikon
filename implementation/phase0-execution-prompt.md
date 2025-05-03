# Phase 0: Project Bootstrapping - Execution Prompt

I need you to bootstrap the Panoptikon file search application with a focus on quality from day one. Follow the "Land Rover philosophy" of simplicity, robustness, and fitness for purpose while implementing a rigorous quality foundation.

## Task Overview

You're implementing the initial project structure and quality tools for Panoptikon, a high-performance file search application inspired by the Windows "Everything" utility. This needs to be done with quality as the primary concern from the very beginning.

## Step 1: Project Structure Setup

Create the following directory structure:

```
panoptikon/
├── pyproject.toml       # Main package configuration
├── README.md           # Project documentation
├── src/
│   └── panoptikon/     # Main package
│       ├── __init__.py
│       ├── index/      # File indexing system
│       │   └── __init__.py
│       ├── search/     # Search functionality
│       │   └── __init__.py
│       ├── ui/         # UI components (PyObjC)
│       │   └── __init__.py
│       ├── db/         # Database operations
│       │   └── __init__.py
│       ├── cloud/      # Cloud provider integration
│       │   └── __init__.py
│       ├── config/     # Application settings
│       │   └── __init__.py
│       └── utils/      # Common utilities
│           └── __init__.py
├── tests/              # Test directory
│   ├── conftest.py
│   ├── test_index/
│   ├── test_search/
│   ├── test_ui/
│   ├── test_db/
│   ├── test_cloud/
│   └── test_utils/
├── scripts/            # Utility scripts
├── docs/               # Documentation
│   ├── project_status.md
│   └── phase0_complete.md
└── assets/             # Non-code resources
```

## Step 2: Quality Tool Configuration

Implement the following quality tools:

1. Create `pyproject.toml` with:
   - Project metadata and dependencies
   - Black configuration (120 char line length)
   - Ruff configuration for fast linting
   - MyPy for strict type checking
   - Pytest configuration
   - Coverage settings (minimum 80%)

2. Create `.pre-commit-config.yaml` with:
   - Black for formatting
   - Ruff for linting
   - MyPy for type checking
   - Additional hooks for quality checks
   - Maximum file size checks (500 lines)
   - Docstring coverage validation

## Step 3: Module Structure Initialization

Initialize each module with:

1. Descriptive `__init__.py` files that:
   - Define module responsibility
   - Include proper type annotations
   - Document public API

2. Create a basic class or function in each module that:
   - Demonstrates proper docstring format
   - Shows correct type annotation style
   - Follows project style guidelines

## Step 4: Quality Documentation

Create the following documentation:

1. `README.md` with:
   - Project overview and purpose
   - Installation instructions
   - Development setup guide
   - Quality standards summary

2. `CONTRIBUTING.md` with:
   - Contribution workflow
   - Quality requirements
   - Code review process
   - Testing expectations

3. `docs/project_status.md` with:
   - Current phase (Phase 0)
   - Implementation status
   - Next steps for Phase 1

## Step 5: Testing Framework

Set up a comprehensive testing framework:

1. Configure pytest with:
   - Directory structure mirroring the main package
   - Fixture patterns for database, filesystem, etc.
   - Coverage configuration and reporting

2. Create a basic test for each module that:
   - Demonstrates proper test structure
   - Uses fixtures appropriately
   - Shows parameterized testing if applicable

## Deliverables

After completing all steps above, create a detailed status document at `docs/phase0_complete.md` that includes:

1. Project structure diagram showing all directories and files created
2. Complete list of all configured quality checks and their purposes
3. Instructions for running tests and quality checks
4. Module responsibilities and design decisions
5. Next steps for Phase 1 implementation
6. Any challenges encountered and how they were resolved

This document is CRITICAL for continuity as it will be used by the next instance of Claude to continue development.

## Quality Standards

All code and configuration must adhere to these standards:

- Complete type annotations for all functions and methods
- Comprehensive docstrings following Google style
- Maximum file length of 500 lines
- Maximum function length of 50 lines
- No circular dependencies between modules
- Clear separation of concerns
- Consistent naming conventions
- Minimum 80% test coverage

## References

Refer to:
- The Panoptikon project specifications (document 2)
- Quality standards implementation guide (document 5)
- Project execution recommendations (document 4)
- Phased implementation plan (document 1)
