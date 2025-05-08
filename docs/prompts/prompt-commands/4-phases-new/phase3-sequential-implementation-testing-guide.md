# Phase 3: Sequential Implementation and Testing Guide (Cloud Integration)

This document provides a complete sequential implementation and testing workflow for Phase 3 (Cloud Integration + Extended Search) of the Panoptikon file search application. Each step includes both implementation and testing instructions for Cursor. Follow these steps in exact order.

## Initial Setup and Documentation Review

1. **Review specification documentation**:
   - Read the project specification in detail, particularly section 2.1.4 on Cloud Storage Integration
   - Review the implementation plan for Phase 3 requirements
   - Study the specification section 2.2.2 for Advanced Search Capabilities
   - Understand the full cloud provider requirements from the specification

2. **Verify Phase 1 and Phase 2 components**:
   - Ensure all prior components are complete and passing tests
   - Understand the interfaces provided by existing components
   - Verify the database schema supports cloud metadata

3. **Examine cloud provider APIs**:
   - Research the APIs for each required cloud provider:
     - iCloud
     - Dropbox
     - Google Drive
     - OneDrive
     - Box
   - Understand the authentication mechanisms for each provider
   - Identify limitations and rate restrictions

## Implementation Sequence

### Step 1: Cloud Provider Detection System

#### Code: Create Cloud Provider Detection System
```
Implement the ProviderDetector in src/panoptikon/cloud/detector.py:

1. Create a cloud provider detection system that:
   - Identifies cloud storage locations based on path patterns
   - Supports all required providers (iCloud, Dropbox, Google Drive, OneDrive, Box)
   - Uses efficient path-based detection algorithms
   - Caches results for performance
   - Handles edge cases like nested cloud folders
   - Documents detection heuristics

2. Implement the following interface:

class ProviderDetector:
    """Detects cloud storage providers for file paths."""
    
    def __init__(self, cache_size: int = 1000):
        """Initialize the provider detector.
        
        Args:
            cache_size: Size of the detection cache
        """
        ...
        
    def detect_provider(self, path: Path) -> Optional[str]:
        """Detect the cloud provider for a path.
        
        Args:
            path: Path to check
            
        Returns:
            Provider name if detected, None otherwise
        """
        ...
        
    def is_cloud_path(self, path: Path) -> bool:
        """Check if a path is in cloud storage.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is in cloud storage, False otherwise
        """
        ...
        
    def get_provider_root(self, path: Path) -> Optional[Path]:
        """Get the root directory of the cloud provider.
        
        Args:
            path: Path in cloud storage
            
        Returns:
            Root path of the provider if detected, None otherwise
        """
        ...
        
    def clear_cache(self) -> None:
        """Clear the detection cache."""
        ...
```

#### Test: Verify Cloud Provider Detection System
```
Create and run tests for the ProviderDetector in tests/test_cloud/test_detector.py:

1. Write tests that verify:
   - All supported providers are detected correctly
   - Caching improves performance
   - Edge cases are handled properly
   - Non-cloud paths return None

2. Include specific test cases:
   - Test with paths for each provider
   - Test cache behavior
   - Test with nested cloud folders
   - Test with invalid paths
   - Test performance with large path sets

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/test_detector.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/test_detector.py --cov=src.panoptikon.cloud.detector
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component01.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 2: Cloud Provider Registry

#### Code: Create Cloud Provider Registry
```
Implement the ProviderRegistry in src/panoptikon/cloud/registry.py:

1. Create a cloud provider registry that:
   - Manages provider implementation registration
   - Implements dynamic provider discovery
   - Provides a clean interface for accessing providers
   - Supports multiple versions of providers
   - Uses dependency injection pattern
   - Handles provider initialization and shutdown

2. Implement the following interface:

class CloudProvider:
    """Base class for cloud providers."""
    
    @property
    def name(self) -> str:
        """Get the provider name.
        
        Returns:
            Provider name
        """
        ...
        
    def initialize(self) -> bool:
        """Initialize the provider.
        
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def shutdown(self) -> None:
        """Shut down the provider."""
        ...
        
    def get_status(self, path: Path) -> str:
        """Get the status of a cloud file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
        
    def is_path_supported(self, path: Path) -> bool:
        """Check if a path is supported by this provider.
        
        Args:
            path: Path to check
            
        Returns:
            True if supported, False otherwise
        """
        ...

class ProviderRegistry:
    """Registry for cloud providers."""
    
    def __init__(self):
        """Initialize the provider registry."""
        ...
        
    def register_provider(self, provider_class: Type[CloudProvider]) -> None:
        """Register a provider class.
        
        Args:
            provider_class: Provider class to register
        """
        ...
        
    def get_provider(self, name: str) -> Optional[CloudProvider]:
        """Get a provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance if registered, None otherwise
        """
        ...
        
    def get_provider_for_path(self, path: Path) -> Optional[CloudProvider]:
        """Get the provider for a path.
        
        Args:
            path: Path to check
            
        Returns:
            Provider instance if found, None otherwise
        """
        ...
        
    def get_all_providers(self) -> List[CloudProvider]:
        """Get all registered providers.
        
        Returns:
            List of provider instances
        """
        ...
        
    def initialize_all(self) -> None:
        """Initialize all providers."""
        ...
        
    def shutdown_all(self) -> None:
        """Shut down all providers."""
        ...
```

#### Test: Verify Cloud Provider Registry
```
Create and run tests for the ProviderRegistry in tests/test_cloud/test_registry.py:

1. Write tests that verify:
   - Provider registration works correctly
   - Getting providers by name works
   - Getting providers for paths works
   - Initialization and shutdown work

2. Include specific test cases:
   - Test registering providers
   - Test getting providers by name
   - Test getting providers for paths
   - Test initialization and shutdown
   - Test with multiple provider versions

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/test_registry.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/test_registry.py --cov=src.panoptikon.cloud.registry
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component02.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 3: Cloud Provider Framework Integration Testing

