# Panoptikon Documentation Directory

## Overview

This directory contains all project documentation, organized by category. Each subdirectory corresponds to a valid documentation category enforced by the documentation system.

## Documentation Categories

| Category      | Directory         | Description                                      |
|--------------|-------------------|--------------------------------------------------|
| architecture  | docs/architecture | System and software architecture docs            |
| components    | docs/components   | Documentation for individual components/modules   |
| stages        | docs/stages       | Project stage and substage documentation         |
| testing       | docs/testing      | Test plans, coverage, and testing docs           |
| api           | docs/api          | API documentation and references                 |
| guides        | docs/guides       | How-to guides and tutorials                      |
| decisions     | docs/decisions    | Architecture Decision Records (ADRs)             |
| progress      | docs/progress     | Progress tracking and milestone documentation    |

## Onboarding & Usage

- **All documentation must be placed in the correct subdirectory.**
- The documentation system (see `scripts/documentation/ai_docs.py`) enforces category consistency. Only the above categories are valid.
- When creating or updating documentation, always specify the correct category. The system will raise an error if an invalid category is used.
- For more information on the documentation system and how to contribute, see `scripts/documentation/README.md` and `AI_DOCUMENTATION_GUIDE.md`.

## Example

- To add a new component doc, place it in `docs/components/`.
- To update project stage documentation, use `docs/stages/`.
- All ADRs (decisions) go in `docs/decisions/`.

## Questions?

If you are unsure which category to use, run `list_valid_categories()` from the documentation system or consult the AI assistant. 