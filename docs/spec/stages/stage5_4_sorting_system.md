# 🔍 SEGMENT 5.4: SORTING SYSTEM

## 📋 CONTEXT
**Stage**: 5 - Search Engine
**Segment**: 5.4 - Sorting System
**Dependencies**: Result Management (Segment 5.3), Database Foundation (Stage 4)

## 🎯 OBJECTIVES
Implement a flexible, high-performance sorting system that enables efficient organization of search results by multiple criteria, with support for custom sorting functions, multi-key sorts, and dynamic sort direction.

## 📑 SPECIFICATIONS

### Core Requirements
- Implement flexible result sorting by any file attribute
- Support multi-key sort operations (primary, secondary, etc.)
- Enable both ascending and descending sort directions
- Allow custom sort functions and comparators
- Support folder size sorting for directory results
- Performance optimization for large result sets

### Technical Implementation
1. Develop SortingEngine class with clean interfaces
2. Create SortCriteria abstraction for different sort types
3. Implement database-level sorting for performance
4. Build client-side sorting for custom functions
5. Ensure sort stability for consistent results

### Performance Targets
- Sorting of 10,000 results in under 100ms
- Minimal memory overhead during sort operations
- Efficient sort application without full result materialization

## 🧪 TEST REQUIREMENTS

### Unit Tests
- Test sorting by name (ascending/descending)
- Test sorting by date (created/modified)
- Test sorting by size (including folder size)
- Test sorting by file type and extension
- Test multi-key sorting
- Test custom sort functions
- Test sorting performance with large result sets
- Test sort stability

### Integration Tests
- Test integration with result management
- Verify database-level sort optimization
- Test sorting with various result set sizes
- Verify memory usage during sorting

## 📝 IMPLEMENTATION GUIDELINES

### Key Design Principles
- Push sorting to database layer when possible
- Implement Strategy pattern for sort operations
- Use stable sorting algorithms for consistent results
- Optimize for common sort cases (name, date, size)

### Interfaces
```python
# Key interfaces (not actual implementation)
class SortCriteria:
    """Abstract base class for sort criteria"""
    
    def apply_to_query(self, query):
        """
        Apply sort to database query
        
        Args:
            query: Database query to modify
            
        Returns:
            Modified query with sort applied
        """
        pass
    
    def compare(self, result1, result2):
        """
        Compare two results for client-side sorting
        
        Args:
            result1: First SearchResult
            result2: Second SearchResult
            
        Returns:
            -1, 0, or 1 (less, equal, greater)
        """
        pass

class SortingEngine:
    """Engine for applying sorts to result sets"""
    
    def apply_sort(self, result_set, criteria, direction="asc"):
        """
        Apply sort criteria to result set
        
        Args:
            result_set: ResultSet to sort
            criteria: SortCriteria or list of criteria
            direction: "asc" or "desc"
            
        Returns:
            Sorted ResultSet
        """
        pass
    
    def create_sort_criteria(self, attribute, custom_fn=None):
        """
        Create sort criteria for specified attribute
        
        Args:
            attribute: Attribute to sort by
            custom_fn: Optional custom comparison function
            
        Returns:
            SortCriteria instance
        """
        pass
```

### Folder Size Sorting Implementation
- Implement special handling for folder size sorting
- Utilize the folder_size field from database schema
- Support efficient sorting by folder size in both directions
- Handle cases where folder size calculation is pending

### Error Handling Strategy
- Graceful fallback to client-side sorting when database sort fails
- Clear error messages for invalid sort criteria
- Recovery from sort operation timeouts

## 🏁 COMPLETION CRITERIA
- All unit tests passing
- Sorting operations under 100ms for 10k results
- Memory-efficient sorting verified
- Integration tests confirm correct behavior with result management
- Support for folder size sorting verified
- 95% code coverage
- Zero lint errors
- Documentation complete

## 📚 RESOURCES
- SQLite ORDER BY optimization
- Stable sorting algorithms
- Memory-efficient sorting strategies