```
Implement and run integration tests for the Cloud Provider Framework in tests/integration/phase3/test_provider_framework.py:

1. Create integration tests that:
   - Verify the detector and registry work together
   - Test provider abstraction layer
   - Validate provider lifecycle management
   - Test with real file system paths

2. Include specific test scenarios:
   - Test detecting providers and getting them from registry
   - Test provider initialization and shutdown
   - Test getting status for various paths
   - Test with mixed cloud and non-cloud paths

3. Run the integration tests:
   ```
   pytest tests/integration/phase3/test_provider_framework.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - Provider detection works correctly
   - Registry manages providers properly
   - Provider lifecycle is managed correctly
   - Framework handles mixed path types

6. Create an integration report at:
   `/docs/reports/integration/phase3-provider-framework.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 4: iCloud Provider Implementation

#### Code: Create iCloud Provider Implementation
```
Implement the iCloudProvider in src/panoptikon/cloud/providers/icloud.py:

1. Create an iCloud provider that:
   - Implements the CloudProvider interface
   - Detects iCloud Drive directories
   - Determines download status of files
   - Uses optimal detection heuristics
   - Handles macOS-specific iCloud behavior
   - Implements proper caching

2. Implement the following interface:

class iCloudProvider(CloudProvider):
    """Provider for iCloud Drive."""
    
    @property
    def name(self) -> str:
        """Get the provider name.
        
        Returns:
            Provider name ('icloud')
        """
        ...
        
    def initialize(self) -> bool:
        """Initialize the provider.
        
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def shutdown(self) -> None:
        """Shut down the provider."""
        ...
        
    def get_status(self, path: Path) -> str:
        """Get the status of a cloud file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
        
    def is_path_supported(self, path: Path) -> bool:
        """Check if a path is supported by this provider.
        
        Args:
            path: Path to check
            
        Returns:
            True if supported, False otherwise
        """
        ...
        
    def get_icloud_directory(self) -> Optional[Path]:
        """Get the iCloud Drive directory.
        
        Returns:
            iCloud Drive path if found, None otherwise
        """
        ...
        
    def _check_download_status(self, path: Path) -> str:
        """Check the download status of a file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
```

#### Test: Verify iCloud Provider Implementation
```
Create and run tests for the iCloudProvider in tests/test_cloud/providers/test_icloud.py:

1. Write tests that verify:
   - iCloud paths are detected correctly
   - Status checking works
   - Provider-specific methods work
   - Caching improves performance

2. Include specific test cases:
   - Test iCloud path detection
   - Test status checking with different file states
   - Test initialization and shutdown
   - Test with invalid paths
   - Measure performance with caching

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/providers/test_icloud.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/providers/test_icloud.py --cov=src.panoptikon.cloud.providers.icloud
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component03.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 5: Dropbox Provider Implementation

#### Code: Create Dropbox Provider Implementation
```
Implement the DropboxProvider in src/panoptikon/cloud/providers/dropbox.py:

1. Create a Dropbox provider that:
   - Implements the CloudProvider interface
   - Detects Dropbox directories
   - Determines download status using Dropbox-specific attributes
   - Uses optimal detection heuristics
   - Handles cross-platform Dropbox behavior
   - Implements proper caching

2. Implement the following interface:

class DropboxProvider(CloudProvider):
    """Provider for Dropbox."""
    
    @property
    def name(self) -> str:
        """Get the provider name.
        
        Returns:
            Provider name ('dropbox')
        """
        ...
        
    def initialize(self) -> bool:
        """Initialize the provider.
        
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def shutdown(self) -> None:
        """Shut down the provider."""
        ...
        
    def get_status(self, path: Path) -> str:
        """Get the status of a cloud file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
        
    def is_path_supported(self, path: Path) -> bool:
        """Check if a path is supported by this provider.
        
        Args:
            path: Path to check
            
        Returns:
            True if supported, False otherwise
        """
        ...
        
    def get_dropbox_directory(self) -> Optional[Path]:
        """Get the Dropbox directory.
        
        Returns:
            Dropbox path if found, None otherwise
        """
        ...
        
    def _check_download_status(self, path: Path) -> str:
        """Check the download status of a file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
```

#### Test: Verify Dropbox Provider Implementation
```
Create and run tests for the DropboxProvider in tests/test_cloud/providers/test_dropbox.py:

1. Write tests that verify:
   - Dropbox paths are detected correctly
   - Status checking works
   - Provider-specific methods work
   - Caching improves performance

2. Include specific test cases:
   - Test Dropbox path detection
   - Test status checking with different file states
   - Test initialization and shutdown
   - Test with invalid paths
   - Measure performance with caching

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/providers/test_dropbox.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/providers/test_dropbox.py --cov=src.panoptikon.cloud.providers.dropbox
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component04.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 6: Google Drive Provider Implementation

#### Code: Create Google Drive Provider Implementation
```
Implement the GoogleDriveProvider in src/panoptikon/cloud/providers/gdrive.py:

1. Create a Google Drive provider that:
   - Implements the CloudProvider interface
   - Detects Google Drive directories
   - Determines download status using Drive-specific attributes
   - Uses optimal detection heuristics
   - Handles cross-platform Drive behavior
   - Implements proper caching

2. Implement the following interface:

class GoogleDriveProvider(CloudProvider):
    """Provider for Google Drive."""
    
    @property
    def name(self) -> str:
        """Get the provider name.
        
        Returns:
            Provider name ('gdrive')
        """
        ...
        
    def initialize(self) -> bool:
        """Initialize the provider.
        
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def shutdown(self) -> None:
        """Shut down the provider."""
        ...
        
    def get_status(self, path: Path) -> str:
        """Get the status of a cloud file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
        
    def is_path_supported(self, path: Path) -> bool:
        """Check if a path is supported by this provider.
        
        Args:
            path: Path to check
            
        Returns:
            True if supported, False otherwise
        """
        ...
        
    def get_gdrive_directory(self) -> Optional[Path]:
        """Get the Google Drive directory.
        
        Returns:
            Google Drive path if found, None otherwise
        """
        ...
        
    def _check_download_status(self, path: Path) -> str:
        """Check the download status of a file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
```

