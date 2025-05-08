"""File metadata extraction functionality."""

import datetime
import hashlib
import logging
import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Container for file metadata information."""

    path: str
    filename: str
    extension: str
    size: int
    created_at: datetime.datetime
    modified_at: datetime.datetime
    accessed_at: datetime.datetime
    is_hidden: bool
    owner: str
    checksum: Optional[str] = None

    @property
    def mime_type(self) -> str:
        """Get the MIME type for the file based on extension.

        Returns:
            The MIME type as a string, or 'application/octet-stream' if unknown
        """
        # Simple extension-based lookup, not comprehensive
        extension_map = {
            # Documents
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            
            # Images
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'svg': 'image/svg+xml',
            
            # Audio
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'flac': 'audio/flac',
            
            # Video
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mkv': 'video/x-matroska',
            
            # Code
            'py': 'text/x-python',
            'js': 'application/javascript',
            'html': 'text/html',
            'css': 'text/css',
            'json': 'application/json',
            'xml': 'application/xml',
            
            # Archives
            'zip': 'application/zip',
            'tar': 'application/x-tar',
            'gz': 'application/gzip',
            '7z': 'application/x-7z-compressed',
        }
        
        ext = self.extension.lower().lstrip('.')
        return extension_map.get(ext, 'application/octet-stream')


class MetadataExtractor:
    """Extracts metadata from files efficiently.

    This class handles different file systems and encodings,
    and provides methods to extract various metadata attributes.
    """

    def __init__(self, compute_checksum: bool = False, checksum_algorithm: str = 'md5'):
        """Initialize the metadata extractor.

        Args:
            compute_checksum: Whether to compute file checksums (resource intensive)
            checksum_algorithm: Algorithm to use for checksum calculation ('md5', 'sha1', 'sha256')
        """
        self.compute_checksum = compute_checksum
        self.checksum_algorithm = checksum_algorithm
        self._system = platform.system()

    def extract(self, file_path: Union[str, Path]) -> FileMetadata:
        """Extract metadata from the specified file.

        Args:
            file_path: Path to the file

        Returns:
            FileMetadata object containing the extracted information

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be accessed due to permissions
            OSError: For other OS-related errors
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            # Get basic file stats
            stats = path.stat()
            
            # Extract dates based on platform (different meanings on different OSes)
            if self._system == 'Windows':
                created_at = datetime.datetime.fromtimestamp(stats.st_ctime)
                modified_at = datetime.datetime.fromtimestamp(stats.st_mtime)
                accessed_at = datetime.datetime.fromtimestamp(stats.st_atime)
            else:  # Unix-like
                # On Unix, st_ctime is change time, not creation time
                # Best effort for creation time (may not be accurate on all Unix systems)
                created_at = datetime.datetime.fromtimestamp(stats.st_mtime)
                modified_at = datetime.datetime.fromtimestamp(stats.st_mtime)
                accessed_at = datetime.datetime.fromtimestamp(stats.st_atime)
                
                # For macOS, try to get actual creation time if available
                if self._system == 'Darwin':
                    try:
                        created_at = datetime.datetime.fromtimestamp(
                            path.stat().st_birthtime
                        )
                    except AttributeError:
                        # If birthtime is not available, fall back to mtime
                        pass
            
            # Compute checksum if requested
            checksum = None
            if self.compute_checksum:
                checksum = self._compute_checksum(path)

            # Determine if file is hidden
            is_hidden = self._is_hidden(path)
            
            # Get file owner
            owner = self._get_owner(path)
            
            return FileMetadata(
                path=str(path.resolve()),
                filename=path.name,
                extension=path.suffix.lower(),
                size=stats.st_size,
                created_at=created_at,
                modified_at=modified_at,
                accessed_at=accessed_at,
                is_hidden=is_hidden,
                owner=owner,
                checksum=checksum,
            )
        
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {path}: {e}")
            raise
        except OSError as e:
            logger.warning(f"OS error accessing {path}: {e}")
            raise

    def _compute_checksum(self, path: Path) -> str:
        """Compute the checksum of a file.

        Args:
            path: Path to the file

        Returns:
            Checksum string

        Raises:
            OSError: If there's an error reading the file
        """
        hash_obj = None
        if self.checksum_algorithm == 'md5':
            hash_obj = hashlib.md5()
        elif self.checksum_algorithm == 'sha1':
            hash_obj = hashlib.sha1()
        elif self.checksum_algorithm == 'sha256':
            hash_obj = hashlib.sha256()
        else:
            hash_obj = hashlib.md5()  # Default to MD5
        
        try:
            # Use buffered reading to handle large files efficiently
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except (PermissionError, OSError) as e:
            logger.warning(f"Error computing checksum for {path}: {e}")
            return "checksum_error"

    def _is_hidden(self, path: Path) -> bool:
        """Check if a file is hidden.

        Args:
            path: Path to check

        Returns:
            True if the file is hidden, False otherwise
        """
        # For Unix-like systems, hidden files start with a dot
        if path.name.startswith('.'):
            return True
            
        # For Windows systems, try to use attrib command
        if self._system == 'Windows':
            try:
                # Run attrib command to check for hidden attribute
                result = subprocess.run(
                    ["attrib", str(path)], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                # If output contains 'H' (for hidden), the file is hidden
                return 'H' in result.stdout.split()[0] if result.stdout else False
            except (subprocess.SubprocessError, IndexError, FileNotFoundError):
                # If the command fails, fall back to checking the filename
                return False
                
        return False

    def _get_owner(self, path: Path) -> str:
        """Get the owner of a file.

        Args:
            path: Path to the file

        Returns:
            Owner name or UID as string
        """
        try:
            if self._system in ('Linux', 'Darwin'):
                import pwd
                return pwd.getpwuid(path.stat().st_uid).pw_name
            elif self._system == 'Windows':
                # Getting owner on Windows requires win32 API
                # This is simplified and may not work in all cases
                import getpass
                return getpass.getuser()
            else:
                # Fall back to UID
                return str(path.stat().st_uid)
        except (ImportError, KeyError, OSError):
            # If we can't get the username, fall back to the UID
            try:
                return str(path.stat().st_uid)
            except OSError:
                return "unknown"

    def extract_batch(self, paths: list[Union[str, Path]]) -> list[FileMetadata]:
        """Extract metadata from multiple files in a batch operation.

        Args:
            paths: List of file paths to process

        Returns:
            List of FileMetadata objects
        """
        results = []
        for path in paths:
            try:
                metadata = self.extract(path)
                results.append(metadata)
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.warning(f"Error extracting metadata for {path}: {e}")
                continue
        return results


def get_file_metadata(
    file_path: Union[str, Path], compute_checksum: bool = False
) -> FileMetadata:
    """Convenience function to get metadata for a single file.

    Args:
        file_path: Path to the file
        compute_checksum: Whether to compute the file checksum

    Returns:
        FileMetadata object containing the extracted information

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be accessed due to permissions
        OSError: For other OS-related errors
    """
    extractor = MetadataExtractor(compute_checksum=compute_checksum)
    return extractor.extract(file_path) 