# CAP Theorem

## Summary

The CAP theorem, introduced by Eric Brewer in 2000, provides a fundamental framework for understanding the trade-offs that must be made when designing distributed systems. It states that **it is impossible for a distributed data store to simultaneously provide all three guarantees**: Consistency, Availability, and Partition Tolerance.

## The Three Pillars

### 1. Consistency (C)

**Definition:** Every read receives the most recent write or an error.

All working nodes in a distributed system return the same data at any given time. If you write data to node A, a read from node B immediately reflects that write.

**Example:** Financial systems where balance inquiries must reflect the most up-to-date account state.

```
┌─────────┐     Write: Balance = $1000
│ Node A  │─────────────────────────────┐
└─────────┘                             │
                                         ▼
┌─────────┐     Read: Balance = $1000  │
│ Node B  │◄────────────────────────────┘
└─────────┘     (Consistent - same value)
```

### 2. Availability (A)

**Definition:** Every request receives a non-error response, without guarantee that it contains the most recent write.

The system remains operational and responsive, even if responses don't reflect the most up-to-date data.

**Example:** Online retail systems that need to remain operational at all times.

```
┌─────────┐     Write: Item added
│ Node A  │─────────────────────────────┐
└─────────┘                             │
                                         ▼
┌─────────┐     Read: May return      │
│ Node B  │◄────────────────────────────┘
└─────────┘     stale data (Available)
```

### 3. Partition Tolerance (P)

**Definition:** The system continues to function despite network partitions where nodes cannot communicate.

A network partition occurs when a network failure causes a distributed system to split into groups of nodes that cannot communicate.

**Example:** Distributed systems across multiple data centers.

```
Normal State:
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Node A  │─────│ Node B  │─────│ Node C │
└─────────┘     └─────────┘     └─────────┘

Partition Occurs:
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Node A  │     │ Node B  │     │ Node C │
└─────────┘     └─────────┘     └─────────┘
   │              │              │
   └──────────────┴──────────────┘
   (Cannot communicate)
```

## The CAP Trade-Off: Choosing 2 out of 3

The theorem asserts that in the presence of a network partition, a distributed system must choose between Consistency and Availability.

```
        CAP Triangle
            /\
           /  \
          /    \
    Consistency  Availability
          \    /
           \  /
            \/
      Partition Tolerance
```

### CP (Consistency + Partition Tolerance)

**Prioritizes:** Consistency over Availability

**Behavior:** During a partition, the system may reject requests to maintain consistency.

**Examples:**
- Traditional relational databases (MySQL, PostgreSQL) with strong consistency
- Banking systems (ATM networks)
- Financial trading systems

**Diagram:**
```
Partition Occurs:
┌─────────┐     ┌─────────┐
│ Node A  │     │ Node B  │
│ (Write) │     │ (Read)  │
└─────────┘     └─────────┘
   │              │
   └──────────────┘ (Partition)

Node B: Returns ERROR (unavailable)
        to maintain consistency
```

### AP (Availability + Partition Tolerance)

**Prioritizes:** Availability over Consistency

**Behavior:** During a partition, different nodes may return different values (eventual consistency).

**Examples:**
- NoSQL databases (Cassandra, DynamoDB)
- Amazon shopping cart
- DNS systems
- CDN systems

**Diagram:**
```
Partition Occurs:
┌─────────┐     ┌─────────┐
│ Node A  │     │ Node B  │
│ Value=5 │     │ Value=3 │
└─────────┘     └─────────┘
   │              │
   └──────────────┘ (Partition)

Both nodes: Return responses (available)
            but may have different values
```

### CA (Consistency + Availability)

**Reality:** Impossible in distributed systems

**Why:** Network partitions are inevitable in distributed systems. This combination only works for single-node systems.

**Example:** Single-node databases (not distributed)

```
Single Node System:
┌──────────────┐
│   Database   │
│  (One Node)   │
└──────────────┘
   │
   └── Consistent AND Available
       (But not partition-tolerant)
```

## Practical Design Strategies

### 1. Eventual Consistency

Updates propagate to all nodes eventually, but not immediately.

**Use Cases:**
- DNS systems
- Content delivery networks (CDNs)
- Social media feeds
- Product recommendations

