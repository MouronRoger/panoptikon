"""File indexing system for Panoptikon.

This module is responsible for:
1. Crawling the file system to discover files
2. Building and maintaining the file index
3. Monitoring the file system for changes
4. Updating the index in real-time

The indexing system is designed to be efficient and scalable, with a focus on
performance and resource utilization.
"""

from panoptikon.index.indexer import index_path, index_default_paths

__all__ = ["index_path", "index_default_paths"]
