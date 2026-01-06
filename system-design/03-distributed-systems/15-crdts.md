# CRDTs (Conflict-free Replicated Data Types)

**What it is:** Data structures that automatically resolve conflicts in distributed systems without coordination.

**One-line:** CRDTs allow distributed systems to scale, stay available, and converge automatically—by making conflicts mathematically impossible.

## Why CRDTs Are Needed

### The Core Distributed Systems Problem

In distributed systems you often want:
- ✅ High availability
- ✅ Low latency
- ✅ Offline / partition tolerance
- ✅ No global locks or coordination

**But:**
- Nodes update independently
- Network partitions happen
- Updates arrive out of order

### Traditional Approaches & Problems

| Approach | Problem |
|----------|---------|
| **Distributed locks** | Slow, fragile |
| **Strong consistency (2PC, Paxos)** | High latency |
| **Last-write-wins (LWW)** | Loses data |
| **Manual conflict resolution** | Complex, error-prone |

👉 **CRDTs solve this by design.**

## What CRDTs Guarantee

A CRDT (Conflict-free Replicated Data Type) ensures:

**All replicas converge to the same state without coordination, regardless of message order, duplication, or delay.**

### Formally: Strong Eventual Consistency (SEC)

- ✅ **Eventual delivery** - All updates eventually arrive
- ✅ **Convergence** - All replicas reach same state
- ✅ **No conflicts** - Automatic resolution

## How CRDTs Work (Core Idea)

CRDTs rely on mathematical properties:

**State must form a join-semilattice**

### Meaning: There is a merge function

**Merge is:**

- **Commutative** → order doesn't matter
  ```
  merge(a, b) = merge(b, a)
  ```

- **Associative** → grouping doesn't matter
  ```
  merge(a, merge(b, c)) = merge(merge(a, b), c)
  ```

- **Idempotent** → duplicates don't matter
  ```
  merge(a, a) = a
  ```

### So Replicas Can:

1. Update locally
2. Exchange states or operations
3. Merge freely
4. Always converge

## Two Synchronization Models

### 1. State-based CRDTs (CvRDTs)

**How it works:** Nodes periodically exchange full state

**Merge:** States using join operation

**Pros:**
- ✅ Simple
- ✅ Works with unreliable delivery

**Cons:**
- ❌ Higher bandwidth
- ❌ Larger messages

### 2. Operation-based CRDTs (CmRDTs)

**How it works:** Nodes send operations

**Requirement:** Operations must be delivered at least once

**Pros:**
- ✅ Efficient
- ✅ Smaller messages

**Cons:**
- ❌ Needs reliable delivery
- ❌ More complex

## Types of CRDTs

### A. Counter CRDTs

#### G-Counter (Grow-only)

**What it is:** Only increments, never decrements

**State:** Vector per replica

**Value:** Sum of all entries

**Use Cases:** Metrics, likes, view counts

**Example:**
```
Replica A: [5, 0, 0]
Replica B: [0, 3, 0]
Replica C: [0, 0, 2]
Value = 5 + 3 + 2 = 10
```

#### PN-Counter (Increment + Decrement)

**What it is:** Two G-Counters: increments and decrements

**Value:** `sum(increments) - sum(decrements)`

**Use Cases:** Vote counts, inventory (can go negative)

### B. Set CRDTs

#### G-Set (Grow-only Set)

**What it is:** Only add, no delete (ever)

**Use Cases:** Event logs, append-only sets

#### 2P-Set (Two-phase Set)

**What it is:** Add-set + Remove-set

**Limitation:** Once removed, can never re-add

**Use Cases:** Deleted items that shouldn't return

#### OR-Set (Observed-Remove Set) ⭐

**What it is:** Each add gets a unique ID, remove only removes observed IDs

**How it works:**
- Add element → assign unique tag
- Remove element → mark all its tags as removed
- Element exists if it has unremoved tags

**Use Cases:** Most common set CRDT, used heavily in real systems

### C. Register CRDTs

#### LWW-Register (Last-Write-Wins)

**What it is:** Keeps value with highest timestamp

**Uses:** Physical or hybrid clocks

**Limitation:** ⚠️ Can lose concurrent writes

**Use Cases:** Configuration values, user preferences

#### MV-Register (Multi-Value Register)

**What it is:** Keeps all concurrent values

**Resolution:** Application resolves conflict

**Use Cases:** When you need to see all concurrent writes

### D. Sequence CRDTs (Hardest)

**Used in:**
- Google Docs
- Figma
- Notion

**Examples:**
- RGA (Replicated Growable Array)
- Logoot
- YATA

**Enable:** Collaborative editing with real-time sync

## Real-World Applications

### Databases