#### Test: Verify Google Drive Provider Implementation
```
Create and run tests for the GoogleDriveProvider in tests/test_cloud/providers/test_gdrive.py:

1. Write tests that verify:
   - Google Drive paths are detected correctly
   - Status checking works
   - Provider-specific methods work
   - Caching improves performance

2. Include specific test cases:
   - Test Google Drive path detection
   - Test status checking with different file states
   - Test initialization and shutdown
   - Test with invalid paths
   - Measure performance with caching

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/providers/test_gdrive.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/providers/test_gdrive.py --cov=src.panoptikon.cloud.providers.gdrive
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component05.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 7: OneDrive Provider Implementation

#### Code: Create OneDrive Provider Implementation
```
Implement the OneDriveProvider in src/panoptikon/cloud/providers/onedrive.py:

1. Create a OneDrive provider that:
   - Implements the CloudProvider interface
   - Detects OneDrive directories
   - Determines download status using OneDrive-specific attributes
   - Uses optimal detection heuristics
   - Handles cross-platform OneDrive behavior
   - Implements proper caching

2. Implement the following interface:

class OneDriveProvider(CloudProvider):
    """Provider for OneDrive."""
    
    @property
    def name(self) -> str:
        """Get the provider name.
        
        Returns:
            Provider name ('onedrive')
        """
        ...
        
    def initialize(self) -> bool:
        """Initialize the provider.
        
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def shutdown(self) -> None:
        """Shut down the provider."""
        ...
        
    def get_status(self, path: Path) -> str:
        """Get the status of a cloud file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
        
    def is_path_supported(self, path: Path) -> bool:
        """Check if a path is supported by this provider.
        
        Args:
            path: Path to check
            
        Returns:
            True if supported, False otherwise
        """
        ...
        
    def get_onedrive_directory(self) -> Optional[Path]:
        """Get the OneDrive directory.
        
        Returns:
            OneDrive path if found, None otherwise
        """
        ...
        
    def _check_download_status(self, path: Path) -> str:
        """Check the download status of a file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
```

#### Test: Verify OneDrive Provider Implementation
```
Create and run tests for the OneDriveProvider in tests/test_cloud/providers/test_onedrive.py:

1. Write tests that verify:
   - OneDrive paths are detected correctly
   - Status checking works
   - Provider-specific methods work
   - Caching improves performance

2. Include specific test cases:
   - Test OneDrive path detection
   - Test status checking with different file states
   - Test initialization and shutdown
   - Test with invalid paths
   - Measure performance with caching

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/providers/test_onedrive.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/providers/test_onedrive.py --cov=src.panoptikon.cloud.providers.onedrive
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component06.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 8: Box Provider Implementation

#### Code: Create Box Provider Implementation
```
Implement the BoxProvider in src/panoptikon/cloud/providers/box.py:

1. Create a Box provider that:
   - Implements the CloudProvider interface
   - Detects Box directories
   - Determines download status using Box-specific attributes
   - Uses optimal detection heuristics
   - Handles cross-platform Box behavior
   - Implements proper caching

2. Implement the following interface:

class BoxProvider(CloudProvider):
    """Provider for Box."""
    
    @property
    def name(self) -> str:
        """Get the provider name.
        
        Returns:
            Provider name ('box')
        """
        ...
        
    def initialize(self) -> bool:
        """Initialize the provider.
        
        Returns:
            True if successful, False otherwise
        """
        ...
        
    def shutdown(self) -> None:
        """Shut down the provider."""
        ...
        
    def get_status(self, path: Path) -> str:
        """Get the status of a cloud file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
        
    def is_path_supported(self, path: Path) -> bool:
        """Check if a path is supported by this provider.
        
        Args:
            path: Path to check
            
        Returns:
            True if supported, False otherwise
        """
        ...
        
    def get_box_directory(self) -> Optional[Path]:
        """Get the Box directory.
        
        Returns:
            Box path if found, None otherwise
        """
        ...
        
    def _check_download_status(self, path: Path) -> str:
        """Check the download status of a file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
```

#### Test: Verify Box Provider Implementation
```
Create and run tests for the BoxProvider in tests/test_cloud/providers/test_box.py:

1. Write tests that verify:
   - Box paths are detected correctly
   - Status checking works
   - Provider-specific methods work
   - Caching improves performance

2. Include specific test cases:
   - Test Box path detection
   - Test status checking with different file states
   - Test initialization and shutdown
   - Test with invalid paths
   - Measure performance with caching

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/providers/test_box.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/providers/test_box.py --cov=src.panoptikon.cloud.providers.box
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component07.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 9: Cloud File Status Tracker

#### Code: Create Cloud File Status Tracker
```
Implement the CloudStatusTracker in src/panoptikon/cloud/status.py:

1. Create a cloud file status tracker that:
   - Determines download status of cloud files
   - Works with provider-specific APIs
   - Uses heuristics when APIs are unavailable
   - Handles status changes efficiently
   - Caches results appropriately
   - Uses observer pattern for updates

2. Implement the following interface:

class StatusChangeListener:
    """Listener for cloud status changes."""
    
    def on_status_changed(self, path: Path, old_status: str, new_status: str) -> None:
        """Called when a file's status changes.
        
        Args:
            path: File path
            old_status: Old status
            new_status: New status
        """
        ...

class CloudStatusTracker:
    """Tracks the status of cloud files."""
    
    def __init__(self, provider_registry: ProviderRegistry, cache_size: int = 1000):
        """Initialize the status tracker.
        
        Args:
            provider_registry: Provider registry
            cache_size: Size of the status cache
        """
        ...
        
    def get_status(self, path: Path) -> str:
        """Get the status of a cloud file.
        
        Args:
            path: Path to check
            
        Returns:
            Status string ('downloaded', 'online', 'unknown')
        """
        ...
        
    def refresh_status(self, path: Path) -> str:
        """Refresh the status of a cloud file.
        
        Args:
            path: Path to refresh
            
        Returns:
            Updated status
        """
        ...
        
    def add_listener(self, listener: StatusChangeListener) -> None:
        """Add a status change listener.
        
        Args:
            listener: Listener to add
        """
        ...
        
    def remove_listener(self, listener: StatusChangeListener) -> None:
        """Remove a status change listener.
        
        Args:
            listener: Listener to remove
        """
        ...
        
    def clear_cache(self) -> None:
        """Clear the status cache."""
        ...
```

#### Test: Verify Cloud File Status Tracker
```
Create and run tests for the CloudStatusTracker in tests/test_cloud/test_status.py:

1. Write tests that verify:
   - Status tracking works across providers
   - Caching improves performance
   - Listeners are notified of changes
   - Status refresh works

2. Include specific test cases:
   - Test status checking with different providers
   - Test caching behavior
   - Test listener notification
   - Test status refresh
   - Measure performance with large file sets

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/test_status.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/test_status.py --cov=src.panoptikon.cloud.status
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component08.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 10: Cloud Status Integration Testing

```
Implement and run integration tests for Cloud Status in tests/integration/phase3/test_cloud_status.py:

1. Create integration tests that:
   - Verify all cloud providers work with the status tracker
   - Test status tracking across providers
   - Validate status change detection
   - Test online/offline transitions

2. Include specific test scenarios:
   - Test status tracking with each provider
   - Test listener notification across providers
   - Test with mixed cloud providers
   - Test with offline and online files

3. Run the integration tests:
   ```
   pytest tests/integration/phase3/test_cloud_status.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - Status tracking works for all providers
   - Status changes are detected properly
   - Listeners are notified correctly
   - Performance meets requirements

6. Create an integration report at:
   `/docs/reports/integration/phase3-cloud-status.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 11: Cloud Provider Integration Build

```
Create a buildable prototype with cloud provider integration:

1. Create a build script in scripts/build_phase3_cloud.py that:
   - Packages all cloud provider components
   - Creates a runnable application with cloud features
   - Sets up proper provider initialization
   - Configures logging and error handling
   - Includes basic documentation

2. Run the build script:
   ```
   python scripts/build_phase3_cloud.py
   ```

3. Test the cloud integration prototype manually:
   - Verify cloud provider detection works
   - Test status tracking with actual cloud files
   - Check integration with Phase 1 and 2 components
   - Validate offline behavior

4. Success criteria:
   - Application builds successfully
   - Cloud providers are detected correctly
   - Status tracking works with real files
   - Integration with previous phases is functional

5. Create a prototype build report at:
   `/docs/reports/builds/phase3-cloud-build.md`
   Include build details, test results, screenshots, and any issues encountered.
```

### Step 12: Cloud Filter System

#### Code: Create Cloud Filter System
```
Implement the CloudFilter in src/panoptikon/search/cloud_filter.py:

1. Create a cloud filter system that:
   - Extends the search filter system
   - Implements cloud provider filtering
   - Supports download status filtering
   - Integrates with the query parser
   - Generates optimized SQL for cloud filters
   - Uses clean extension patterns

2. Implement the following interface:

class CloudProviderFilter(Filter):
    """Filter for cloud provider."""
    
    def __init__(self, provider: str):
        """Initialize cloud provider filter.
        
        Args:
            provider: Provider name to filter by
        """
        ...
        
    def to_sql(self) -> Tuple[str, List]:
        """Convert filter to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...

