"""Query parsing and SQL condition generation for Panoptikon search engine."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from panoptikon.database.query_builder import QueryBuilder
from panoptikon.filesystem.paths import PathMatchType


@dataclass(frozen=True)
class QueryPattern:
    """Represents a parsed user query pattern for filename search."""

    pattern: str
    match_type: PathMatchType
    case_sensitive: bool
    whole_word: bool
    extension: str | None = None


class QueryParserError(Exception):
    """Raised for errors in query parsing or validation."""


class QueryParser:
    """Parses user search queries into optimized patterns and SQL conditions."""

    @staticmethod
    def parse(
        query_string: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> QueryPattern:
        """Parse a query string into an optimized QueryPattern.

        Args:
            query_string: User-provided search text
            case_sensitive: Whether to match case exactly
            whole_word: Whether to match whole words only

        Returns:
            QueryPattern object representing the parsed query

        Raises:
            QueryParserError: If the pattern is invalid
        """
        if not query_string or not query_string.strip():
            raise QueryParserError("Query string is empty.")

        query = query_string.strip()
        extension = None
        # Only match extension filter if 'ext:pdf' or 'ext=pdf' (not .txt at end)
        ext_match = re.search(r"(?:ext:|ext=)([a-zA-Z0-9]+)$", query)
        if ext_match:
            extension = ext_match.group(1).lower()
            query = query[: ext_match.start()].strip()

        # Determine match type
        if "*" in query or "?" in query:
            match_type = PathMatchType.GLOB
        elif re.search(r"[\[\](){}+^$|\\]", query):
            # Only treat as regex if explicit regex metacharacters (not .)
            match_type = PathMatchType.REGEX
        else:
            match_type = PathMatchType.EXACT

        # Validate pattern
        if match_type == PathMatchType.REGEX:
            try:
                re.compile(query)
            except re.error as e:
                raise QueryParserError(f"Invalid regex pattern: {e}") from e

        return QueryPattern(
            pattern=query,
            match_type=match_type,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            extension=extension,
        )

    @staticmethod
    def create_sql_condition(
        query_pattern: QueryPattern,
        column: str = "name",
        extension_column: str = "extension",
    ) -> tuple[str, dict[str, Any]]:
        """Convert a QueryPattern into an SQL condition and parameters.

        Args:
            query_pattern: QueryPattern from parse()
            column: The DB column to match filename (default: 'name')
            extension_column: The DB column for file extension (default: 'extension')

        Returns:
            Tuple of (SQL condition string, parameters dict)
        """
        conds = []
        params: dict[str, Any] = {}
        col = QueryBuilder.safe_identifier(column)
        ext_col = QueryBuilder.safe_identifier(extension_column)

        # Handle extension filter
        if query_pattern.extension:
            conds.append(f"{ext_col} = :ext")
            params["ext"] = query_pattern.extension

        # Handle pattern
        if query_pattern.match_type == PathMatchType.EXACT:
            if query_pattern.whole_word:
                conds.append(f"{col} = :pattern")
                params["pattern"] = query_pattern.pattern
            else:
                # Substring match
                conds.append(f"{col} LIKE :pattern")
                params["pattern"] = (
                    query_pattern.pattern
                    if query_pattern.case_sensitive
                    else f"%{query_pattern.pattern}%"
                )
        elif query_pattern.match_type == PathMatchType.GLOB:
            # Convert glob to SQL LIKE
            like_pattern = query_pattern.pattern.replace("*", "%").replace("?", "_")
            if not query_pattern.case_sensitive:
                conds.append(f"LOWER({col}) LIKE LOWER(:pattern)")
                params["pattern"] = like_pattern
            else:
                conds.append(f"{col} LIKE :pattern")
                params["pattern"] = like_pattern
        elif query_pattern.match_type == PathMatchType.REGEX:
            # Use REGEXP if supported, fallback to LIKE for simple cases
            conds.append(f"{col} REGEXP :pattern")
            params["pattern"] = query_pattern.pattern
        else:
            raise QueryParserError(f"Unknown match type: {query_pattern.match_type}")

        return " AND ".join(conds), params