| System | Usage |
|--------|-------|
| **DynamoDB** | Version vectors + CRDT concepts |
| **Riak** | Native CRDT support |
| **Cassandra** | Counters, LWW |
| **Redis** | CRDT modules |
| **CouchDB** | MVCC + CRDT ideas |

### Collaboration Tools

- **Google Docs** - Sequence CRDTs for text editing
- **Figma** - CRDTs for collaborative design
- **Notion** - CRDTs for document collaboration
- **Dropbox Paper** - CRDT-based editing

### Messaging / Sync

- Offline-first mobile apps
- IoT state sync
- Edge computing
- Distributed rate limiting
- Feature flags
- Counters & metrics
- User presence

## Code Implementation

### Example 1: G-Counter (Python)

```python
class GCounter:
    def __init__(self, node_id):
        self.node_id = node_id
        self.counts = {}

    def increment(self, value=1):
        self.counts[self.node_id] = self.counts.get(self.node_id, 0) + value

    def merge(self, other):
        for node, count in other.counts.items():
            self.counts[node] = max(self.counts.get(node, 0), count)

    def value(self):
        return sum(self.counts.values())
```

**Properties:**
- ✅ No locks
- ✅ No conflicts
- ✅ Order independent

### Example 2: PN-Counter

```python
class PNCounter:
    def __init__(self, node_id):
        self.p = GCounter(node_id)  # Positive
        self.n = GCounter(node_id)  # Negative

    def increment(self, v=1):
        self.p.increment(v)

    def decrement(self, v=1):
        self.n.increment(v)

    def merge(self, other):
        self.p.merge(other.p)
        self.n.merge(other.n)

    def value(self):
        return self.p.value() - self.n.value()
```

### Example 3: OR-Set (Simplified)

```python
import uuid

class ORSet:
    def __init__(self):
        self.adds = {}      # elem -> set of ids
        self.removes = set()

    def add(self, elem):
        tag = uuid.uuid4()
        self.adds.setdefault(elem, set()).add(tag)

    def remove(self, elem):
        if elem in self.adds:
            self.removes |= self.adds[elem]

    def merge(self, other):
        for elem, tags in other.adds.items():
            self.adds.setdefault(elem, set()).update(tags)
        self.removes |= other.removes

    def value(self):
        return {
            elem for elem, tags in self.adds.items()
            if len(tags - self.removes) > 0
        }
```

### Example 4: LWW-Register

```python
class LWWRegister:
    def __init__(self):
        self.value = None
        self.timestamp = 0

    def write(self, value, ts):
        if ts > self.timestamp:
            self.value = value
            self.timestamp = ts

    def merge(self, other):
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp
```

## When NOT to Use CRDTs

❌ **If you need:**

- **Strict invariants** - Bank balances, exact counts
- **Global uniqueness** - Unique IDs, primary keys
- **Strong ordering** - Transaction logs, event ordering

❌ **Large dynamic replica sets** - Vector explosion problem

**Use instead:**
- Transactions
- Consensus (Raft / Paxos)
- Hybrid approaches

## CRDT vs Alternatives

| Feature | CRDT | Transactions | Consensus |
|---------|------|--------------|-----------|
| **Availability** | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| **Latency** | Low | High | Medium |
| **Conflict-free** | ✅ | ❌ | ❌ |
| **Offline** | ✅ | ❌ | ❌ |
| **Strong Consistency** | ❌ | ✅ | ✅ |

## Best Practices

- ✅ Use CRDTs for eventually consistent data
- ✅ Choose appropriate CRDT type for use case
- ✅ Use OR-Set for general sets
- ✅ Use LWW-Register when losing concurrent writes is acceptable
- ✅ Use sequence CRDTs for collaborative editing
- ✅ Monitor convergence time
- ❌ Don't use CRDTs for strict invariants
- ❌ Don't use CRDTs for small, strongly consistent data

## Common Interview Questions

**Q: How do CRDTs ensure convergence?**
- Mathematical properties (commutative, associative, idempotent)
- Merge function always produces same result regardless of order

**Q: What's the difference between state-based and operation-based CRDTs?**
- State-based: Exchange full state, simpler but larger messages
- Operation-based: Exchange operations, efficient but needs reliable delivery

**Q: When would you use CRDTs vs consensus?**
- CRDTs: High availability, eventual consistency acceptable
- Consensus: Strong consistency required, can tolerate lower availability

**Q: How do CRDTs handle network partitions?**
- Continue operating locally
- Merge automatically when partition heals
- No coordination needed

## Related Topics

- **[Eventual Consistency](./01-eventual-consistency.md)** - Consistency model
- **[CAP Theorem](../01-fundamentals/08-distributed-systems/01-cap-theorem.md)** - Tradeoffs in distributed systems
- **[Consensus Algorithms](./06-consensus-algorithms.md)** - Strong consistency alternative
- **[Vector Clocks](./07-vector-clocks.md)** - Causality tracking

