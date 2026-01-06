# Database Indexing

// (// 

## Summary

Indexing is a data structure technique that speeds up data retrieval operations at the cost of additional storage and slower writes. Think of it like a book's index—instead of reading every page, you look up the index to find the right page quickly.

## Key Concepts

### Index Types

1. **Primary Index**
   - Index on primary key
   - Automatically created
   - Unique, sorted

2. **Secondary Index**
   - Index on non-primary columns
   - Multiple per table
   - Can be unique or non-unique

3. **Composite Index**
   - Index on multiple columns
   - Order matters (leftmost prefix)
   - Example: `(last_name, first_name)`

4. **Covering Index**
   - Contains all columns needed for query
   - Avoids table lookup
   - Faster queries, larger index

### Index Data Structures

1. **B-Tree Index**
   - Balanced tree structure
   - O(log n) lookup
   - Good for range queries
   - Most common type

2. **Hash Index**
   - Hash table structure
   - O(1) lookup
   - Only equality queries
   - No range queries

3. **Bitmap Index**
   - Bitmap per value
   - Good for low-cardinality columns
   - Efficient for AND/OR operations

## Why It Matters

**Query Performance:** Indexes can speed up queries by 100x or more.

**Scalability:** Without indexes, queries become slower as data grows.

**Cost Efficiency:** Faster queries = fewer database instances needed.

**User Experience:** Sub-second query responses vs multi-second waits.

## Real-World Examples

**E-commerce:** Index on `product_id`, `category`, `price` for fast product searches.

**Social Media:** Index on `user_id`, `created_at` for timeline queries.

**Search Engines:** Inverted indexes for full-text search.

**Analytics:** Columnar indexes for analytical queries.

## Tradeoffs

### Advantages
- ✅ Faster reads (10-1000x speedup)
- ✅ Enables efficient sorting
- ✅ Supports unique constraints

### Disadvantages
- ❌ Slower writes (must update index)
- ❌ Additional storage (10-30% overhead)
- ❌ Maintenance overhead
- ❌ Can slow down bulk inserts

## Design Considerations

### What to Index

**Good candidates:**
- Frequently queried columns
- Foreign keys
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY

**Avoid indexing:**
- Rarely queried columns
- Frequently updated columns
- Very small tables
- Low-cardinality columns (unless bitmap)

### Index Selection Strategy

1. **Identify slow queries:** Use query profiler
2. **Analyze query patterns:** What columns are queried?
3. **Create indexes:** Start with most impactful
4. **Monitor performance:** Measure improvement
5. **Iterate:** Add/remove based on usage

### Composite Index Order

Order matters! Put most selective column first:
```
Index (category, status)  -- Good if category is selective
Index (status, category)  -- Good if status is selective
```

## Common Mistakes

1. **Over-indexing:** Too many indexes slow down writes
2. **Under-indexing:** Missing indexes on frequently queried columns
3. **Wrong column order:** In composite indexes
4. **Indexing low-cardinality:** Not helpful (unless bitmap)
5. **Not monitoring:** Indexes become unused over time

## Performance Impact

### Without Index
```
Full table scan: O(n)
1M rows = 1M operations
```

### With Index
```
Index lookup: O(log n)
1M rows = ~20 operations
```

**Speedup: 50,000x for large tables**

## Interview Hints

When discussing indexing:
1. Identify query patterns
2. Choose appropriate index type
3. Consider composite indexes
4. Discuss tradeoffs (read vs write performance)
5. Address index maintenance
// (// 

