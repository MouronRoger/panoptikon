#!/usr/bin/env python3
"""MCP-aware parser for ai_docs.md progress tracking.

Extracts progress entries and links them to roadmap entities using MCP best practices.
CRITICAL: Only uses existing timestamps - NEVER generates dates/times.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.knowledge.relationship_extractor_typed import (  # noqa: E402
    KnowledgeGraphManager,
)


class AIDocsParser:
    """Parse ai_docs.md entries and extract progress information."""

    def __init__(self, memory_manager: KnowledgeGraphManager) -> None:
        self.km = memory_manager
        self.processed_entries: set[str] = set()

    def parse_file(self, filepath: Path, dry_run: bool = False) -> None:
        """Parse ai_docs.md and extract all progress entries."""
        print(f"\nParsing AI docs: {filepath}")
        content = filepath.read_text(encoding="utf-8")
        entries = self._split_entries(content)
        valid_count = 0
        skipped_count = 0
        for entry in entries:
            if self._has_valid_timestamp(entry):
                self._process_entry(entry, dry_run)
                valid_count += 1
            else:
                skipped_count += 1
        print(
            f"\nProcessed {valid_count} entries, skipped {skipped_count} (no valid timestamp)"
        )

    def _split_entries(self, content: str) -> List[str]:
        """Split content into individual dated entries."""
        pattern = r"(?=## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\])"
        entries = re.split(pattern, content)
        return [e.strip() for e in entries if e.strip()]

    def _has_valid_timestamp(self, entry: str) -> bool:
        """Check if entry has a valid timestamp format."""
        return bool(re.match(r"## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]", entry))

    def _process_entry(self, entry: str, dry_run: bool = False) -> None:
        """Process a single progress entry using MCP best practices."""
        timestamp_match = re.match(r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]", entry)
        if not timestamp_match:
            return
        timestamp = timestamp_match.group(1)
        first_line = entry.split("\n")[0]
        tags = re.findall(r"#([\w.-]+)", first_line)
        phase_tags = [t for t in tags if t.startswith("phase")]
        stage_tags = [t for t in tags if t.startswith("stage")]
        status = self._extract_status(tags)
        summary = self._extract_summary(entry)
        self._process_phases_and_stages(
            phase_tags, stage_tags, timestamp, status, summary, dry_run
        )
        if summary:
            self._process_components(summary, timestamp, dry_run)
        if "decision" in tags:
            self._process_decision(timestamp, summary, dry_run)

    def _extract_status(self, tags: list[str]) -> str:
        """Extract status from tags."""
        if "done" in tags:
            return "Complete"
        if "todo" in tags:
            return "Planned"
        if "wip" in tags or "in-progress" in tags:
            return "In Progress"
        return "In Progress"

    def _extract_summary(self, entry: str) -> str:
        """Extract summary from entry."""
        summary_match = re.search(
            r"- \*\*Summary:\*\*\s*(.+?)(?=\n-|\n\n|\Z)", entry, re.DOTALL
        )
        return summary_match.group(1).strip() if summary_match else ""

    def _process_phases_and_stages(
        self,
        phase_tags: list[str],
        stage_tags: list[str],
        timestamp: str,
        status: str,
        summary: str,
        dry_run: bool,
    ) -> None:
        """Process phase and stage tags."""
        for tag in phase_tags + stage_tags:
            entity_name = self._tag_to_entity_name(tag)
            entity_type = "Phase" if tag.startswith("phase") else "Stage"
            if self.km.entity_exists(entity_name):
                observations = self._create_atomic_observations(
                    timestamp, status, summary
                )
                for obs in observations:
                    self.km.add_observation(entity_name, obs, dry_run=dry_run)
            else:
                obs = f"[{timestamp}] Status: {status}"
                self.km.add_entity(
                    entity_name,
                    entity_type,
                    observation=obs,
                    dry_run=dry_run,
                )

    def _process_components(self, summary: str, timestamp: str, dry_run: bool) -> None:
        """Process component mentions in summary."""
        components = self._extract_components(summary)
        for component in components:
            component_name = self._mcp_component_name(component)
            if self.km.entity_exists(component_name):
                obs = f"[{timestamp}] {summary[:100]}..."
                self.km.add_observation(
                    component_name,
                    obs,
                    dry_run=dry_run,
                )
            else:
                self.km.add_entity(
                    component_name,
                    "Component",
                    observation=(f"[{timestamp}] First mentioned in progress"),
                    dry_run=dry_run,
                )

    def _tag_to_entity_name(self, tag: str) -> str:
        """Convert a tag like 'phase5.1' to 'Phase 5.1'."""
        if tag.startswith("phase"):
            parts = tag.replace("phase", "").split(".")
            if len(parts) == 1:
                return f"Phase {parts[0]}"
            else:
                return f"Phase {parts[0]}.{parts[1]}"
        elif tag.startswith("stage"):
            num = tag.replace("stage", "").replace("_", ".")
            return f"Stage {num}"
        return tag

    def _mcp_component_name(self, component: str) -> str:
        """Convert component name to MCP convention."""
        component = component.replace(" class", "").replace(" component", "")
        return component.strip().replace(" ", "_")

    def _create_atomic_observations(
        self, timestamp: str, status: str, summary: str
    ) -> List[str]:
        """Create atomic observations following MCP best practices."""
        observations = [f"[{timestamp}] Status: {status}"]
        if summary:
            if "implemented" in summary.lower():
                impl_match = re.search(r"[Ii]mplemented\s+(.+?)(?:\.|,|;|$)", summary)
                if impl_match:
                    observations.append(
                        f"[{timestamp}] Implemented: {impl_match.group(1)}"
                    )
            if "fixed" in summary.lower():
                fix_match = re.search(r"[Ff]ixed\s+(.+?)(?:\.|,|;|$)", summary)
                if fix_match:
                    observations.append(f"[{timestamp}] Fixed: {fix_match.group(1)}")
            if "added" in summary.lower():
                add_match = re.search(r"[Aa]dded\s+(.+?)(?:\.|,|;|$)", summary)
                if add_match:
                    observations.append(f"[{timestamp}] Added: {add_match.group(1)}")
        return observations

    def _extract_components(self, text: str) -> List[str]:
        """Extract component names from text."""
        components: list[str] = []
        patterns = [
            (
                r"(?:Implemented|Created|Added|Updated|Fixed)"
                r"\s+(?:the\s+)?`?(\w+(?:\s+\w+)*?)`?"
                r"(?:\s+class|\s+component|\s+module)?"
            ),
            r"`(\w+(?:\s+\w+)*?)`",
            r"(?:^|\s)([A-Z]\w+(?:[A-Z]\w+)+)(?:\s|$)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            components.extend(matches)
        cleaned: list[str] = []
        for comp in components:
            comp = comp.strip()
            if (
                comp
                and len(comp) > 2
                and comp not in ["Status", "Summary", "Phase", "Stage"]
            ):
                cleaned.append(comp)
        return list(set(cleaned))

    def _process_decision(self, timestamp: str, summary: str, dry_run: bool) -> None:
        """Process architectural decisions with MCP decision type."""
        if summary:
            decision_match = re.search(r"[Dd]ecided\s+(?:to\s+)?(.+?)(?:\.|$)", summary)
            if decision_match:
                date_part = timestamp.split()[0]
                decision_name = f"Decision_{date_part}"
                self.km.add_entity(
                    decision_name,
                    "decision",
                    observation=f"[{timestamp}] {decision_match.group(1)}",
                    dry_run=dry_run,
                )


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse ai_docs.md progress entries")
    parser.add_argument("file", help="Path to ai_docs.md")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing"
    )
    args = parser.parse_args()
    km = KnowledgeGraphManager()
    parser_obj = AIDocsParser(km)
    parser_obj.parse_file(Path(args.file), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