class CloudStatusFilter(Filter):
    """Filter for cloud status."""
    
    def __init__(self, status: str):
        """Initialize cloud status filter.
        
        Args:
            status: Status to filter by ('downloaded', 'online')
        """
        ...
        
    def to_sql(self) -> Tuple[str, List]:
        """Convert filter to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...

class CloudFilterBuilder:
    """Builds cloud filters from query nodes."""
    
    def __init__(self):
        """Initialize the cloud filter builder."""
        ...
        
    def register_with_filter_builder(self, filter_builder: FilterBuilder) -> None:
        """Register cloud filters with the filter builder.
        
        Args:
            filter_builder: Filter builder to register with
        """
        ...
        
    def build_provider_filter(self, provider: str) -> CloudProviderFilter:
        """Build a cloud provider filter.
        
        Args:
            provider: Provider name
            
        Returns:
            Cloud provider filter
        """
        ...
        
    def build_status_filter(self, status: str) -> CloudStatusFilter:
        """Build a cloud status filter.
        
        Args:
            status: Status to filter by
            
        Returns:
            Cloud status filter
        """
        ...
```

#### Test: Verify Cloud Filter System
```
Create and run tests for the CloudFilter in tests/test_search/test_cloud_filter.py:

1. Write tests that verify:
   - Cloud provider filters work correctly
   - Status filters work correctly
   - SQL generation is optimized
   - Integration with filter builder works

2. Include specific test cases:
   - Test provider filters with different providers
   - Test status filters with different statuses
   - Test SQL generation
   - Test integration with filter builder
   - Measure filter performance

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_cloud_filter.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_cloud_filter.py --cov=src.panoptikon.search.cloud_filter
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component09.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 13: Cloud Metadata Extraction

#### Code: Create Cloud Metadata Extraction
```
Implement the CloudMetadata in src/panoptikon/cloud/metadata.py:

1. Create a cloud metadata extraction system that:
   - Extracts cloud-specific file metadata
   - Handles provider-specific attributes
   - Determines sync status efficiently
   - Caches results appropriately
   - Uses clean design patterns
   - Follows consistent interfaces

2. Implement the following interface:

class CloudMetadata:
    """Cloud-specific metadata for files."""
    
    provider: str
    status: str
    sync_date: Optional[datetime]
    
    def __init__(self, provider: str, status: str, sync_date: Optional[datetime] = None):
        """Initialize cloud metadata.
        
        Args:
            provider: Cloud provider name
            status: File status
            sync_date: Last sync date, or None
        """
        ...

class CloudMetadataExtractor:
    """Extracts cloud metadata from files."""
    
    def __init__(self, provider_registry: ProviderRegistry, status_tracker: CloudStatusTracker):
        """Initialize the cloud metadata extractor.
        
        Args:
            provider_registry: Provider registry
            status_tracker: Cloud status tracker
        """
        ...
        
    def extract(self, path: Path) -> Optional[CloudMetadata]:
        """Extract cloud metadata for a file.
        
        Args:
            path: Path to extract for
            
        Returns:
            Cloud metadata if available, None otherwise
        """
        ...
        
    def extract_batch(self, paths: List[Path]) -> Dict[Path, Optional[CloudMetadata]]:
        """Extract cloud metadata for multiple files.
        
        Args:
            paths: Paths to extract for
            
        Returns:
            Dictionary mapping paths to metadata
        """
        ...
```

#### Test: Verify Cloud Metadata Extraction
```
Create and run tests for the CloudMetadata in tests/test_cloud/test_metadata.py:

1. Write tests that verify:
   - Metadata extraction works for all providers
   - Batch extraction is efficient
   - Caching improves performance
   - Provider-specific attributes are extracted

2. Include specific test cases:
   - Test extraction for each provider
   - Test batch extraction
   - Test with non-cloud files
   - Test with different file statuses
   - Measure extraction performance

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/test_metadata.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/test_metadata.py --cov=src.panoptikon.cloud.metadata
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component10.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 14: Cloud Search Extensions

#### Code: Create Cloud Search Extensions
```
Implement the CloudSearchExtensions in src/panoptikon/search/extensions/cloud.py:

1. Create cloud search extensions that:
   - Add cloud search syntax to the parser
   - Implement special cloud operators
   - Provide cloud-aware results sorting
   - Generate optimized queries
   - Use clean extension patterns
   - Follow consistent interfaces

2. Implement the following interface:

class CloudQueryExtension:
    """Extension for cloud queries."""
    
    def __init__(self, query_parser: QueryParser, filter_builder: FilterBuilder):
        """Initialize the cloud query extension.
        
        Args:
            query_parser: Query parser to extend
            filter_builder: Filter builder to use
        """
        ...
        
    def register(self) -> None:
        """Register the extension with the parser."""
        ...
        
    def parse_cloud_filter(self, tokens: List[str]) -> QueryNode:
        """Parse a cloud filter.
        
        Args:
            tokens: Filter tokens
            
        Returns:
            Query node
        """
        ...
        
    def parse_status_filter(self, tokens: List[str]) -> QueryNode:
        """Parse a status filter.
        
        Args:
            tokens: Filter tokens
            
        Returns:
            Query node
        """
        ...

class CloudSearchExtension:
    """Extension for cloud-aware search."""
    
    def __init__(self, 
                 search_engine: SearchEngine, 
                 status_tracker: CloudStatusTracker,
                 provider_registry: ProviderRegistry):
        """Initialize the cloud search extension.
        
        Args:
            search_engine: Search engine to extend
            status_tracker: Cloud status tracker
            provider_registry: Provider registry
        """
        ...
        
    def register(self) -> None:
        """Register the extension with the search engine."""
        ...
        
    def extend_results(self, results: List[FileMetadata]) -> List[FileMetadata]:
        """Extend search results with cloud information.
        
        Args:
            results: Search results to extend
            
        Returns:
            Extended results
        """
        ...
```

#### Test: Verify Cloud Search Extensions
```
Create and run tests for the CloudSearchExtensions in tests/test_search/extensions/test_cloud.py:

1. Write tests that verify:
   - Cloud query syntax works
   - Result extension works
   - Integration with search engine works
   - Query optimization works

2. Include specific test cases:
   - Test cloud provider filter syntax
   - Test status filter syntax
   - Test result extension
   - Test with complex queries
   - Measure query performance

3. Run the tests using pytest:
   ```
   pytest tests/test_search/extensions/test_cloud.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/extensions/test_cloud.py --cov=src.panoptikon.search.extensions.cloud
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component11.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 15: Status Change Monitoring

#### Code: Create Status Change Monitoring
```
Implement the StatusChangeMonitor in src/panoptikon/cloud/monitor.py:

1. Create a status change monitoring system that:
   - Tracks cloud file status changes
   - Updates index when status changes
   - Uses efficient change detection
   - Minimizes resource usage
   - Implements observer pattern
   - Has clean error handling

2. Implement the following interface:

class StatusChangeMonitor(StatusChangeListener):
    """Monitors cloud file status changes."""
    
    def __init__(self, 
                 status_tracker: CloudStatusTracker, 
                 db_operations: DatabaseOperations,
                 poll_interval_ms: int = 5000):
        """Initialize the status change monitor.
        
        Args:
            status_tracker: Cloud status tracker
            db_operations: Database operations
            poll_interval_ms: Polling interval in milliseconds
        """
        ...
        
    def start(self) -> None:
        """Start monitoring."""
        ...
        
    def stop(self) -> None:
        """Stop monitoring."""
        ...
        
    def is_running(self) -> bool:
        """Check if monitoring is active.
        
        Returns:
            True if monitoring is active, False otherwise
        """
        ...
        
    def on_status_changed(self, path: Path, old_status: str, new_status: str) -> None:
        """Called when a file's status changes.
        
        Args:
            path: File path
            old_status: Old status
            new_status: New status
        """
        ...
        
    def _update_database(self, path: Path, status: str) -> None:
        """Update the database with the new status.
        
        Args:
            path: File path
            status: New status
        """
        ...
```

#### Test: Verify Status Change Monitoring
```
Create and run tests for the StatusChangeMonitor in tests/test_cloud/test_monitor.py:

1. Write tests that verify:
   - Status changes are detected
   - Database is updated correctly
   - Resource usage is minimal
   - Start/stop functionality works

2. Include specific test cases:
   - Test status change detection
   - Test database updates
   - Test start/stop behavior
   - Test with rapid status changes
   - Measure resource usage during monitoring

3. Run the tests using pytest:
   ```
   pytest tests/test_cloud/test_monitor.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_cloud/test_monitor.py --cov=src.panoptikon.cloud.monitor
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component12.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 16: Cloud Search Integration Testing

```
Implement and run integration tests for Cloud Search in tests/integration/phase3/test_cloud_search.py:

1. Create integration tests that:
   - Verify cloud filters work with the search engine
   - Test cloud-aware search functionality
   - Validate cloud metadata integration
   - Test with mixed local/cloud results

2. Include specific test scenarios:
   - Test searching with cloud provider filters
   - Test searching with status filters
   - Test result ranking with cloud attributes
   - Test with mixed cloud and non-cloud results

3. Run the integration tests:
   ```
   pytest tests/integration/phase3/test_cloud_search.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - Cloud filters work correctly
   - Search results include cloud information
   - Result ranking considers cloud attributes
   - Mixed results are handled properly

6. Create an integration report at:
   `/docs/reports/integration/phase3-cloud-search.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 17: Advanced Search Syntax

#### Code: Create Advanced Search Syntax
```
Implement the AdvancedSearchSyntax in src/panoptikon/search/advanced.py:

1. Create an advanced search syntax that:
   - Extends the query parser with advanced operators
   - Implements complex query structures
   - Supports wildcards and pattern matching
   - Provides helpful error messages
   - Is extensible for future enhancements
   - Uses clean parser design

2. Implement the following interface:

class AdvancedQueryParser:
    """Parser for advanced search queries."""
    
    def __init__(self, base_parser: QueryParser):
        """Initialize the advanced query parser.
        
        Args:
            base_parser: Base query parser to extend
        """
        ...
        
    def register(self) -> None:
        """Register advanced syntax with the base parser."""
        ...
        
    def parse_advanced_operator(self, operator: str, tokens: List[str]) -> QueryNode:
        """Parse an advanced operator.
        
        Args:
            operator: Operator name
            tokens: Operator tokens
            
        Returns:
            Query node
        """
        ...
        
    def parse_pattern(self, pattern: str) -> QueryNode:
        """Parse a pattern with wildcards.
        
        Args:
            pattern: Pattern string
            
        Returns:
            Query node
        """
        ...
        
    def parse_range(self, range_str: str) -> QueryNode:
        """Parse a range expression.
        
        Args:
            range_str: Range expression
            
        Returns:
            Query node
        """
        ...
```

#### Test: Verify Advanced Search Syntax
```
Create and run tests for the AdvancedSearchSyntax in tests/test_search/test_advanced.py:

1. Write tests that verify:
   - Advanced operators work correctly
   - Pattern matching works
   - Range expressions work
   - Error handling provides useful messages

2. Include specific test cases:
   - Test each advanced operator
   - Test wildcard patterns
   - Test range expressions
   - Test error handling
   - Measure parsing performance

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_advanced.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_advanced.py --cov=src.panoptikon.search.advanced
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component13.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 18: Boolean Operators Implementation

#### Code: Create Boolean Operators Implementation
```
Implement the BooleanOperators in src/panoptikon/search/boolean.py:

1. Create boolean operators implementation that:
   - Implements AND, OR, NOT operators
   - Supports operator precedence
   - Handles parentheses for grouping
   - Generates optimized SQL
   - Uses clean operator implementation
   - Provides helpful error messages

2. Implement the following interface:

class AndNode(QueryNode):
    """Logical AND node."""
    
    def __init__(self, children: List[QueryNode]):
        """Initialize AND node.
        
        Args:
            children: Child nodes
        """
        ...
        
    def to_sql(self) -> Tuple[str, List]:
        """Convert to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...

