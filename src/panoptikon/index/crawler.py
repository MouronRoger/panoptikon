"""File system crawler module.

This module is responsible for traversing the file system to discover files
and directories.
"""

import os
from pathlib import Path
from typing import Generator, List, Optional, Set


class FileCrawler:
    """File system crawler for discovering files and directories.

    This class traverses the file system starting from specified root directories
    and collects file information for indexing.
    """

    def __init__(
        self,
        root_dirs: List[Path],
        excluded_dirs: Optional[Set[Path]] = None,
        excluded_patterns: Optional[Set[str]] = None,
    ) -> None:
        """Initialize the file crawler.

        Args:
            root_dirs: List of root directories to crawl
            excluded_dirs: Set of directories to exclude from crawling
            excluded_patterns: Set of glob patterns for files/dirs to exclude
        """
        self.root_dirs = root_dirs
        self.excluded_dirs = excluded_dirs or set()
        self.excluded_patterns = excluded_patterns or set()

    def crawl(self) -> Generator[Path, None, None]:
        """Crawl the file system and yield discovered file paths.

        Yields:
            Paths to discovered files
        """
        for root_dir in self.root_dirs:
            if not root_dir.exists() or not root_dir.is_dir():
                continue

            yield from self._crawl_directory(root_dir)

    def _crawl_directory(self, directory: Path) -> Generator[Path, None, None]:
        """Recursively crawl a directory and yield file paths.

        Args:
            directory: Directory path to crawl

        Yields:
            Paths to discovered files
        """
        try:
            for entry in os.scandir(directory):
                path = Path(entry.path)
                
                # Skip excluded directories
                if path.is_dir() and path in self.excluded_dirs:
                    continue
                
                # Check excluded patterns
                if any(path.match(pattern) for pattern in self.excluded_patterns):
                    continue
                
                if entry.is_file():
                    yield path
                elif entry.is_dir():
                    yield from self._crawl_directory(path)
        except PermissionError:
            # Skip directories we don't have permission to access
            pass 