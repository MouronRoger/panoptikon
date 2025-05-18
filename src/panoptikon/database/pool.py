"""Connection pool management for SQLite database connections.

This module provides a thread-safe connection pool for SQLite database
connections, with health monitoring, automatic reconnection, and
transaction isolation level support.
"""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
import enum
import logging
from pathlib import Path
import sqlite3
import threading
import time
import traceback
from typing import Any, Optional, Union

from ..core.errors import DatabaseError

logger = logging.getLogger(__name__)


class ConnectionHealthStatus(enum.Enum):
    """Health status of a database connection."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class TransactionIsolationLevel(enum.Enum):
    """SQLite transaction isolation levels."""

    DEFERRED = "DEFERRED"
    IMMEDIATE = "IMMEDIATE"
    EXCLUSIVE = "EXCLUSIVE"


@dataclass
class PooledConnection:
    """A connection managed by the connection pool.

    Attributes:
        connection: The SQLite connection object.
        created_at: Time when the connection was created.
        last_used_at: Time when the connection was last used.
        last_checked_at: Time when the connection was last health-checked.
        health_status: Current health status of the connection.
        in_use: Whether the connection is currently in use.
        thread_id: ID of the thread currently using this connection, if any.
    """

    connection: sqlite3.Connection
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    last_checked_at: float = field(default_factory=time.time)
    health_status: ConnectionHealthStatus = ConnectionHealthStatus.UNKNOWN
    in_use: bool = False
    thread_id: Optional[int] = None


class ConnectionPoolError(DatabaseError):
    """Base exception for connection pool errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConnectionAcquisitionTimeout(ConnectionPoolError):
    """Raised when a connection cannot be acquired within the timeout."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConnectionHealthError(ConnectionPoolError):
    """Raised when a connection is found to be unhealthy."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PerformanceTracker:
    """Simple in-memory performance tracker for connection pool."""

    def __init__(self, window_size: int = 1000) -> None:
        self.window_size = window_size
        self.acquisition_times: deque[float] = deque(maxlen=window_size)
        self.error_counts: dict[str, int] = defaultdict(int)

    def record_acquisition(self, duration: float) -> None:
        self.acquisition_times.append(duration)

    def record_error(self, error_type: str) -> None:
        self.error_counts[error_type] += 1

    def get_percentiles(self) -> dict[str, float]:
        if not self.acquisition_times:
            return {"p50": 0, "p90": 0, "p99": 0}
        sorted_times = sorted(self.acquisition_times)
        n = len(sorted_times)
        return {
            "p50": sorted_times[n // 2],
            "p90": sorted_times[int(n * 0.9)],
            "p99": sorted_times[int(n * 0.99)],
        }


class ConnectionPool:
    """Thread-safe connection pool for SQLite connections.

    This class manages a pool of SQLite connections, providing checkout/checkin
    functionality, health monitoring, and automatic reconnection.

    Thread Safety:
        - All public methods are thread-safe unless otherwise noted.
        - Each thread is assigned its own connection when possible.
        - The pool uses a reentrant lock to protect internal state.
        - Connections are not shared between threads; attempting to use a connection
          from a different thread will result in an error from SQLite.

    Context Manager Usage:
        - Use `with pool.get_connection()` to safely acquire and release a connection.
        - Use `with pool.transaction()` to run a transaction with automatic commit/rollback.
        - Use `with pool.savepoint()` for nested transactions.

    SQLite Single-Writer Limitation:
        - SQLite allows only one writer at a time. Under high write concurrency,
          some threads may experience 'database is locked' errors or timeouts.
        - The pool will retry and recycle connections as needed, but users should
          expect write contention and handle exceptions accordingly.

    Attributes:
        db_path: Path to the SQLite database file.
        max_connections: Maximum number of connections to maintain.
        min_connections: Minimum number of connections to maintain.
        connection_timeout: Timeout for connection acquisition in seconds.
        connection_max_age: Maximum age of a connection in seconds before recycling.
        health_check_interval: Interval between health checks in seconds.
        debug_mode: Set to True to enable debug diagnostics (default: False)
    """

    def __init__(
        self,
        db_path: Path,
        max_connections: int = 10,
        min_connections: int = 1,
        connection_timeout: float = 5.0,
        connection_max_age: float = 600.0,  # 10 minutes
        health_check_interval: float = 60.0,  # 1 minute
    ) -> None:
        """Initialize the connection pool.

        Args:
            db_path: Path to the SQLite database file.
            max_connections: Maximum number of connections in the pool.
            min_connections: Minimum number of connections to maintain.
            connection_timeout: Timeout for connection acquisition in seconds.
            connection_max_age: Maximum age of a connection before recycling.
            health_check_interval: Interval between health checks in seconds.
            debug_mode: Set to True to enable debug diagnostics (default: False)

        Raises:
            ValueError: If invalid parameters are provided.
        """
        if max_connections < 1:
            raise ValueError("max_connections must be at least 1")
        if min_connections < 0 or min_connections > max_connections:
            raise ValueError(
                "min_connections must be at least 0 and not greater than max_connections"
            )
        if connection_timeout <= 0:
            raise ValueError("connection_timeout must be positive")
        if connection_max_age <= 0:
            raise ValueError("connection_max_age must be positive")
        if health_check_interval <= 0:
            raise ValueError("health_check_interval must be positive")

        self.db_path = db_path
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_timeout = connection_timeout
        self.connection_max_age = connection_max_age
        self.health_check_interval = health_check_interval
        self.debug_mode = False

        # Pool state
        self._lock = threading.RLock()
        self._idle_connections: deque[PooledConnection] = deque()
        self._active_connections: dict[int, PooledConnection] = {}
        self._shutting_down = False
        self._total_created = 0
        self._total_closed = 0

        # Thread-local storage for tracking connection state
        self._local = threading.local()

        self._performance_tracker = PerformanceTracker()
        self._total_acquisitions = 0
        self._total_timeouts = 0
        self._acquisition_times: deque[float] = deque(maxlen=1000)
        self._max_acquisition_time = 0.0
        self._failed_health_checks = 0
        self._connection_errors = 0
        self._last_error_time: Optional[float] = None
        self._peak_connections = 0
        self._connections_recycled = 0
        self._stack_traces: dict[int, Any] = {}  # For debug mode

    def initialize(self) -> None:
        """Initialize the connection pool.

        Creates the minimum number of connections.

        Raises:
            ConnectionPoolError: If there's an error initializing the pool.
        """
        logger.debug(f"Initializing connection pool for {self.db_path}")
        with self._lock:
            try:
                # Create minimum connections
                for _ in range(self.min_connections):
                    conn = self._create_connection()
                    self._idle_connections.append(conn)
                logger.info(
                    f"Connection pool initialized with {self.min_connections} connections"
                )
            except Exception as e:
                raise ConnectionPoolError(
                    f"Failed to initialize connection pool: {e}"
                ) from e

    def shutdown(self) -> None:
        """Shutdown the connection pool.

        Closes all connections and releases resources.
        """
        logger.debug("Shutting down connection pool")
        with self._lock:
            self._shutting_down = True

            # Close idle connections
            while self._idle_connections:
                conn = self._idle_connections.popleft()
                self._close_connection(conn)

            # Log warning if there are still active connections
            if self._active_connections:
                logger.warning(
                    f"Connection pool has {len(self._active_connections)} active "
                    "connections during shutdown"
                )
                # Close active connections
                for thread_id, conn in list(self._active_connections.items()):
                    self._close_connection(conn)
                    del self._active_connections[thread_id]

            logger.info(
                f"Connection pool shutdown. Created: {self._total_created}, "
                f"Closed: {self._total_closed}"
            )

    @contextmanager
    def get_connection(
        self, timeout: Optional[float] = None
    ) -> Generator[sqlite3.Connection, None, None]:
        """Get a connection from the pool.

        This method is a context manager. Use as:
            with pool.get_connection() as conn:
                ...

        Thread Safety:
            - Safe to call from multiple threads. Each thread gets its own connection.
            - Connections are not shared between threads.

        SQLite Limitation:
            - Under high concurrency, acquiring a connection may block or timeout.
            - If all connections are in use, a ConnectionAcquisitionTimeout is raised.

        Args:
            timeout: Optional timeout override for connection acquisition.

        Yields:
            A SQLite database connection.

        Raises:
            ConnectionPoolError: If there's an error getting a connection.
            ConnectionAcquisitionTimeout: If a connection couldn't be acquired within the timeout.
        """
        start = time.perf_counter()
        try:
            conn_obj = self._checkout_connection(timeout or self.connection_timeout)
            elapsed = time.perf_counter() - start
            self._total_acquisitions += 1
            self._acquisition_times.append(elapsed * 1000)
            self._performance_tracker.record_acquisition(elapsed * 1000)
            if elapsed * 1000 > self._max_acquisition_time:
                self._max_acquisition_time = elapsed * 1000
            self._peak_connections = max(
                self._peak_connections, len(self._active_connections)
            )
            logger.info(
                "pool.connection.acquired",
                extra={
                    "pool_id": id(self),
                    "acquisition_time_ms": elapsed * 1000,
                    "idle_count": len(self._idle_connections),
                    "active_count": len(self._active_connections),
                },
            )
            if self.debug_mode:
                stack = traceback.extract_stack()
                self._stack_traces[id(conn_obj)] = stack
            yield conn_obj.connection
        except ConnectionAcquisitionTimeout:
            self._total_timeouts += 1
            self._performance_tracker.record_error("timeout")
            logger.warning(
                "pool.connection.timeout",
                extra={
                    "pool_id": id(self),
                    "timeout_seconds": timeout or self.connection_timeout,
                    "active_connections": len(self._active_connections),
                },
            )
            raise
        finally:
            if "conn_obj" in locals():
                self._checkin_connection(conn_obj)

    @contextmanager
    def transaction(
        self,
        isolation_level: TransactionIsolationLevel = TransactionIsolationLevel.DEFERRED,
    ) -> Generator[sqlite3.Connection, None, None]:
        """Execute a transaction with the specified isolation level.

        This method is a context manager. Use as:
            with pool.transaction() as conn:
                ...

        Thread Safety:
            - Safe to call from multiple threads. Each thread gets its own transaction.

        SQLite Limitation:
            - Only one write transaction can be active at a time. Other threads may block or fail.
            - Use IMMEDIATE or EXCLUSIVE isolation levels to control locking behavior.

        Args:
            isolation_level: Transaction isolation level.

        Yields:
            A SQLite connection within a transaction.

        Raises:
            ConnectionPoolError: If there's an error with the transaction.
        """
        with self.get_connection() as conn:
            try:
                conn.execute(f"BEGIN {isolation_level.value}")
                yield conn
                conn.execute("COMMIT")
                logger.debug(
                    f"Transaction committed with isolation level {isolation_level.value}"
                )
            except Exception as e:
                conn.execute("ROLLBACK")
                logger.debug(f"Transaction rolled back: {e}")
                if self.debug_mode:
                    logger.debug(
                        "pool.state.transition",
                        extra={
                            "connection_id": id(conn),
                            "from_state": "active",
                            "to_state": "error",
                            "thread_id": threading.get_ident(),
                            "stack": traceback.extract_stack(),
                        },
                    )
                raise

    @contextmanager
    def savepoint(self, name: str = "") -> Generator[sqlite3.Connection, None, None]:
        """Create a savepoint for nested transactions.

        This method is a context manager. Use as:
            with pool.savepoint("sp_name") as conn:
                ...

        Thread Safety:
            - Safe to call from multiple threads. Each thread gets its own savepoint.

        SQLite Limitation:
            - Savepoints are only effective within a transaction.

        Args:
            name: Optional savepoint name. If not provided, a unique name is generated.

        Yields:
            A SQLite connection within a savepoint.

        Raises:
            ConnectionPoolError: If there's an error with the savepoint.
        """
        # Generate a unique savepoint name if not provided
        if not name:
            name = f"sp_{int(time.time() * 1000)}"

        # Get the connection (reusing one if we're already in a transaction)
        if (
            hasattr(self._local, "current_connection")
            and self._local.current_connection
        ):
            conn = self._local.current_connection
            need_checkin = False
        else:
            conn_obj = self._checkout_connection(self.connection_timeout)
            conn = conn_obj.connection
            need_checkin = True

        try:
            conn.execute(f"SAVEPOINT {name}")
            yield conn
            conn.execute(f"RELEASE {name}")
            logger.debug(f"Savepoint {name} released")
        except Exception as e:
            conn.execute(f"ROLLBACK TO {name}")
            logger.debug(f"Rolled back to savepoint {name}: {e}")
            raise
        finally:
            if need_checkin:
                self._checkin_connection(conn_obj)

    def execute(
        self,
        query: str,
        parameters: Optional[Union[tuple[object, ...], dict[str, object]]] = None,
    ) -> sqlite3.Cursor:
        """Execute a SQL query with parameters.

        Thread Safety:
            - Safe to call from multiple threads.

        SQLite Limitation:
            - Write queries may fail under high concurrency due to SQLite's single-writer limitation.

        Args:
            query: The SQL query to execute.
            parameters: Optional parameters for the query.

        Returns:
            A SQLite cursor with the query results.

        Raises:
            ConnectionPoolError: If there's an error executing the query.
        """
        with self.get_connection() as conn:
            try:
                if parameters is None:
                    return conn.execute(query)
                return conn.execute(query, parameters)
            except sqlite3.Error as e:
                raise ConnectionPoolError(
                    f"Error executing query: {e}, Query: {query}"
                ) from e

    def execute_many(
        self, query: str, parameters: list[Union[tuple[object, ...], dict[str, object]]]
    ) -> sqlite3.Cursor:
        """Execute a SQL query with multiple parameter sets.

        Thread Safety:
            - Safe to call from multiple threads.

        SQLite Limitation:
            - Write queries may fail under high concurrency due to SQLite's single-writer limitation.

        Args:
            query: The SQL query to execute.
            parameters: List of parameter sets for the query.

        Returns:
            A SQLite cursor with the query results.

        Raises:
            ConnectionPoolError: If there's an error executing the query.
        """
        with self.get_connection() as conn:
            try:
                return conn.executemany(query, parameters)
            except sqlite3.Error as e:
                raise ConnectionPoolError(
                    f"Error executing batch query: {e}, Query: {query}"
                ) from e

    def get_stats(self) -> dict[str, object]:
        """Get enhanced statistics about the connection pool."""
        with self._lock:
            return {
                # Existing metrics
                "idle_connections": len(self._idle_connections),
                "active_connections": len(self._active_connections),
                "total_created": self._total_created,
                "total_closed": self._total_closed,
                # New performance metrics
                "total_acquisitions": self._total_acquisitions,
                "total_acquisition_timeouts": self._total_timeouts,
                "avg_acquisition_time_ms": self._calculate_avg_acquisition_time(),
                "max_acquisition_time_ms": self._max_acquisition_time,
                # Health metrics
                "failed_health_checks": self._failed_health_checks,
                "connection_errors": self._connection_errors,
                "last_error_timestamp": self._last_error_time,
                # Usage patterns
                "peak_connections": self._peak_connections,
                "connections_recycled": self._connections_recycled,
                "oldest_connection_age_seconds": self._get_oldest_connection_age(),
                # Configuration
                "max_connections": self.max_connections,
                "min_connections": self.min_connections,
                "health_check_interval": self.health_check_interval,
                # Performance percentiles
                "acquisition_percentiles_ms": self._performance_tracker.get_percentiles(),
            }

    def _create_connection(self) -> PooledConnection:
        """Create a new database connection.

        Returns:
            A new pooled connection.

        Raises:
            ConnectionPoolError: If there's an error creating the connection.
        """
        try:
            # Create a new connection
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=self.connection_timeout,
                isolation_level=None,  # Use explicit transaction control
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")

            # Enable detailed error messages
            sqlite3.enable_callback_tracebacks(True)

            # Use row factory for better row access
            conn.row_factory = sqlite3.Row

            # Update stats
            self._total_created += 1

            # Create and return a pooled connection
            pooled_conn = PooledConnection(connection=conn)
            return pooled_conn

        except sqlite3.Error as e:
            raise ConnectionPoolError(f"Error creating database connection: {e}") from e

    def _close_connection(self, pooled_conn: PooledConnection) -> None:
        """Close a pooled connection.

        Args:
            pooled_conn: The pooled connection to close.
        """
        try:
            pooled_conn.connection.close()
            self._total_closed += 1
            logger.debug("Closed database connection")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")

    def _reuse_existing_connection(
        self, current_thread_id: int
    ) -> Optional[PooledConnection]:
        """Check if the thread already has a connection and return it if available."""
        if (
            hasattr(self._local, "connection_id")
            and self._local.connection_id is not None
        ):
            with self._lock:
                if self._local.connection_id in self._active_connections:
                    conn = self._active_connections[self._local.connection_id]
                    logger.debug("Reusing existing connection for current thread")
                    return conn
        return None

    def _get_idle_connection(
        self, current_thread_id: int
    ) -> Optional[PooledConnection]:
        """Get an idle connection from the pool, recycling if needed."""
        if self._idle_connections:
            conn = self._idle_connections.popleft()
            # Check if the connection is too old
            if time.time() - conn.created_at > self.connection_max_age:
                logger.debug("Recycling connection that exceeded max age")
                self._close_connection(conn)
                conn = self._create_connection()
            # Check connection health
            if self._check_connection_health(conn) != ConnectionHealthStatus.HEALTHY:
                logger.debug("Recycling unhealthy connection")
                self._close_connection(conn)
                conn = self._create_connection()
            # Mark as active and return
            conn.in_use = True
            conn.thread_id = current_thread_id
            conn.last_used_at = time.time()
            self._active_connections[current_thread_id] = conn
            self._local.connection_id = current_thread_id
            self._local.current_connection = conn.connection
            if self.debug_mode:
                logger.debug(
                    "pool.state.transition",
                    extra={
                        "connection_id": id(conn),
                        "from_state": "created",
                        "to_state": "active",
                        "thread_id": current_thread_id,
                        "stack": traceback.extract_stack(),
                    },
                )
            return conn
        return None

    def _create_and_register_connection(
        self, current_thread_id: int
    ) -> PooledConnection:
        """Create a new connection and register it as active for the current thread."""
        conn = self._create_connection()
        conn.in_use = True
        conn.thread_id = current_thread_id
        self._active_connections[current_thread_id] = conn
        self._local.connection_id = current_thread_id
        self._local.current_connection = conn.connection
        if self.debug_mode:
            logger.debug(
                "pool.state.transition",
                extra={
                    "connection_id": id(conn),
                    "from_state": "created",
                    "to_state": "active",
                    "thread_id": current_thread_id,
                    "stack": traceback.extract_stack(),
                },
            )
        return conn

    def _checkout_connection(self, timeout: float) -> PooledConnection:
        """Get a connection from the pool.

        Args:
            timeout: Maximum time to wait for a connection.

        Returns:
            A pooled connection.

        Raises:
            ConnectionPoolError: If the pool is shutting down.
            ConnectionAcquisitionTimeout: If a connection couldn't be acquired within the timeout.
        """
        start_time = time.time()
        current_thread_id = threading.get_ident()

        # Try to reuse an existing connection for this thread
        reused = self._reuse_existing_connection(current_thread_id)
        if reused:
            return reused

        while True:
            with self._lock:
                if self._shutting_down:
                    raise ConnectionPoolError("Connection pool is shutting down")

                # Try to get an idle connection
                idle = self._get_idle_connection(current_thread_id)
                if idle:
                    return idle

                # If we haven't reached max connections, create a new one
                if (
                    len(self._active_connections) + len(self._idle_connections)
                    < self.max_connections
                ):
                    return self._create_and_register_connection(current_thread_id)

            # If we've reached the timeout, raise an exception
            if time.time() - start_time > timeout:
                msg = (
                    f"Couldn't acquire a connection within {timeout} seconds. "
                    f"Active connections: {len(self._active_connections)}"
                )
                raise ConnectionAcquisitionTimeout(msg)

            # Wait and try again
            time.sleep(0.01)

    def _checkin_connection(self, conn: PooledConnection) -> None:
        """Return a connection to the pool.

        Args:
            conn: The pooled connection to return.
        """
        with self._lock:
            current_thread_id = threading.get_ident()

            # Only checkin if the connection is active and belongs to the current thread
            if conn.thread_id == current_thread_id and conn.in_use:
                # Remove from active connections
                if current_thread_id in self._active_connections:
                    del self._active_connections[current_thread_id]

                # Reset thread local
                if hasattr(self._local, "connection_id"):
                    self._local.connection_id = None
                if hasattr(self._local, "current_connection"):
                    self._local.current_connection = None

                # Return to idle pool if not shutting down
                if not self._shutting_down:
                    conn.in_use = False
                    conn.thread_id = None
                    conn.last_used_at = time.time()
                    self._idle_connections.append(conn)
                else:
                    # If shutting down, close the connection
                    self._close_connection(conn)

    def _check_connection_health(
        self, conn: PooledConnection
    ) -> ConnectionHealthStatus:
        """Check if a connection is healthy.

        Args:
            conn: The pooled connection to check.

        Returns:
            The health status of the connection.
        """
        try:
            start_time = time.time()
            conn.connection.execute("SELECT 1").fetchone()
            check_duration = time.time() - start_time
            if check_duration > 0.1:
                logger.warning(
                    "pool.health_check.slow",
                    extra={
                        "duration_ms": check_duration * 1000,
                        "connection_age": time.time() - conn.created_at,
                    },
                )
            conn.health_status = ConnectionHealthStatus.HEALTHY
            return conn.health_status
        except sqlite3.Error as e:
            self._failed_health_checks += 1
            self._connection_errors += 1
            self._last_error_time = time.time()
            logger.error(
                "pool.health_check.failed",
                extra={
                    "error": str(e),
                    "connection_age": time.time() - conn.created_at,
                },
            )
            conn.health_status = ConnectionHealthStatus.UNHEALTHY
            return conn.health_status

    def _clean_idle_connections(self) -> None:
        """Clean up idle connections that are too old or exceed minimum count."""
        with self._lock:
            # Don't do anything if we're at or below minimum connections
            total_conns = len(self._active_connections) + len(self._idle_connections)
            if total_conns <= self.min_connections:
                return

            current_time = time.time()
            to_close = []

            # Collect connections to close
            for conn in self._idle_connections:
                # Close if it's too old
                if current_time - conn.created_at > self.connection_max_age:
                    to_close.append(conn)
                # Or if we have more than minimum idle connections and it's been idle for a while
                elif (
                    total_conns > self.min_connections
                    and current_time - conn.last_used_at > 30  # 30 seconds idle
                ):
                    to_close.append(conn)
                    total_conns -= 1
                    if total_conns <= self.min_connections:
                        break

            # Remove and close collected connections
            for conn in to_close:
                if conn in self._idle_connections:
                    self._idle_connections.remove(conn)
                    self._close_connection(conn)

    def _calculate_avg_acquisition_time(self) -> float:
        if not self._acquisition_times:
            return 0.0
        return sum(self._acquisition_times) / len(self._acquisition_times)

    def _get_oldest_connection_age(self) -> float:
        now = time.time()
        if not self._idle_connections and not self._active_connections:
            return 0.0
        ages = [now - c.created_at for c in self._idle_connections]
        ages += [now - c.created_at for c in self._active_connections.values()]
        return max(ages) if ages else 0.0


class PoolManager:
    """Manager for database connection pools.

    This class creates and manages connection pools for different database paths.
    """

    def __init__(self) -> None:
        """Initialize the pool manager."""
        self._pools: dict[str, ConnectionPool] = {}
        self._lock = threading.RLock()

    def get_pool(
        self,
        db_path: Path,
        max_connections: int = 10,
        min_connections: int = 1,
        connection_timeout: float = 5.0,
        connection_max_age: float = 600.0,
        health_check_interval: float = 60.0,
    ) -> ConnectionPool:
        """Get or create a connection pool for the specified database path.

        Args:
            db_path: Path to the SQLite database file.
            max_connections: Maximum number of connections in the pool.
            min_connections: Minimum number of connections to maintain.
            connection_timeout: Timeout for connection acquisition in seconds.
            connection_max_age: Maximum age of a connection before recycling.
            health_check_interval: Interval between health checks in seconds.

        Returns:
            A connection pool for the specified database.
        """
        db_key = str(db_path.resolve())

        with self._lock:
            if db_key not in self._pools:
                pool = ConnectionPool(
                    db_path=db_path,
                    max_connections=max_connections,
                    min_connections=min_connections,
                    connection_timeout=connection_timeout,
                    connection_max_age=connection_max_age,
                    health_check_interval=health_check_interval,
                )
                pool.initialize()
                self._pools[db_key] = pool

            return self._pools[db_key]

    def shutdown_all(self) -> None:
        """Shutdown all connection pools."""
        with self._lock:
            for pool in self._pools.values():
                pool.shutdown()
            self._pools.clear()


# Global pool manager instance
_pool_manager = PoolManager()


def get_pool_manager() -> PoolManager:
    """Get the global pool manager instance.

    Returns:
        The global pool manager instance.
    """
    return _pool_manager