class OrNode(QueryNode):
    """Logical OR node."""
    
    def __init__(self, children: List[QueryNode]):
        """Initialize OR node.
        
        Args:
            children: Child nodes
        """
        ...
        
    def to_sql(self) -> Tuple[str, List]:
        """Convert to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...

class NotNode(QueryNode):
    """Logical NOT node."""
    
    def __init__(self, child: QueryNode):
        """Initialize NOT node.
        
        Args:
            child: Child node
        """
        ...
        
    def to_sql(self) -> Tuple[str, List]:
        """Convert to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...

class BooleanOperatorParser:
    """Parser for boolean operators."""
    
    def __init__(self, query_parser: QueryParser):
        """Initialize the boolean operator parser.
        
        Args:
            query_parser: Query parser to extend
        """
        ...
        
    def register(self) -> None:
        """Register with the query parser."""
        ...
        
    def parse_and(self, tokens: List[str]) -> AndNode:
        """Parse an AND expression.
        
        Args:
            tokens: Expression tokens
            
        Returns:
            AND node
        """
        ...
        
    def parse_or(self, tokens: List[str]) -> OrNode:
        """Parse an OR expression.
        
        Args:
            tokens: Expression tokens
            
        Returns:
            OR node
        """
        ...
        
    def parse_not(self, tokens: List[str]) -> NotNode:
        """Parse a NOT expression.
        
        Args:
            tokens: Expression tokens
            
        Returns:
            NOT node
        """
        ...
