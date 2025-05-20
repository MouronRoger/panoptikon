# Stage 6.5: File System Monitoring

## Overview

The File System Monitoring module provides real-time awareness of file system changes to trigger incremental updates. This critical component must reliably detect file creation, modification, deletion, and movement across local and network storage while handling edge cases and failures gracefully.

## Objectives

- Implement reliable FSEvents-based file system monitoring
- Create fallback monitoring mechanisms for resilience
- Build efficient event processing with coalescing and filtering
- Implement verification strategies for network storage

## Implementation Tasks

### 1. FSEvents Integration

- Implement FSEvents wrapper:
  ```python
  class FSEventsWrapper:
      """Wrapper for macOS FSEvents API with error handling."""
      
      def __init__(self, callback):
          self.callback = callback
          self.stream_refs = {}  # Path -> FSEventStreamRef
          
      def start_monitoring(self, path):
          """Start monitoring a directory path."""
          try:
              # Create FSEvents stream
              stream_ref = self._create_fs_stream(path)
              
              # Schedule with runloop
              FSEventStreamScheduleWithRunLoop(stream_ref, 
                                              CFRunLoopGetCurrent(),
                                              kCFRunLoopDefaultMode)
              
              # Start the stream
              if not FSEventStreamStart(stream_ref):
                  raise RuntimeError(f"Failed to start FSEvents stream for {path}")
                  
              self.stream_refs[path] = stream_ref
              return True
          except Exception as e:
              # Log error and return False to trigger fallback
              return False
              
      def _event_callback(self, stream_ref, client_info, num_events,
                         event_paths, event_flags, event_ids):
          """Process FSEvents callbacks."""
          events = []
          for i in range(num_events):
              path = event_paths[i]
              flags = event_flags[i]
              
              # Convert to standardized event format
              event_type = self._determine_event_type(flags)
              events.append({
                  'path': path,
                  'type': event_type,
                  'flags': flags
              })
              
          # Forward events to registered callback
          self.callback(events)
  ```

- Create error handling:
  - Detect and recover from FSEvents failures
  - Implement reconnection logic
  - Handle resource limitations

- Build event normalization:
  - Standardize event formats
  - Resolve symbolic links
  - Handle folder vs. file events

### 2. Fallback Monitoring

- Implement polling-based alternative:
  - Create efficient directory snapshot mechanism
  - Implement diff-based change detection
  - Optimize polling frequency based on activity

- Create automatic fallback switching:
  - Detect FSEvents failures
  - Seamlessly transition to polling
  - Attempt recovery of primary monitoring

- Build monitoring strategy selection:
  - Use FSEvents for local volumes
  - Use polling for network storage
  - Support hybrid approaches for complex setups

### 3. Event Processing

- Implement event coalescing:
  ```python
  def coalesce_events(events, window_ms=500):
      """Coalesce multiple events on the same path."""
      result = {}  # path -> event
      
      for event in events:
          path = event['path']
          event_type = event['type']
          
          if path not in result:
              result[path] = event
          else:
              # Determine the effective event type based on sequence
              result[path] = determine_effective_event(result[path], event)
              
      return list(result.values())
  ```

- Create event filtering:
  - Apply path rules to events
  - Filter redundant events
  - Apply priority based on path importance

- Build prioritized processing:
  - Process user-focused directories first
  - Implement queue management
  - Throttle processing for system health

### 4. Shadow Verification

- Implement verification for network volumes:
  - Create lightweight snapshot of network directories
  - Implement periodic consistency checking
  - Detect missed events through comparison

- Create missed event detection:
  - Implement periodic full scans of critical directories
  - Detect and synthesize missed events
  - Update index with discovered changes

- Build recovery mechanisms:
  - Trigger targeted rescans when inconsistencies found
  - Implement self-healing for index
  - Create corruption detection and recovery

## Testing Requirements

1. **Unit Tests**
   - Test event normalization and coalescing
   - Verify fallback mechanism activation
   - Test shadow verification algorithms

2. **Integration Tests**
   - Test with various file operations:
     - File creation and deletion
     - File modification
     - Directory creation and deletion
     - File and directory moves/renames
   - Verify behavior with network volumes
   - Test fallback mechanisms under failure conditions

3. **Resilience Tests**
   - Test reconnection after FSEvents failures
   - Verify recovery from missed events
   - Test with network disconnection and reconnection

## Success Criteria

- Reliable detection of >99% of file system changes
- Successful fallback to alternative mechanisms when primary fails
- Efficient event coalescing reducing processing overhead by >50%
- Network volume changes correctly detected with verification
- Recovery from missed events within reasonable time frame
- 95% test coverage achieved
- Resource usage within constraints during continuous monitoring

## Dependencies

- **Requires**: Core Indexing Framework (Stage 6.1), Incremental Updates (Stage 6.4)
- **Required by**: Progress Tracking (Stage 6.6)

## Time Estimate

- Implementation: 3-4 days
- Testing: 2-3 days
