# **. Entity Extraction**
* Detect and extract **new entities** (📦 components, 🧱 modules, 🔧 services, 🧪 test types, ⚙️ configurations).
* Classify them under existing architecture domains:
  * Core Infrastructure, File System Layer, Data Layer, Search Engine, Indexing System, UI, System Integration.

⠀**🔗 2. Relationship Mapping**
* Identify and log **functional dependencies** between components (e.g., Search Engine depends on Query Parser → Query Parser uses Configuration System).
* Represent **bidirectional links** between subsystems using structured triples (e.g., Search Engine ↔ UI Framework via "Result Presentation").

⠀**🏷️ 3. Tagging & Contextual Labelling**
* Auto-apply tags based on context:
  * #critical_path, #performance_risk, #macOS_api, #permissions, #cloud_sync, #UI_threading, etc.
* Use phase and milestone references (Phase_2_Core, Milestone_FoundationReady) for time-specific tags.

⠀**♻️ 4. Dynamic Graph Update**
* Insert or update nodes and edges in the knowledge graph:
  * Ensure **no orphan nodes** (all new entities must connect to at least one functional parent or dependency).
  * Prune **redundant or outdated nodes** (e.g., deprecated abstractions or superseded modules).

⠀**🧪 5. Verification & Consistency Checks**
* Confirm:
  * All #dependencies are valid and resolvable across phases.
  * Tags reflect current **risk status**, **ownership**, and **implementation state**.
  * Phase dependencies remain **acyclic** and **chronologically coherent**.

⠀**📤 6. Snapshot and Log**
* Save the updated graph state as a timestamped JSON-LD or RDF snapshot.
* Log:
  * Changeset summary: +3 nodes, +4 edges, -1 deprecated
  * Top-level diffs by subsystem
  * Any unresolved tagging or dependency issues

⠀
📎 **Use Context:** Panoptikon follows a modular, phase-based architecture with resilient OS abstractions, a search/index core, and layered UI/system integration. The knowledge graph is critical for keeping this complex architecture traceable, auditable, and auto-refactorable.
🛠️ **Tech Context:** Python 3.11+, PyObjC, SQLite (WAL mode), Event-driven architecture, strict lint/test gates.