**Diagram:**
```
Write to Node A:
┌─────────┐
│ Node A  │ Value = 10
└────┬────┘
     │
     │ (Propagation delay)
     │
┌────▼────┐     ┌─────────┐
│ Node B  │     │ Node C  │
│ Value=5 │     │ Value=5 │
└─────────┘     └─────────┘

Eventually all nodes → Value = 10
```

### 2. Strong Consistency

Once a write is confirmed, any subsequent read returns that value.

**Use Cases:**
- Financial applications
- Inventory management
- Banking systems
- E-commerce order processing

**Diagram:**
```
Write: Balance = $1000
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Node A  │─────│ Node B  │─────│ Node C  │
│ $1000   │     │ $1000   │     │ $1000   │
└─────────┘     └─────────┘     └─────────┘
   │              │              │
   └──────────────┴──────────────┘
   All reads return $1000 immediately
```

### 3. Tunable Consistency

Systems adjust consistency levels based on specific needs.

**Example:** Cassandra allows configuring consistency per query.

**Use Cases:**
- E-commerce (strong consistency for orders, eventual for recommendations)
- Real-time analytics
- Multi-region applications

**Diagram:**
```
┌─────────────────┐
│  Application    │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ Strong │ │Eventual│
│Consist.│ │Consist.│
└────────┘ └────────┘
 Orders    Recommendations
```

### 4. Quorum-Based Approaches

Uses voting among nodes to ensure consistency and fault tolerance.

**Examples:**
- Consensus algorithms (Paxos, Raft)
- Distributed databases
- Distributed locks

**Diagram:**
```
3-node system, Quorum = 2

Write Request:
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Node A  │─────│ Node B  │─────│ Node C  │
│  ✓      │     │  ✓      │     │   ✗     │
└─────────┘     └─────────┘     └─────────┘

2 out of 3 nodes agree → Write succeeds
```

## Beyond CAP: PACELC

**PACELC** extends CAP by introducing **Latency** and **Consistency** trade-offs:

- **If Partition (P):** Trade-off between Availability and Consistency (A and C)
- **Else (E):** Trade-off between **Latency (L)** and **Consistency (C)**

**Diagram:**
```
PACELC Framework:

Partition? ──Yes──► Choose: A or C
    │
   No
    │
    ▼
Choose: L or C

Example:
- Strong consistency → Higher latency
- Eventual consistency → Lower latency
```

## Real-World Examples

### Banking System (CP)
- **Consistency:** Critical (balance accuracy)
- **Availability:** Can tolerate downtime during partitions
- **Example:** ATM networks reject transactions during network issues

### Amazon Shopping Cart (AP)
- **Availability:** Critical (always accept items)
- **Consistency:** Can tolerate eventual consistency
- **Example:** Cart works even during high traffic (Black Friday)

### Single Database (CA)
- **Consistency:** Yes
- **Availability:** Yes
- **Partition Tolerance:** No (single node)
- **Example:** Local MySQL database

## Why It Matters

**System Design Decisions:** CAP theorem guides architectural choices in distributed systems.

**Trade-off Clarity:** Makes trade-offs explicit and justifiable.

**Technology Selection:** Helps choose appropriate databases and architectures.

**Interview Preparation:** Fundamental concept for system design interviews.

## Design Considerations

### When to Choose CP
- Financial transactions
- Critical data accuracy
- Can tolerate downtime
- Strong consistency required

### When to Choose AP
- High availability critical
- Can tolerate stale data
- Large-scale systems
- Real-time user experience important

### Hybrid Approaches
- Different consistency levels for different operations
- Tunable consistency
- Quorum-based systems
- Eventual consistency with conflict resolution

## Interview Hints

When discussing CAP theorem:
1. Explain all three properties clearly
2. Explain why you can only choose 2 out of 3
3. Give real-world examples for CP and AP
4. Explain why CA is impractical
5. Discuss PACELC extension
6. Explain how your system design addresses CAP trade-offs

## Conclusion

The CAP theorem is a powerful tool for understanding inherent trade-offs in distributed system design. It's not about choosing the "best" property, but making informed decisions based on application requirements. By carefully evaluating CAP trade-offs, you can architect robust systems that deliver the right balance of consistency, availability, and partition tolerance.

