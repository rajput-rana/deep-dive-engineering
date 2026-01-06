# Database Replication

## Summary

Database replication creates copies of data across multiple database servers. It improves availability, enables read scaling, and provides disaster recovery. Replication is fundamental for building reliable distributed systems.

## Key Concepts

### Replication Types

1. **Master-Slave (Primary-Replica)**
   - One master handles writes
   - Multiple slaves handle reads
   - Asynchronous replication
   - Simple, common pattern

2. **Master-Master (Multi-Master)**
   - Multiple masters handle writes
   - Bidirectional replication
   - More complex, conflict resolution needed
   - Higher availability

3. **Synchronous vs Asynchronous**
   - **Synchronous:** Write waits for replication (strong consistency)
   - **Asynchronous:** Write doesn't wait (better performance, eventual consistency)

## Why It Matters

**High Availability:** If master fails, slave can take over.

**Read Scaling:** Distribute read traffic across replicas.

**Disaster Recovery:** Replicas in different regions provide backup.

**Performance:** Read-heavy workloads benefit from read replicas.

## Real-World Examples

**MySQL Replication:** Master-slave replication for read scaling.

**PostgreSQL:** Streaming replication for high availability.

**MongoDB:** Replica sets with automatic failover.

**AWS RDS:** Automated replication across availability zones.

## Tradeoffs

### Master-Slave vs Master-Master

**Master-Slave:**
- ✅ Simple, proven
- ✅ No write conflicts
- ❌ Single write point
- ❌ Failover complexity

**Master-Master:**
- ✅ Higher availability
- ✅ Write scaling
- ❌ Conflict resolution
- ❌ More complex

### Synchronous vs Asynchronous

**Synchronous:**
- ✅ Strong consistency
- ❌ Higher latency
- ❌ Lower throughput

**Asynchronous:**
- ✅ Better performance
- ✅ Lower latency
- ❌ Replication lag
- ❌ Eventual consistency

## Design Considerations

- Choose replication type based on needs
- Consider replication lag impact
- Plan for failover scenarios
- Monitor replication health
- Use read replicas for read-heavy workloads

## Interview Hints

When discussing replication:
1. Explain replication types
2. Discuss synchronous vs asynchronous
3. Address failover scenarios
4. Consider consistency tradeoffs
5. Explain use cases
