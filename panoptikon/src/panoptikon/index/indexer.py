"""Indexing manager for coordinating file crawling and metadata extraction."""

import logging
import os
import queue
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional, Set, Union

from panoptikon.index.crawler import FileCrawler
from panoptikon.index.metadata import FileMetadata, MetadataExtractor

logger = logging.getLogger(__name__)


@dataclass
class IndexingProgress:
    """Container for tracking indexing progress."""

    directories_processed: int = 0
    files_processed: int = 0
    total_bytes_processed: int = 0
    current_path: Optional[str] = None
    start_time: float = 0.0
    is_complete: bool = False
    errors: int = 0

    def __post_init__(self) -> None:
        """Initialize the start time if not already set."""
        if self.start_time == 0.0:
            self.start_time = time.time()

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds.

        Returns:
            Elapsed time since indexing started
        """
        return time.time() - self.start_time

    @property
    def files_per_second(self) -> float:
        """Calculate files processed per second.

        Returns:
            Files per second rate or 0 if no time has elapsed
        """
        elapsed = self.elapsed_time
        return self.files_processed / elapsed if elapsed > 0 else 0

    @property
    def bytes_per_second(self) -> float:
        """Calculate bytes processed per second.

        Returns:
            Bytes per second rate or 0 if no time has elapsed
        """
        elapsed = self.elapsed_time
        return self.total_bytes_processed / elapsed if elapsed > 0 else 0


class IndexingManager:
    """Coordinates file crawling and metadata extraction.

    This class manages concurrent indexing operations, handles throttling,
    provides progress tracking, and ensures graceful shutdown.
    """

    def __init__(
        self,
        num_threads: int = 8,
        batch_size: int = 100,
        throttle_bytes_per_sec: Optional[int] = None,
        exclude_patterns: Optional[List[str]] = None,
        follow_symlinks: bool = False,
        compute_checksums: bool = False,
    ):
        """Initialize the indexing manager.

        Args:
            num_threads: Number of worker threads for processing files
            batch_size: Number of files to process in a batch
            throttle_bytes_per_sec: Optional throughput limit in bytes/second
            exclude_patterns: List of glob patterns for directories/files to exclude
            follow_symlinks: Whether to follow symbolic links during traversal
            compute_checksums: Whether to compute file checksums
        """
        self.num_threads = max(1, min(num_threads, os.cpu_count() or 4))
        self.batch_size = batch_size
        self.throttle_bytes_per_sec = throttle_bytes_per_sec
        self.exclude_patterns = exclude_patterns
        self.follow_symlinks = follow_symlinks
        self.compute_checksums = compute_checksums

        self._queue: queue.Queue = queue.Queue(maxsize=batch_size * 2)
        self._stop_event = threading.Event()
        self._progress = IndexingProgress()
        self._metadata_extractor = MetadataExtractor(
            compute_checksum=compute_checksums
        )
        self._lock = threading.RLock()
        self._processed_paths: Set[str] = set()

        # For throttling
        self._bytes_processed_recently = 0
        self._last_throttle_check = time.time()

        # Register signal handlers
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
        except (AttributeError, ValueError):
            # Running in a context where signals cannot be caught (e.g., Windows)
            logger.warning(
                "Unable to set signal handlers, graceful shutdown may not work"
            )

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle interrupt signals for graceful shutdown.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.stop()

    def _progress_callback(self, path: Path) -> None:
        """Update progress when a file is processed.

        Args:
            path: The path being processed
        """
        with self._lock:
            if path.is_file():
                try:
                    self._progress.files_processed += 1
                    self._progress.total_bytes_processed += path.stat().st_size
                    self._bytes_processed_recently += path.stat().st_size
                except (PermissionError, OSError):
                    pass
            else:
                self._progress.directories_processed += 1

            self._progress.current_path = str(path)

            # Apply throttling if needed
            self._throttle()

    def _throttle(self) -> None:
        """Apply throughput throttling if configured."""
        if self.throttle_bytes_per_sec is None:
            return

        now = time.time()
        time_delta = now - self._last_throttle_check

        if time_delta >= 1.0:
            # Reset the counter every second
            self._bytes_processed_recently = 0
            self._last_throttle_check = now
            return

        if self._bytes_processed_recently >= self.throttle_bytes_per_sec:
            # Sleep for the remainder of the second to throttle
            sleep_time = 1.0 - time_delta
            if sleep_time > 0:
                time.sleep(sleep_time)
                self._bytes_processed_recently = 0
                self._last_throttle_check = time.time()

    def _process_file_batch(self, paths: List[Path]) -> List[FileMetadata]:
        """Process a batch of files to extract metadata.

        Args:
            paths: List of file paths to process

        Returns:
            List of FileMetadata objects
        """
        results = []
        
        for path in paths:
            if self._stop_event.is_set():
                break
                
            try:
                str_path = str(path.resolve())
                # Skip already processed files
                if str_path in self._processed_paths:
                    continue
                    
                metadata = self._metadata_extractor.extract(path)
                results.append(metadata)
                self._processed_paths.add(str_path)
                
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.warning(f"Error processing file {path}: {e}")
                with self._lock:
                    self._progress.errors += 1
        
        return results

    def _worker(self) -> None:
        """Worker thread function that processes files from the queue."""
        batch: List[Path] = []
        
        while not self._stop_event.is_set():
            try:
                # Get a path from the queue with timeout
                path = self._queue.get(timeout=0.5)
                
                if path is None:  # Sentinel value to indicate end of work
                    self._queue.task_done()
                    break
                    
                batch.append(path)
                self._queue.task_done()
                
                # Process batch when it reaches the batch size
                if len(batch) >= self.batch_size:
                    self._process_file_batch(batch)
                    batch = []
                    
            except queue.Empty:
                # If queue is empty and we have some files in batch, process them
                if batch:
                    self._process_file_batch(batch)
                    batch = []
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")
                with self._lock:
                    self._progress.errors += 1
        
        # Process any remaining files in the batch
        if batch:
            self._process_file_batch(batch)

    def index(
        self,
        root_path: Union[str, Path],
        progress_callback: Optional[
            Callable[[IndexingProgress], None]
        ] = None,
    ) -> List[FileMetadata]:
        """Index a directory and return all extracted file metadata.

        Args:
            root_path: The root directory to index
            progress_callback: Optional callback to receive progress updates

        Returns:
            List of FileMetadata objects for all indexed files
        """
        # Reset state for a new indexing operation
        self._progress = IndexingProgress()
        self._stop_event.clear()
        self._processed_paths.clear()
        
        root_path = Path(root_path).resolve()
        if not root_path.exists():
            raise FileNotFoundError(f"Root path does not exist: {root_path}")
            
        results: List[FileMetadata] = []
        file_paths: List[Path] = []
        
        try:
            # Create the crawler
            crawler = FileCrawler(
                exclude_patterns=self.exclude_patterns,
                follow_symlinks=self.follow_symlinks,
                progress_callback=self._progress_callback,
            )
            
            # Start worker threads
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                # Submit worker function to each thread
                future_workers = [
                    executor.submit(self._worker) for _ in range(self.num_threads)
                ]
                
                # Start crawling and queuing files
                last_progress_time = time.time()
                for path in crawler.crawl(root_path):
                    if self._stop_event.is_set():
                        break
                        
                    if path.is_file():
                        self._queue.put(path)
                        file_paths.append(path)
                    
                    # Call progress callback if provided
                    now = time.time()
                    if progress_callback and now - last_progress_time >= 0.5:
                        with self._lock:
                            progress_copy = IndexingProgress(
                                directories_processed=(
                                    self._progress.directories_processed
                                ),
                                files_processed=self._progress.files_processed,
                                total_bytes_processed=(
                                    self._progress.total_bytes_processed
                                ),
                                current_path=self._progress.current_path,
                                start_time=self._progress.start_time,
                                errors=self._progress.errors,
                            )
                        progress_callback(progress_copy)
                        last_progress_time = now
                
                # Signal workers that there's no more work
                for _ in range(self.num_threads):
                    self._queue.put(None)
                
                # Wait for all work to be processed
                self._queue.join()
                
                # Wait for all worker threads to complete
                for future in future_workers:
                    future.result()
            
            # Get all the metadata from the processed files
            with self._lock:
                for path_str in self._processed_paths:
                    path = Path(path_str)
                    try:
                        metadata = self._metadata_extractor.extract(path)
                        results.append(metadata)
                    except (FileNotFoundError, PermissionError, OSError):
                        # Skip files that can't be processed
                        pass
                        
                # Mark indexing as complete
                self._progress.is_complete = True
                
                # Final progress callback
                if progress_callback:
                    progress_callback(self._progress)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error during indexing: {e}")
            self.stop()
            raise
            
        finally:
            # Always ensure threads are stopped
            self.stop()

    def stop(self) -> None:
        """Stop the indexing operation gracefully."""
        self._stop_event.set()
        
        # Clear the queue to unblock workers
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break

    @property
    def progress(self) -> IndexingProgress:
        """Get the current indexing progress.

        Returns:
            A copy of the current IndexingProgress object
        """
        with self._lock:
            return IndexingProgress(
                directories_processed=self._progress.directories_processed,
                files_processed=self._progress.files_processed,
                total_bytes_processed=self._progress.total_bytes_processed,
                current_path=self._progress.current_path,
                start_time=self._progress.start_time,
                is_complete=self._progress.is_complete,
                errors=self._progress.errors,
            )


def index_directory(
    directory: Union[str, Path],
    exclude_patterns: Optional[List[str]] = None,
    num_threads: int = 8,
    follow_symlinks: bool = False,
    compute_checksums: bool = False,
    progress_callback: Optional[Callable[[IndexingProgress], None]] = None,
) -> List[FileMetadata]:
    """Index a directory and return metadata for all files.

    This is a convenience function that creates an IndexingManager and
    immediately uses it to index the specified directory.

    Args:
        directory: The root directory to index
        exclude_patterns: List of glob patterns for directories/files to exclude
        num_threads: Number of worker threads for processing files
        follow_symlinks: Whether to follow symbolic links during traversal
        compute_checksums: Whether to compute file checksums
        progress_callback: Optional callback to receive progress updates

    Returns:
        List of FileMetadata objects for all indexed files

    Raises:
        FileNotFoundError: If the directory does not exist
    """
    indexer = IndexingManager(
        num_threads=num_threads,
        exclude_patterns=exclude_patterns,
        follow_symlinks=follow_symlinks,
        compute_checksums=compute_checksums,
    )
    return indexer.index(directory, progress_callback=progress_callback) 