```

#### Test: Verify Boolean Operators Implementation
```
Create and run tests for the BooleanOperators in tests/test_search/test_boolean.py:

1. Write tests that verify:
   - AND operator works correctly
   - OR operator works correctly
   - NOT operator works correctly
   - Operator precedence is correct
   - SQL generation is optimized

2. Include specific test cases:
   - Test simple boolean expressions
   - Test complex nested expressions
   - Test operator precedence
   - Test SQL generation
   - Measure expression performance

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_boolean.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_boolean.py --cov=src.panoptikon.search.boolean
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component14.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 19: Size/Date Filters Implementation

#### Code: Create Size/Date Filters Implementation
```
Implement the SizeDateFilters in src/panoptikon/search/filters.py:

1. Create size and date filters that:
   - Implement filtering by file size
   - Support size unit conversion (KB, MB, GB)
   - Implement filtering by file dates
   - Support date comparison operators
   - Generate optimized SQL
   - Use clean filter implementation

2. Implement the following interface:

class SizeFilter(Filter):
    """Filter for file size."""
    
    def __init__(self, size: int, operator: str = '=', unit: str = 'B'):
        """Initialize size filter.
        
        Args:
            size: Size value
            operator: Comparison operator ('=', '<', '>', '<=', '>=')
            unit: Size unit ('B', 'KB', 'MB', 'GB')
        """
        ...
        
    def to_sql(self) -> Tuple[str, List]:
        """Convert to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...
        
    def _normalize_size(self, size: int, unit: str) -> int:
        """Normalize size to bytes.
        
        Args:
            size: Size value
            unit: Size unit
            
        Returns:
            Size in bytes
        """
        ...

class DateFilter(Filter):
    """Filter for file dates."""
    
    def __init__(self, date: datetime, operator: str = '=', field: str = 'modified_at'):
        """Initialize date filter.
        
        Args:
            date: Date value
            operator: Comparison operator ('=', '<', '>', '<=', '>=')
            field: Date field ('created_at', 'modified_at')
        """
        ...
        
    def to_sql(self) -> Tuple[str, List]:
        """Convert to SQL.
        
        Returns:
            Tuple of (sql_clause, parameters)
        """
        ...
        
    def _format_date(self, date: datetime) -> str:
        """Format date for SQL.
        
        Args:
            date: Date value
            
        Returns:
            Formatted date
        """
        ...

class SizeDateFilterParser:
    """Parser for size and date filters."""
    
    def __init__(self, query_parser: QueryParser, filter_builder: FilterBuilder):
        """Initialize the filter parser.
        
        Args:
            query_parser: Query parser to extend
            filter_builder: Filter builder to use
        """
        ...
        
    def register(self) -> None:
        """Register with the query parser."""
        ...
        
    def parse_size_filter(self, tokens: List[str]) -> QueryNode:
        """Parse a size filter.
        
        Args:
            tokens: Filter tokens
            
        Returns:
            Query node
        """
        ...
        
    def parse_date_filter(self, tokens: List[str]) -> QueryNode:
        """Parse a date filter.
        
        Args:
            tokens: Filter tokens
            
        Returns:
            Query node
        """
        ...
```

