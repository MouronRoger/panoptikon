"""Recursive file system crawler for indexing directories."""

import fnmatch
import logging
from pathlib import Path
from typing import Callable, Generator, List, Optional, Pattern, Set, Union
import re

logger = logging.getLogger(__name__)


class FileCrawler:
    """A recursive file system crawler that traverses directories efficiently.

    This crawler handles permissions errors gracefully, supports exclusion patterns,
    and provides progress reporting capabilities.
    """

    def __init__(
        self,
        exclude_patterns: Optional[List[str]] = None,
        follow_symlinks: bool = False,
        progress_callback: Optional[Callable[[Path], None]] = None,
    ):
        """Initialize the file crawler with configuration options.

        Args:
            exclude_patterns: List of glob patterns for directories/files to exclude
            follow_symlinks: Whether to follow symbolic links during traversal
            progress_callback: Optional callback function that receives the current path being processed
        """
        self.exclude_patterns = exclude_patterns or []
        self.follow_symlinks = follow_symlinks
        self.progress_callback = progress_callback
        self._compiled_patterns: List[Pattern] = [
            re.compile(fnmatch.translate(pattern)) for pattern in self.exclude_patterns
        ]
        self._visited_inodes: Set[int] = set()

    def _should_exclude(self, path: Path) -> bool:
        """Check if the path should be excluded based on patterns.

        Args:
            path: The path to check against exclusion patterns

        Returns:
            True if the path should be excluded, False otherwise
        """
        path_str = str(path)
        return any(pattern.match(path_str) for pattern in self._compiled_patterns)

    def _is_already_visited(self, path: Path) -> bool:
        """Check if the path has already been visited (prevents cycles).

        Args:
            path: The path to check

        Returns:
            True if the path has already been visited, False otherwise
        """
        try:
            inode = path.stat().st_ino
            if inode in self._visited_inodes:
                return True
            self._visited_inodes.add(inode)
            return False
        except (PermissionError, OSError):
            # If we can't get the inode, assume it's not visited
            return False

    def crawl(self, root_path: Union[str, Path]) -> Generator[Path, None, None]:
        """Recursively crawl the file system starting from the root path.

        Args:
            root_path: The starting directory for the crawl

        Yields:
            Each file path encountered during the crawl
        """
        root_path = Path(root_path).resolve()
        if not root_path.exists():
            logger.error(f"Path does not exist: {root_path}")
            return

        if not root_path.is_dir():
            if self.progress_callback:
                self.progress_callback(root_path)
            yield root_path
            return

        try:
            dirs_to_process = [root_path]
            
            while dirs_to_process:
                current_dir = dirs_to_process.pop()
                
                # Skip if excluded or already visited
                if self._should_exclude(current_dir) or (
                    current_dir.is_symlink() and not self.follow_symlinks
                ):
                    continue
                
                if current_dir.is_symlink() and self._is_already_visited(current_dir):
                    continue
                
                try:
                    # Process files in the current directory
                    for item in current_dir.iterdir():
                        if self._should_exclude(item):
                            continue
                            
                        if item.is_file():
                            if self.progress_callback:
                                self.progress_callback(item)
                            yield item
                        elif item.is_dir():
                            # For directories, add to the processing queue
                            dirs_to_process.append(item)
                except PermissionError:
                    logger.warning(f"Permission denied: {current_dir}")
                except OSError as e:
                    logger.warning(f"Error accessing {current_dir}: {e}")
                
                # Report progress for the directory itself
                if self.progress_callback:
                    self.progress_callback(current_dir)
                    
        except Exception as e:
            logger.error(f"Error during file crawling: {e}")


def crawl_directory(
    directory: Union[str, Path],
    exclude_patterns: Optional[List[str]] = None,
    follow_symlinks: bool = False,
    progress_callback: Optional[Callable[[Path], None]] = None,
) -> Generator[Path, None, None]:
    """Crawl a directory recursively and yield all file paths.

    This is a convenience function that creates a FileCrawler instance and
    immediately uses it to crawl the specified directory.

    Args:
        directory: The root directory to crawl
        exclude_patterns: List of glob patterns for directories/files to exclude
        follow_symlinks: Whether to follow symbolic links during traversal
        progress_callback: Optional callback function for progress reporting

    Yields:
        Each file path encountered during the crawl
    """
    crawler = FileCrawler(
        exclude_patterns=exclude_patterns,
        follow_symlinks=follow_symlinks,
        progress_callback=progress_callback,
    )
    yield from crawler.crawl(directory) 