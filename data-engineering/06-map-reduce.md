# 🔄 MapReduce - Expert Guide

<div align="center">

**Master MapReduce: distributed data processing algorithm**

[![MapReduce](https://img.shields.io/badge/MapReduce-Distributed-blue?style=for-the-badge)](./)
[![Hadoop](https://img.shields.io/badge/Hadoop-Framework-green?style=for-the-badge)](./)
[![Big Data](https://img.shields.io/badge/Big%20Data-Processing-orange?style=for-the-badge)](./)

*Comprehensive guide to MapReduce: algorithm, implementation, and patterns*

</div>

---

## 🎯 MapReduce Fundamentals

<div align="center">

### What is MapReduce?

**MapReduce is a programming model for processing large datasets in parallel across distributed clusters.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🔄 Two Phases** | Map phase and Reduce phase |
| **📊 Distributed** | Processes data across cluster |
| **🛡️ Fault Tolerant** | Handles node failures |
| **📈 Scalable** | Handles petabytes of data |
| **🔀 Automatic Parallelization** | Splits work across nodes |

**Mental Model:** Think of MapReduce like a factory assembly line - Map phase processes items independently (like workers doing their tasks), then Reduce phase combines results (like assembling final products).

</div>

---

## 📚 Core Concepts

<div align="center">

### Q1: What is MapReduce and why is it used?

**A:** MapReduce is a programming model for processing large datasets in parallel.

**Why Use MapReduce:**

1. **Scalability:** Handle massive datasets
2. **Parallel Processing:** Process data in parallel
3. **Fault Tolerance:** Handles failures automatically
4. **Simple Model:** Easy to understand
5. **Distributed:** Works across clusters

**Key Benefits:**
- ✅ Scalable to petabytes
- ✅ Automatic parallelization
- ✅ Fault tolerant
- ✅ Simple programming model
- ✅ Works on commodity hardware

---

### Q2: What are the two phases of MapReduce?

**A:**

**1. Map Phase:**
- Processes input data
- Produces key-value pairs
- Runs in parallel
- Independent operations

**2. Reduce Phase:**
- Aggregates map outputs
- Groups by key
- Produces final results
- Runs in parallel

**Flow:**
```
Input → Map → Shuffle & Sort → Reduce → Output
```

**Example - Word Count:**
```
Input: "hello world hello"

Map Phase:
  ("hello", 1)
  ("world", 1)
  ("hello", 1)

Shuffle & Sort:
  ("hello", [1, 1])
  ("world", [1])

Reduce Phase:
  ("hello", 2)
  ("world", 1)
```

---

### Q3: How does MapReduce work?

**A:**

**Process:**

1. **Input Splitting:**
   - Input divided into splits
   - Each split processed by one mapper

2. **Map Phase:**
   - Each mapper processes one split
   - Produces key-value pairs
   - Runs in parallel

3. **Shuffle & Sort:**
   - Groups values by key
   - Sorts keys
   - Prepares for reduce

4. **Reduce Phase:**
   - Each reducer processes one key
   - Aggregates values
   - Produces final output

**Architecture:**
```
Input Files
  ↓
Splits (InputFormat)
  ↓
Map Tasks (parallel)
  ↓
Shuffle & Sort
  ↓
Reduce Tasks (parallel)
  ↓
Output Files
```

---

### Q4: What is the Map function?

**A:** Map function processes input and produces key-value pairs.

**Characteristics:**
- Processes one record at a time
- Independent operations
- Produces key-value pairs
- Runs in parallel

**Example:**
```python
# Map function for word count
def map_function(line):
    words = line.split()
    for word in words:
        yield (word, 1)

# Input: "hello world hello"
# Output: [("hello", 1), ("world", 1), ("hello", 1)]
```

**Map Function Signature:**
```
map(key, value) → list of (key, value) pairs
```

---

### Q5: What is the Reduce function?

**A:** Reduce function aggregates values for each key.

**Characteristics:**
- Processes one key at a time
- Receives all values for key
- Aggregates values
- Produces final output

**Example:**
```python
# Reduce function for word count
def reduce_function(key, values):
    count = sum(values)
    return (key, count)

# Input: ("hello", [1, 1])
# Output: ("hello", 2)
```

**Reduce Function Signature:**
```
reduce(key, list of values) → (key, aggregated_value)
```

---

### Q6: What is Shuffle and Sort in MapReduce?

**A:**

**Shuffle:**
- Transfers map outputs to reducers
- Groups values by key
- Network-intensive operation

**Sort:**
- Sorts keys before reduce
- Ensures keys arrive sorted
- Optimizes reduce phase

**Process:**
```
Map Outputs:
  Node 1: [("a", 1), ("b", 1)]
  Node 2: [("a", 1), ("c", 1)]

Shuffle (by key):
  "a" → [1, 1] (to reducer 1)
  "b" → [1] (to reducer 2)
  "c" → [1] (to reducer 3)

Sort:
  Keys sorted: "a", "b", "c"
```

**Cost:**
- Network I/O
- Disk I/O
- Expensive operation

---

### Q7: What is a Combiner in MapReduce?

**A:** Combiner is a local reducer that runs on map node.

**Purpose:**
- Reduce data transferred
- Optimize shuffle phase
- Local aggregation

**Example:**
```python
# Combiner (local reduce)
def combiner(key, values):
    return (key, sum(values))

# Before combiner:
# Map output: [("hello", 1), ("hello", 1), ("world", 1)]
# Shuffle: 3 records

# After combiner:
# Map output: [("hello", 2), ("world", 1)]
# Shuffle: 2 records (less data)
```

**Benefits:**
- ✅ Reduces network traffic
- ✅ Faster shuffle
- ✅ Lower costs

**Note:** Combiner is optional optimization.

---

### Q8: What is the difference between MapReduce and traditional processing?

**A:**

| Aspect | Traditional | MapReduce |
|:---:|:---:|:---:|
| **Processing** | Single machine | Distributed cluster |
| **Scalability** | Limited | Petabytes |
| **Fault Tolerance** | Manual | Automatic |
| **Parallelization** | Manual | Automatic |
| **Data Location** | Centralized | Distributed |

**Traditional:**
- Single machine
- Limited by memory/CPU
- Manual parallelization
- No fault tolerance

**MapReduce:**
- Distributed cluster
- Scales horizontally
- Automatic parallelization
- Fault tolerant

---

### Q9: What are MapReduce use cases?

**A:**

**Common Use Cases:**

1. **Word Count:**
   - Count word frequencies
   - Text analysis

2. **Log Analysis:**
   - Process server logs
   - Error analysis

3. **Data Aggregation:**
   - Sum, count, average
   - Group by operations

4. **ETL:**
   - Extract, transform, load
   - Data processing

5. **Indexing:**
   - Build search indexes
   - Inverted index

**Example - Log Analysis:**
```python
# Map: Extract error type
def map(line):
    if "ERROR" in line:
        error_type = extract_error_type(line)
        yield (error_type, 1)

# Reduce: Count errors
def reduce(key, values):
    return (key, sum(values))
```

---

### Q10: What is Hadoop MapReduce?

**A:** Hadoop MapReduce is the implementation of MapReduce in Hadoop ecosystem.

**Components:**

1. **JobTracker:**
   - Manages jobs
   - Schedules tasks
   - Monitors progress

2. **TaskTracker:**
   - Executes tasks
   - Reports status
   - Manages resources

**Architecture:**
```
JobTracker (Master)
  ├── Schedules tasks
  └── Monitors progress

TaskTrackers (Workers)
  ├── Execute map tasks
  └── Execute reduce tasks
```

**Example:**
```bash
# Submit MapReduce job
hadoop jar wordcount.jar WordCount input/ output/

# Job runs on Hadoop cluster
# MapReduce framework handles distribution
```

---

### Q11: What are MapReduce patterns?

**A:**

**Common Patterns:**

1. **Summarization:**
   - Count, sum, average
   - Aggregate data

2. **Filtering:**
   - Select records
   - Remove unwanted data

3. **Joining:**
   - Combine datasets
   - Multiple inputs

4. **Sorting:**
   - Sort by key
   - Secondary sort

5. **Iterative Processing:**
   - Multiple MapReduce jobs
   - Chain jobs

**Example - Summarization:**
```python
# Map: Extract sales amount
def map(record):
    amount = record['amount']
    yield ("total", amount)

# Reduce: Sum amounts
def reduce(key, values):
    return ("total", sum(values))
```

---

### Q12: What are the limitations of MapReduce?

**A:**

**Limitations:**

1. **Performance:**
   - Disk-based (slow)
   - Multiple disk I/O
   - Not optimal for iterative

2. **Complexity:**
   - Low-level API
   - Verbose code
   - Hard to optimize

3. **Latency:**
   - Batch processing only
   - Not real-time
   - High latency

4. **Iterative Algorithms:**
   - Multiple MapReduce jobs
   - Slow for ML algorithms

**Alternatives:**
- Spark (in-memory, faster)
- Flink (streaming)
- Tez (optimized)

---

### Q13: What is the difference between MapReduce and Spark?

**A:**

| Aspect | MapReduce | Spark |
|:---:|:---:|:---:|
| **Processing** | Disk-based | In-memory |
| **Speed** | Slower | 100x faster |
| **API** | Low-level | High-level |
| **Iterative** | Slow | Fast |
| **Streaming** | Not native | Native |

**MapReduce:**
- Disk-based processing
- Mature ecosystem
- Simple model

**Spark:**
- In-memory processing
- Faster execution
- Higher-level APIs

**When to Use:**

**MapReduce:**
- Simple batch processing
- One-time jobs
- Legacy systems

**Spark:**
- Iterative algorithms
- Real-time processing
- Complex analytics

---

### Q14: How to optimize MapReduce jobs?

**A:**

**Optimization Techniques:**

1. **Use Combiners:**
   - Reduce shuffle data
   - Local aggregation

2. **Tune Number of Reducers:**
   - Optimal reducer count
   - Avoid too many/few

3. **Compress Intermediate Data:**
   - Reduce I/O
   - Faster shuffle

4. **Filter Early:**
   - Remove unwanted data
   - Reduce processing

5. **Use Appropriate Data Formats:**
   - Binary formats (SequenceFile)
   - Compressed formats

**Example:**
```python
# Optimized: Use combiner, filter early
def map(line):
    if should_process(line):  # Filter early
        yield (key, value)

def combiner(key, values):  # Local aggregation
    return (key, aggregate(values))
```

---

### Q15: What are MapReduce best practices?

**A:**

**Best Practices:**

1. **Design for Parallelism:**
   - Independent map tasks
   - Balanced reduce tasks

2. **Minimize Shuffle:**
   - Use combiners
   - Filter early
   - Reduce data size

3. **Handle Skew:**
   - Balance reducer load
   - Custom partitioner

4. **Error Handling:**
   - Handle failures gracefully
   - Retry logic

5. **Testing:**
   - Test locally first
   - Use small datasets
   - Validate output

**Example:**
```python
# Good: Balanced, uses combiner
def map(record):
    key = balanced_key(record)  # Balanced keys
    yield (key, value)

def combiner(key, values):  # Reduce shuffle
    return (key, aggregate(values))

# Bad: Skewed keys, no combiner
def map(record):
    key = skewed_key(record)  # Skewed keys
    yield (key, value)
    # No combiner
```

---

## 🎯 Advanced Topics

<div align="center">

### MapReduce Patterns

**Common Patterns:**
- Summarization
- Filtering
- Joining
- Sorting
- Iterative processing

**Optimization:**
- Combiners
- Custom partitioners
- Compression
- Data locality

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Two Phases** | Map and Reduce |
| **Distributed** | Processes across cluster |
| **Fault Tolerant** | Handles failures |
| **Shuffle** | Expensive operation |
| **Combiners** | Optimize shuffle |

**💡 Remember:** MapReduce is a simple model for distributed processing. Use combiners, minimize shuffle, balance keys, and filter early for optimal performance.

</div>

---

<div align="center">

**Master MapReduce for distributed processing! 🚀**

*From algorithm to optimization - comprehensive guide to MapReduce.*

</div>