#### Test: Verify Size/Date Filters Implementation
```
Create and run tests for the SizeDateFilters in tests/test_search/test_size_date.py:

1. Write tests that verify:
   - Size filters work with different units
   - Date filters work with different formats
   - Comparison operators work correctly
   - SQL generation is optimized
   - Filter parsing is correct

2. Include specific test cases:
   - Test size filters with various units
   - Test date filters with different formats
   - Test comparison operators
   - Test filter parsing
   - Measure filter performance

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_size_date.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_size_date.py --cov=src.panoptikon.search.filters
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component15.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 20: Search Preferences Integration

#### Code: Create Search Preferences Integration
```
Implement the SearchPreferences in src/panoptikon/search/preferences.py:

1. Create search preferences integration that:
   - Manages search configuration options
   - Persists preferences in the database
   - Provides default values
   - Handles preference validation
   - Notifies listeners of changes
   - Uses clean preference management

2. Implement the following interface:

class SearchPreferencesListener:
    """Listener for search preference changes."""
    
    def on_preferences_changed(self, preferences: 'SearchPreferences') -> None:
        """Called when preferences change.
        
        Args:
            preferences: Updated preferences
        """
        ...

class SearchPreferences:
    """Search preferences."""
    
    def __init__(self, db_operations: DatabaseOperations):
        """Initialize search preferences.
        
        Args:
            db_operations: Database operations
        """
        ...
        
    def load(self) -> None:
        """Load preferences from the database."""
        ...
        
    def save(self) -> None:
        """Save preferences to the database."""
        ...
        
    def get_case_sensitive(self) -> bool:
        """Get case sensitivity setting.
        
        Returns:
            True if case sensitive, False otherwise
        """
        ...
        
    def set_case_sensitive(self, value: bool) -> None:
        """Set case sensitivity setting.
        
        Args:
            value: New value
        """
        ...
        
    def get_default_operator(self) -> str:
        """Get default operator.
        
        Returns:
            Default operator ('AND', 'OR')
        """
        ...
        
    def set_default_operator(self, value: str) -> None:
        """Set default operator.
        
        Args:
            value: New value
        """
        ...
        
    def get_search_history_size(self) -> int:
        """Get search history size.
        
        Returns:
            History size
        """
        ...
        
    def set_search_history_size(self, value: int) -> None:
        """Set search history size.
        
        Args:
            value: New value
        """
        ...
        
    def add_listener(self, listener: SearchPreferencesListener) -> None:
        """Add a preferences listener.
        
        Args:
            listener: Listener to add
        """
        ...
        
    def remove_listener(self, listener: SearchPreferencesListener) -> None:
        """Remove a preferences listener.
        
        Args:
            listener: Listener to remove
        """
        ...
```

#### Test: Verify Search Preferences Integration
```
Create and run tests for the SearchPreferences in tests/test_search/test_preferences.py:

1. Write tests that verify:
   - Preferences are loaded and saved correctly
   - Getters and setters work
   - Listeners are notified of changes
   - Default values are provided

2. Include specific test cases:
   - Test preference loading
   - Test preference saving
   - Test getters and setters
   - Test listener notification
   - Test with invalid values

3. Run the tests using pytest:
   ```
   pytest tests/test_search/test_preferences.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_search/test_preferences.py --cov=src.panoptikon.search.preferences
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component16.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 21: Incremental Index Updates

#### Code: Create Incremental Index Updates
```
Implement the IncrementalIndexing in src/panoptikon/index/incremental.py:

1. Create incremental indexing that:
   - Updates index incrementally as files change
   - Integrates with file system monitoring
   - Optimizes database operations
   - Prioritizes changes based on type
   - Handles batch operations efficiently
   - Uses clean incremental update patterns

2. Implement the following interface:

class IndexChange:
    """Represents a change to the index."""
    
    path: Path
    change_type: str  # 'add', 'modify', 'delete'
    timestamp: datetime
    
    def __init__(self, path: Path, change_type: str):
        """Initialize index change.
        
        Args:
            path: Changed path
            change_type: Change type
        """
        ...

