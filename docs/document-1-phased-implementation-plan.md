# Panoptikon: Phased Implementation Plan

## Key Constraints

* The constraint of working solo in Cursor
* The chosen stack (Python backend, PyObjC frontend)
* The constraint of working solo in Cursor
* Hardwired **linting, code standards, and testing** from day one

## 🧱 Phase 0 – Project Bootstrapping (Week 1)
### 🔹 Goals
* Set up the entire project environment with linters, formatters, test scaffolding, and modular structure.
* Ensure all code passes lint/test CI from the beginning.

### 🔹 Deliverables
* Project directory scaffold in Cursor
* Working test suite and lint pipeline
* Pre-commit hooks (if using Git)
* Cursor-configured dev environment

### 🔹 Tasks
* Use poetry or hatch to manage virtualenv, dependencies, and build targets.
* Add:
  * ruff for linting
  * black for formatting
  * mypy for static typing
  * pytest for test framework
  * coverage.py for tracking test coverage
* Stub out modules:
```
panoptikon/
├── __init__.py
├── index/
├── search/
├── ui/          # For PyObjC frontend
├── config/
├── cloud/
└── db/
tests/
├── test_index.py
├── test_search.py
└── ...
```

## 🚀 Phase 1 – MVP (Weeks 2–4)
### 🔹 Goals
* Implement minimal viable system:
  * Recursive file indexer
  * Persistent metadata store (SQLite)
  * Terminal-based search interface (no GUI yet)

### 🔹 Deliverables
* Indexer scanning local disk
* SQLite schema for file metadata
* Search API returning ranked results
* Linted, typed, and tested modules

### 🔹 Features from spec:
* 2.1.1, 2.1.2 – File indexing + metadata collection
* 2.2.1 – Basic as-you-type filename/path search
* 3.1.1 – Search perf under 200ms
* 4.1.1/4.1.2 – Component + DB structure

## 🪟 Phase 2 – Native macOS UI (Weeks 5–8)
### 🔹 Recommendation: Use PyObjC
* Stays in Python.
* Easier to integrate with existing Cursor environment.
* Smaller footprint than bundling SwiftUI.
* Cursor can help you structure even the verbose AppKit code.

SwiftUI could be explored *later* if PyObjC hits UX or signing walls.

### 🔹 Deliverables
* Native .app window via PyObjC
* Search box with live result list
* Column sorting, open file, reveal in Finder
* Basic menu bar integration

### 🔹 Features from spec:
* 2.3.1 – Single-window UI
* 2.3.2 – File open + reveal
* 2.2.3 – Result display (basic version)
* 2.4.2 – System tray/menu bar icon

## ☁️ Phase 3 – Cloud + Extended Search (Weeks 9–12)
### 🔹 Goals
* Cloud-aware metadata (iCloud, Dropbox)
* Advanced search syntax
* Live updates as filesystem changes

### 🔹 Deliverables
* Cloud storage status detection module
* cloud: and status: filters
* Incremental index updates with watchdog or FSEvents
* Saved searches

### 🔹 Features from spec:
* 2.1.4 – Cloud storage support
* 2.2.2 – Boolean, size, date filters
* 2.3.3 – Preferences pane
* 3.1.2 – Indexing performance constraints

## 🌍 Phase 4 – Finalization and Distribution (Weeks 13–16)
### 🔹 Goals
* Signing + notarization
* Auto-update support
* Full accessibility and UX pass

### 🔹 Deliverables
* Signed .app bundle
* Distribution-ready build scripts
* User documentation
* CI setup for builds (GitHub Actions or local)

### 🔹 Features:
* 3.4 – Compatibility matrix
* 3.3 – Security + privacy
* 4.2.3 – Deployment
* 5.x – Deliverables

## 📂 Recommended Project Layout
```
panoptikon/
├── panoptikon/
│   ├── __init__.py
│   ├── index/
│   ├── search/
│   ├── db/
│   ├── ui/              # PyObjC-specific frontend
│   ├── cloud/
│   ├── config/
│   └── utils/
├── tests/
├── assets/              # icons, images, etc.
├── scripts/             # dev tools, CI helpers
├── pyproject.toml       # use poetry or hatch
├── README.md
└── .github/             # for CI
```
