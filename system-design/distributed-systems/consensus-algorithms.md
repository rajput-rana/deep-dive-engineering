# Consensus Algorithms

// (// 

## Summary

Consensus algorithms enable distributed systems to agree on a single value or state despite node failures and network partitions. They're fundamental to distributed databases, blockchains, and distributed systems requiring consistency.

## Key Concepts

### Consensus Requirements

1. **Agreement:** All nodes agree on the same value
2. **Validity:** Value must be proposed by some node
3. **Termination:** Algorithm eventually terminates
4. **Fault Tolerance:** Works despite node failures

### Major Algorithms

1. **Raft**
   - Leader-based consensus
   - Easier to understand than Paxos
   - Used in etcd, Consul
   - Handles network partitions

2. **Paxos**
   - Classic consensus algorithm
   - Complex to implement
   - Used in Google Chubby
   - Handles Byzantine failures (with variants)

3. **PBFT (Practical Byzantine Fault Tolerance)**
   - Handles Byzantine failures
   - Used in permissioned blockchains
   - Requires 3f+1 nodes for f failures

4. **Proof of Work (PoW)**
   - Used in Bitcoin
   - Energy-intensive
   - Probabilistic consensus

5. **Proof of Stake (PoS)**
   - Used in Ethereum 2.0
   - Energy-efficient
   - Deterministic consensus

## Why It Matters

**Distributed Databases:** Need consensus for replication and consistency.

**Blockchains:** Entire system depends on consensus for validity.

**Service Coordination:** Distributed locks, leader election require consensus.

**Data Consistency:** Ensures all nodes see same data despite failures.

## Real-World Examples

**etcd:** Uses Raft for distributed key-value store (Kubernetes backend).

**Consul:** Raft for service discovery and configuration.

**Bitcoin:** Proof of Work for blockchain consensus.

**Ethereum:** Moving from PoW to Proof of Stake.

**MongoDB:** Raft variant for replica set consensus.

## Tradeoffs

### Raft vs Paxos

| Aspect | Raft | Paxos |
|--------|------|-------|
| Complexity | Simpler | More complex |
| Understandability | Easier | Harder |
| Performance | Similar | Similar |
| Adoption | Growing | Established |

### Consensus Properties

**CAP Theorem Tradeoff:**
- Consensus requires **Consistency** and **Partition tolerance**
- Must sacrifice **Availability** during partitions

**Performance:**
- Consensus adds latency (network round trips)
- Throughput limited by slowest node

## Design Considerations

### When Consensus is Needed

**Required for:**
- Distributed databases (replication)
- Distributed locks
- Leader election
- Configuration management
- Blockchain systems

**Not needed for:**
- Eventually consistent systems
- Read-only systems
- Single-node systems

### Fault Tolerance

**Raft:** Can tolerate (n-1)/2 failures
- 3 nodes: 1 failure
- 5 nodes: 2 failures
- 7 nodes: 3 failures

**Byzantine Fault Tolerance:** Can tolerate (n-1)/3 malicious nodes
- Requires 3f+1 nodes for f failures

## Common Challenges

1. **Split-Brain:** Network partition causes two leaders
   - Solution: Quorum requirements

2. **Slow Nodes:** One slow node slows entire system
   - Solution: Timeouts, remove slow nodes

3. **Network Partitions:** System unavailable during partition
   - Solution: Accept unavailability (CAP theorem)

## Interview Hints

When discussing consensus:
1. Explain why consensus is needed
2. Choose algorithm (Raft for simplicity, Paxos for complexity)
3. Discuss fault tolerance requirements
4. Address CAP theorem tradeoffs
5. Explain performance implications
// (// 