class IncrementalIndexer:
    """Handles incremental index updates."""
    
    def __init__(self, 
                 indexing_manager: IndexingManager, 
                 db_operations: DatabaseOperations,
                 batch_size: int = 100):
        """Initialize incremental indexer.
        
        Args:
            indexing_manager: Indexing manager
            db_operations: Database operations
            batch_size: Batch size for updates
        """
        ...
        
    def process_change(self, change: IndexChange) -> None:
        """Process a single change.
        
        Args:
            change: Index change
        """
        ...
        
    def process_changes(self, changes: List[IndexChange]) -> None:
        """Process multiple changes.
        
        Args:
            changes: List of changes
        """
        ...
        
    def process_directory_change(self, directory: Path, change_type: str) -> None:
        """Process a directory change.
        
        Args:
            directory: Directory path
            change_type: Change type
        """
        ...
        
    def _handle_addition(self, path: Path) -> None:
        """Handle file addition.
        
        Args:
            path: Added file
        """
        ...
        
    def _handle_modification(self, path: Path) -> None:
        """Handle file modification.
        
        Args:
            path: Modified file
        """
        ...
        
    def _handle_deletion(self, path: Path) -> None:
        """Handle file deletion.
        
        Args:
            path: Deleted file
        """
        ...
```

#### Test: Verify Incremental Index Updates
```
Create and run tests for the IncrementalIndexing in tests/test_index/test_incremental.py:

1. Write tests that verify:
   - File additions are processed correctly
   - File modifications are processed correctly
   - File deletions are processed correctly
   - Batch processing is efficient
   - Directory changes are handled properly

2. Include specific test cases:
   - Test with single file changes
   - Test with batch changes
   - Test with directory changes
   - Test error handling
   - Measure update performance

3. Run the tests using pytest:
   ```
   pytest tests/test_index/test_incremental.py -v
   ```

4. Fix any failing tests until all tests pass.

5. Verify quality standards:
   - Run black, ruff, and mypy on the code
   - Check docstring completeness
   - Measure test coverage (target: 80%+) using:
   ```
   pytest tests/test_index/test_incremental.py --cov=src.panoptikon.index.incremental
   ```

6. Create a progress report at:
   `/docs/reports/progress-phase3-component17.md`
   Include the test coverage metrics and any issues found during testing.
```

### Step 22: Advanced Search Integration Testing

```
Implement and run integration tests for Advanced Search in tests/integration/phase3/test_advanced_search.py:

1. Create integration tests that:
   - Verify all advanced search features work together
   - Test boolean operators and filters
   - Validate complex query performance
   - Test incremental indexing integration

2. Include specific test scenarios:
   - Test complex queries with multiple operators
   - Test size and date filters
   - Test incremental indexing with search
   - Test search preferences integration
   - Test performance with large indexes

3. Run the integration tests:
   ```
   pytest tests/integration/phase3/test_advanced_search.py -v
   ```

4. Debug and fix any integration issues until all tests pass.

5. Success criteria:
   - Complex queries work correctly
   - Filters work with boolean operators
   - Incremental indexing keeps search results current
   - Performance meets requirements

6. Create an integration report at:
   `/docs/reports/integration/phase3-advanced-search.md`
   Include detailed findings, metrics, and any issues encountered.
```

### Step 23: Complete Phase 3 Build

```
Create a buildable version of the complete Phase 3 implementation:

1. Create a build script in scripts/build_phase3_complete.py that:
   - Packages all Phase 3 components
   - Creates a runnable application with all features
   - Sets up proper cloud provider integration
   - Includes advanced search functionality
   - Configures incremental indexing
   - Includes comprehensive documentation

2. Run the build script:
   ```
   python scripts/build_phase3_complete.py
   ```

3. Test the complete implementation manually:
   - Verify cloud integration works with real files
   - Test advanced search features
   - Check incremental indexing with file changes
   - Validate integration with previous phases
   - Test performance with large file collections

4. Success criteria:
   - Application builds successfully
   - Cloud integration works with real files
   - Advanced search features work correctly
   - Incremental indexing responds to file changes
   - Performance meets requirements

5. Create a complete build report at:
   `/docs/reports/builds/phase3-complete-build.md`
   Include build details, test results, screenshots, and any issues encountered.
```

### Step 24: Phase 3 Comprehensive Testing

```
Implement and run comprehensive tests for the complete Phase 3 application in tests/application/test_phase3_application.py:

1. Create application tests that:
   - Verify the entire application works end-to-end
   - Test all Phase 3 features together
   - Validate performance requirements
   - Test with substantial data volumes
   - Verify integration with previous phases

2. Include specific test scenarios:
   - Test cloud integration with real providers
   - Test advanced search with complex queries
   - Test incremental indexing with file changes
   - Test search preferences with UI integration
   - Test performance under load

3. Run the application tests:
   ```
   pytest tests/application/test_phase3_application.py -v
   ```

4. Debug and fix any application issues until all tests pass.

5. Success criteria:
   - All application tests pass
   - Cloud integration works seamlessly
   - Advanced search provides accurate results
   - Incremental indexing keeps the index current
   - Performance meets requirements

6. Create a final phase report at:
   `/docs/reports/phase3_completion_report.md`
   Include comprehensive metrics, performance results, and an overview of the implementation.
```

## Implementation Notes

1. **Starting Incrementally**: Implement one component at a time, fully testing each before proceeding.
2. **Quality First**: Never compromise on quality standards.
3. **Cloud Integration Focus**:
   - Test with actual cloud storage when possible
   - Implement graceful degradation for offline operation
   - Handle provider-specific behaviors carefully
4. **Advanced Search Focus**:
   - Ensure parser correctness for complex queries
   - Test with realistic search patterns
   - Maintain search performance with complex filters

## Progress Tracking

Create a project board that tracks:
1. Components completed with test coverage metrics
2. Integration test results
3. Performance benchmarks for cloud operations
4. Outstanding issues and technical debt

Update this board after each component and integration test is completed.
