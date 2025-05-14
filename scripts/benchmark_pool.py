#!/usr/bin/env python3
"""Benchmark script for Panoptikon ConnectionPool.

Measures connection acquisition latency and transaction throughput under various
thread counts. Outputs results to the console and to benchmark_results.md.

Usage:
    python scripts/benchmark_pool.py
"""

import os
from pathlib import Path
import statistics
import tempfile
import threading
import time
from typing import Any, List

from panoptikon.database.pool import ConnectionPool

THREAD_COUNTS = [1, 10, 50, 100]
ACQUISITIONS_PER_THREAD = 100
TRANSACTIONS_PER_THREAD = 50


def benchmark_acquisition(pool: ConnectionPool, num_threads: int) -> dict[str, Any]:
    """Benchmark connection acquisition latency."""
    latencies: List[float] = []
    errors: List[Exception] = []
    lock = threading.Lock()

    def worker() -> None:
        for _ in range(ACQUISITIONS_PER_THREAD):
            start = time.perf_counter()
            try:
                with pool.get_connection():
                    pass
                elapsed = time.perf_counter() - start
                with lock:
                    latencies.append(elapsed)
            except Exception as e:
                with lock:
                    errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return {
        "threads": num_threads,
        "acquisitions": len(latencies),
        "errors": len(errors),
        "min": min(latencies) if latencies else None,
        "mean": statistics.mean(latencies) if latencies else None,
        "max": max(latencies) if latencies else None,
        "p95": statistics.quantiles(latencies, n=100)[94]
        if len(latencies) >= 100
        else None,
    }


def benchmark_transactions(pool: ConnectionPool, num_threads: int) -> dict[str, Any]:
    """Benchmark transaction throughput and latency."""
    latencies: List[float] = []
    errors: List[Exception] = []
    lock = threading.Lock()

    def worker(thread_id: int) -> None:
        for i in range(TRANSACTIONS_PER_THREAD):
            start = time.perf_counter()
            try:
                with pool.transaction() as conn:
                    conn.execute(
                        "INSERT INTO bench (thread, iter, ts) VALUES (?, ?, ?)",
                        (thread_id, i, time.time()),
                    )
                elapsed = time.perf_counter() - start
                with lock:
                    latencies.append(elapsed)
            except Exception as e:
                with lock:
                    errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total = num_threads * TRANSACTIONS_PER_THREAD
    duration = sum(latencies)
    throughput = total / duration if duration > 0 else None
    return {
        "threads": num_threads,
        "transactions": total,
        "errors": len(errors),
        "min": min(latencies) if latencies else None,
        "mean": statistics.mean(latencies) if latencies else None,
        "max": max(latencies) if latencies else None,
        "p95": statistics.quantiles(latencies, n=100)[94]
        if len(latencies) >= 100
        else None,
        "throughput_tps": throughput,
    }


def write_markdown(results: List[dict[str, Any]], section: str, filename: str) -> None:
    """Write benchmark results to a Markdown file."""

    def fmt(val: Any) -> str:
        if isinstance(val, float):
            return f"{val:.6f}"
        if val is None:
            return ""
        return str(val)

    with open(filename, "a") as f:
        f.write(f"\n## {section}\n\n")
        f.write(
            "| Threads | Ops | Errors | Min (s) | Mean (s) | Max (s) | P95 (s) | Throughput (ops/s) |\n"
        )
        f.write(
            "|---------|-----|--------|---------|----------|---------|---------|--------------------|\n"
        )
        for r in results:
            f.write(
                f"| {fmt(r['threads'])} | {fmt(r.get('acquisitions', r.get('transactions')))} | {fmt(r['errors'])} | "
                f"{fmt(r['min'])} | {fmt(r['mean'])} | {fmt(r['max'])} | {fmt(r['p95'])} | "
                f"{fmt(r.get('throughput_tps', None))} |\n"
            )


def main() -> None:
    """Run connection pool benchmarks and output results to Markdown."""
    print("Running connection pool benchmarks...")
    md_file = "benchmark_results.md"
    if os.path.exists(md_file):
        os.remove(md_file)
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "bench.db"
        pool = ConnectionPool(db_path=db_path, max_connections=100, min_connections=1)
        pool.initialize()
        # Create a table for transaction benchmarks
        with pool.get_connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS bench (thread INTEGER, iter INTEGER, ts REAL)"
            )
        # Acquisition benchmarks
        acq_results = []
        for n in THREAD_COUNTS:
            print(f"[Acquisition] Threads: {n}")
            res = benchmark_acquisition(pool, n)
            acq_results.append(res)
            print(res)
        write_markdown(acq_results, "Connection Acquisition Latency", md_file)
        # Transaction benchmarks
        txn_results = []
        for n in THREAD_COUNTS:
            print(f"[Transaction] Threads: {n}")
            res = benchmark_transactions(pool, n)
            txn_results.append(res)
            print(res)
        write_markdown(txn_results, "Transaction Throughput and Latency", md_file)
        pool.shutdown()
    print(f"Benchmark results written to {md_file}")


if __name__ == "__main__":
    main()
