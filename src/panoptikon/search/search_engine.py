"""Search engine implementation for Panoptikon."""

from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any, Callable, cast

from panoptikon.search.query_parser import QueryParser, QueryPattern
from panoptikon.search.result import ResultSetImpl, SearchResult, SearchResultImpl


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
            tuple[str, int, int], tuple[int, Callable[[int, int], list[SearchResult]]]
        ] = OrderedDict()
        self._cache_lock = threading.Lock()
        self._cache_index: dict[str, list[tuple[str, int, int]]] = {}

    def search(
        self,
        query_pattern: QueryPattern,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ResultSetImpl:
        """Execute a search using the provided query pattern.

        Args:
            query_pattern: QueryPattern from QueryParser.
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            ResultSetImpl object containing matching files.
        """
        cache_key = (str(query_pattern), limit or -1, offset or 0)
        with self._cache_lock:
            if cache_key in self._cache:
                total_count, page_loader = self._cache.pop(cache_key)
                self._cache[cache_key] = (total_count, page_loader)
                return ResultSetImpl(self, query_pattern, total_count, page_loader)
        sql_cond, params = QueryParser.create_sql_condition(query_pattern)
        sql = (
            "SELECT id, name, path, extension, size, date_created, date_modified, "
            "file_type, is_directory, cloud_provider, cloud_status, indexed_at "
            "FROM files WHERE "
            f"{sql_cond} ORDER BY name LIMIT :limit OFFSET :offset"
        )
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

        def _page_loader(page_number: int, page_size: int) -> list[SearchResult]:
            page_offset = page_number * page_size
            page_params = dict(params)
            page_params["limit"] = page_size
            page_params["offset"] = page_offset
            with self._db.get_connection() as conn:
                try:
                    cur = conn.execute(sql, page_params)
                    results = [
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
                    ]
                    return cast(list[SearchResult], results)
                except Exception as e:
                    raise RuntimeError(f"Search page query failed: {e}") from e

        with self._cache_lock:
            if len(self._cache) >= self._cache_size:
                self._cache.popitem(last=False)
            self._cache[cache_key] = (total_count, _page_loader)
            if query_pattern.pattern not in self._cache_index:
                self._cache_index[query_pattern.pattern] = []
            self._cache_index[query_pattern.pattern].append(cache_key)
        return ResultSetImpl(self, query_pattern, total_count, _page_loader)

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
