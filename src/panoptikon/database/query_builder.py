"""Query builder utilities for Panoptikon database layer.

Provides helpers for safe parameterization, SQL injection prevention, and
dynamic query composition with type safety.
"""

from __future__ import annotations

import re


class QueryBuilder:
    """Utility for building SQL queries safely and dynamically."""

    @staticmethod
    def safe_identifier(identifier: str) -> str:
        """Escape and validate SQL identifiers to prevent injection.

        Args:
            identifier: The identifier to escape.

        Returns:
            A safely quoted identifier.
        """
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier):
            raise ValueError(f"Unsafe SQL identifier: {identifier}")
        return f'"{identifier}"'

    @staticmethod
    def build_where_clause(
        conditions: dict[str, object], param_style: str = ":{name}"
    ) -> tuple[str, dict[str, object]]:
        """Build a WHERE clause from a dict of conditions.

        Args:
            conditions: Mapping of column to value.
            param_style: Parameter style (default :name).

        Returns:
            Tuple of (where_clause, parameters_dict).
        """
        clauses = []
        params = {}
        for k, v in conditions.items():
            safe_k = QueryBuilder.safe_identifier(k)
            param_name = k
            clauses.append(f"{safe_k} = {param_style.format(name=param_name)}")
            params[param_name] = v
        where_clause = " AND ".join(clauses)
        return where_clause, params

    @staticmethod
    def build_insert(
        table: str, data: dict[str, object]
    ) -> tuple[str, dict[str, object]]:
        """Build a parameterized INSERT statement.

        Args:
            table: Table name.
            data: Mapping of column to value.

        Returns:
            Tuple of (sql, parameters_dict).
        """
        columns = [QueryBuilder.safe_identifier(k) for k in data]
        param_names = [f":{k}" for k in data]
        sql = (
            f"INSERT INTO {QueryBuilder.safe_identifier(table)} "
            f"({', '.join(columns)}) VALUES ({', '.join(param_names)})"
        )
        return sql, data

    @staticmethod
    def build_update(
        table: str, data: dict[str, object], where: dict[str, object]
    ) -> tuple[str, dict[str, object]]:
        """Build a parameterized UPDATE statement.

        Args:
            table: Table name.
            data: Mapping of column to value to update.
            where: Mapping of column to value for WHERE clause.

        Returns:
            Tuple of (sql, parameters_dict).
        """
        set_clause = ", ".join(
            f"{QueryBuilder.safe_identifier(k)} = :{k}" for k in data
        )
        where_clause, where_params = QueryBuilder.build_where_clause(where)
        sql = f"UPDATE {QueryBuilder.safe_identifier(table)} SET {set_clause} WHERE {where_clause}"
        params = {**data, **where_params}
        return sql, params
