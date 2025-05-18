"""Search engine implementation for Panoptikon."""

from __future__ import annotations

from collections import OrderedDict
import threading
from typing import Any, Callable, cast

from panoptikon.search.query_parser import QueryParser, QueryPattern
from panoptikon.search.result import ResultSetImpl, SearchResult, SearchResultImpl
from panoptikon.search.sorting import (
    AttributeSortCriteria,
    FolderSizeSortCriteria,
    SortCriteria,
    SortingEngine,
)


class SearchEngine:
    """High-performance search engine for executing parsed queries against the file database."""

    def __init__(self, database_connection: Any, cache_size: int = 100) -> None:
        """Initialize search engine with database connection.

        Args:
            database_connection: Connection pool or database connection object.
            cache_size: Maximum number of cached query results.
        """
        self._db = database_connection
        self._cache_size = cache_size
        self._cache: OrderedDict[
            tuple[str, int, int, str, str],
            tuple[int, Callable[[int, int], list[SearchResult]]],
        ] = OrderedDict()
        self._cache_lock = threading.Lock()
        self._cache_index: dict[str, list[tuple[str, int, int, str, str]]] = {}
        self._sorting_engine = SortingEngine()

    def _get_sorting_info(
        self,
        sort_criteria: SortCriteria | list[SortCriteria] | None,
        direction: str,
    ) -> tuple[str, list[SortCriteria]]:
        """Determine SQL ORDER BY clause and criteria list for sorting.

        Args:
            sort_criteria: SortCriteria or list of criteria (optional).
            direction: 'asc' or 'desc'.

        Returns:
            Tuple of (ORDER BY clause, criteria list).
        """
        if sort_criteria is not None:
            if isinstance(sort_criteria, SortCriteria):
                criteria_list = [sort_criteria]
            else:
                criteria_list = sort_criteria
            # Folder size support (push to DB if column exists)
            if len(criteria_list) == 1 and isinstance(
                criteria_list[0], FolderSizeSortCriteria
            ):
                # Assume 'folder_size' column exists; if not, fallback will be client-side
                order_by_clause = f"ORDER BY folder_size {direction.upper()}"
                return order_by_clause, criteria_list
            if (
                len(criteria_list) == 1
                and isinstance(criteria_list[0], AttributeSortCriteria)
                and criteria_list[0].attribute
                in {
                    "name",
                    "date_created",
                    "date_modified",
                    "size",
                    "extension",
                    "file_type",
                }
            ):
                col = criteria_list[0].attribute
                order_by_clause = f"ORDER BY {col} {direction.upper()}"
                return order_by_clause, criteria_list
        # Default fallback
        return "ORDER BY name", [] if sort_criteria is None else (
            [sort_criteria]
            if isinstance(sort_criteria, SortCriteria)
            else sort_criteria
        )

    def _make_cache_key(
        self,
        query_pattern: QueryPattern,
        limit: int | None,
        offset: int | None,
        sort_criteria: SortCriteria | list[SortCriteria] | None,
        direction: str,
    ) -> tuple[str, int, int, str, str]:
        """Construct a cache key for the search query and sorting."""
        return (
            str(query_pattern),
            limit or -1,
            offset or 0,
            str(sort_criteria) if sort_criteria else "",
            direction,
        )

    def _make_sql(
        self,
        sql_cond: str,
        order_by_clause: str,
    ) -> str:
        """Construct the SQL query for search."""
        return (
            "SELECT id, name, path, extension, size, date_created, date_modified, "
            "file_type, is_directory, cloud_provider, cloud_status, indexed_at "
            "FROM files WHERE "
            f"{sql_cond} {order_by_clause} LIMIT :limit OFFSET :offset"
        )

    def _make_page_loader(
        self,
        sql: str,
        params: dict[str, Any],
        sort_criteria: SortCriteria | list[SortCriteria] | None,
        criteria_list: list[SortCriteria],
        direction: str,
    ) -> Callable[[int, int], list[SearchResult]]:
        """Create a page loader function for the result set."""

        def _page_loader(page_number: int, page_size: int) -> list[SearchResult]:
            page_offset = page_number * page_size
            page_params = dict(params)
            page_params["limit"] = page_size
            page_params["offset"] = page_offset
            with self._db.get_connection() as conn:
                try:
                    cur = conn.execute(sql, page_params)
                    results = cast(
                        list[SearchResult],
                        [
                            SearchResultImpl(
                                name=row[1],
                                path=row[2],
                                metadata={
                                    "id": row[0],
                                    "extension": row[3],
                                    "size": row[4],
                                    "date_created": row[5],
                                    "date_modified": row[6],
                                    "file_type": row[7],
                                    "is_directory": bool(row[8]),
                                    "cloud_provider": row[9],
                                    "cloud_status": row[10],
                                    "indexed_at": row[11],
                                },
                            )
                            for row in cur.fetchall()
                        ],
                    )
                    # If we could not push sort to DB, sort client-side
                    if sort_criteria is not None:
                        if not (
                            len(criteria_list) == 1
                            and isinstance(criteria_list[0], AttributeSortCriteria)
                            and criteria_list[0].attribute
                            in {
                                "name",
                                "date_created",
                                "date_modified",
                                "size",
                                "extension",
                                "file_type",
                            }
                        ):
                            results = self._sorting_engine.apply_sort(
                                results,
                                criteria_list,
                                direction,
                            )
                    return results
                except Exception as e:
                    raise RuntimeError(f"Search page query failed: {e}") from e

        return _page_loader

    def search(
        self,
        query_pattern: QueryPattern,
        limit: int | None = None,
        offset: int | None = None,
        sort_criteria: SortCriteria | list[SortCriteria] | None = None,
        direction: str = "asc",
    ) -> ResultSetImpl:
        """Execute a search using the provided query pattern and optional sorting.

        Args:
            query_pattern: QueryPattern from QueryParser.
            limit: Maximum number of results to return.
            offset: Number of results to skip.
            sort_criteria: SortCriteria or list of criteria (optional).
            direction: 'asc' or 'desc' (default: 'asc').

        Returns:
            ResultSetImpl object containing matching files.
        """
        cache_key = self._make_cache_key(
            query_pattern, limit, offset, sort_criteria, direction
        )
        with self._cache_lock:
            if cache_key in self._cache:
                total_count, page_loader = self._cache.pop(cache_key)
                self._cache[cache_key] = (total_count, page_loader)
                return ResultSetImpl(self, query_pattern, total_count, page_loader)
        sql_cond, params = QueryParser.create_sql_condition(query_pattern)
        order_by_clause, criteria_list = self._get_sorting_info(
            sort_criteria, direction
        )
        sql = self._make_sql(sql_cond, order_by_clause)
        count_sql = f"SELECT COUNT(*) FROM files WHERE {sql_cond}"
        params_count = dict(params)
        params_count["limit"] = limit or 100
        params_count["offset"] = offset or 0
        with self._db.get_connection() as conn:
            try:
                cur = conn.execute(count_sql, params)
                total_count = int(cur.fetchone()[0])
            except Exception as e:
                raise RuntimeError(f"Search count query failed: {e}") from e
        page_loader = self._make_page_loader(
            sql, params, sort_criteria, criteria_list, direction
        )
        with self._cache_lock:
            if len(self._cache) >= self._cache_size:
                self._cache.popitem(last=False)
            self._cache[cache_key] = (total_count, page_loader)
            if query_pattern.pattern not in self._cache_index:
                self._cache_index[query_pattern.pattern] = []
            self._cache_index[query_pattern.pattern].append(cache_key)
        return ResultSetImpl(self, query_pattern, total_count, page_loader)

    def invalidate_cache(self, path: str | None = None) -> None:
        """Invalidate cache entries.

        Args:
            path: Optional path to invalidate (or all if None).
        """
        with self._cache_lock:
            if path is None:
                self._cache.clear()
                self._cache_index.clear()
            else:
                keys_to_remove = self._cache_index.get(path, [])
                for key in keys_to_remove:
                    self._cache.pop(key, None)
                self._cache_index.pop(path, None)
