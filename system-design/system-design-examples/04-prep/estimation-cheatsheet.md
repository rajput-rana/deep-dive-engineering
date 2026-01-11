# Estimation Cheat Sheet (numbers you must know)

In a system design interview, you might be asked, "How would you design a system to store a billion photos?" or "How many servers do you need to handle Twitter's timeline service?"
The secret isn't about giving a perfectly precise answer. It's about demonstrating your **intuition for scale**.
Estimation is the process of making reasonable, informed guesses to guide your architectural choices. It shows that you understand the trade-offs between different components and can design a system that is both feasible and cost-effective. The goal is not perfect math but a sound thought process.
This cheat sheet provides the real-world reference numbers and quick calculation tricks to anchor your thinking and help you design with confidence.
# 1. Quick Reference Summary
Let's start with the basics. For simplicity in interviews, always use powers of 10.
| Category | Value | Notes |
| --- | --- | --- |
| 1 KB | 1,000 bytes | Don't use 1,024; it complicates the math. |
| 1 MB | 1,000 KB = 106 bytes | Pronounced "1e6" |
| 1 GB | 1,000 MB = 109 bytes | Pronounced "1e9" |
| 1 TB | 1,000 GB = 10¹² bytes | Pronounced "1e12" |
| 1 million users | 10⁶ users | Common scale target |
| 1 billion users | 10⁹ users | Global-scale system |

# 2. Latency Numbers (Know These by Heart)
Latency determines your system's responsiveness and influences key design decisions like caching, data partitioning, and asynchronous processing. These numbers are the foundation.
| Operation | Typical Latency | Real-World Analogy |
| --- | --- | --- |
| L1 cache access | ~0.5 ns | Picking up something from your pocket |
| L2 cache access | ~7 ns | Picking something up from your desk |
| RAM access | ~100 ns | Grabbing a book from a nearby shelf |
| SSD random read | ~100 µs | Walking to another room to get something |
| HDD random read | ~10 ms | Leaving your building to go to a nearby store |
| Network (Data Center) | ~500 µs | Walking to a building across the street |
| Internet (US to Europe) | ~100 ms | Making a cross-continent phone call |

Each layer is roughly **10× slower** than the previous one. A read from RAM is thousands of times faster than from an SSD. **Your primary goal in performance tuning is to minimize operations that cross these boundaries.**
# 3. Bandwidth and Throughput
Bandwidth defines **how much data you can move per second**. You’ll often convert it into **real-world throughput** (MB/s).
| Bandwidth | Transfer Rate (Approx.) | What it can handle |
| --- | --- | --- |
| 1 Mbps | 0.125 MB/s | Sending a low-quality photo per second |
| 100 Mbps | 12.5 MB/s | A typical home Wi-Fi connection |
| 1 Gbps | 125 MB/s | Standard data center network link |
| 10 Gbps | 1.25 GB/s | High-performance backend server link |

**Rule of Thumb:**
`Transfer Time (s) = Data Size (MB) / Bandwidth (MB/s)`
**Example: **Downloading a 1 GB file over 100 Mbps → 1,000 MB / 12.5 MB/s = **~80 seconds**
# 4. Storage Estimation (Mental Models)
Quickly estimating storage needs is a common interview task. Start by estimating the size of a single data object.

### Common Object Sizes
| Item | Approximate Size | Notes |
| --- | --- | --- |
| Text message / Tweet | ~1 KB | Includes metadata |
| Database row | ~1-2 KB | A typical user profile record |
| Photo (compressed) | 2-5 MB | From a smartphone |
| Audio song (MP3) | ~5 MB | A 3-4 minute song |
| Video (HD, 1 min) | ~100 MB | Example: Youtube clip |

#### Estimation Formula
`Total Storage = (Number of Users) × (Items per User) × (Size per Item)`
**Example**: Estimate storage for a simple photo-sharing app after one year.
- **Assumptions**: 100 million users, each uploads 10 photos, average photo size is 2 MB.
- **Calculation**: 100M users × 10 photos/user × 2 MB/photo = 2,000M MB = 2,000,000 GB = 2,000 TB = **2 PB** (Petabytes).

If required, also  account for:
- **Replication (×3)**
- **Backups (×7 for daily retention)**
- **Compression savings (~×0.5)**

# 5. Request Estimation (Traffic and QPS)
Queries Per Second (QPS) is a measure of the request load on your system.
**Rule of Thumb (The 80/20 Rule):** Assume most traffic occurs during an 8-hour peak window, not evenly over 24 hours. A simpler approach for interviews is to assume a **100k second day** for easier math (`24 * 3600 ≈ 86,400`).
**QPS Formula:**
`QPS = (Total Daily Requests) / (Seconds in a Day)`
**Example**: Estimate the average QPS for a service with 100M Daily Active Users (DAU), where each user makes 10 requests per day.
- **Total Requests**: 100M DAU × 10 requests/day = 1 Billion requests/day
- **Average QPS**: 1B requests / 100,000 seconds ≈ **10,000 QPS**

#### Common Traffic Patterns
| System | Approx. QPS | Notes |
| --- | --- | --- |
| Small startup API | 100 – 1,000 | Can be handled by a few servers |
| Medium web app | 10k – 100k | Requires load balancing and a fleet of servers |
| YouTube-scale | 1M+ | Massive global distribution required |

#### Estimating Concurrent Users
`Concurrent = (DAU × Avg Session Duration) / Seconds per Day`
E.g., 10M DAU × 300s session / 86,400 → **~35K concurrent users**
# 6. Data Volume Growth Rates
**Think in time buckets:** *daily → monthly → yearly*. Then add safety for reality: **+30% buffer** (replication, backups, indexes, headroom).

### Core Rule

### Quick Reference Table
| Daily Ingest | Monthly (×30) | Yearly (×360) | With 30% Buffer |
| --- | --- | --- | --- |
| 10 GB/day | 300 GB | 3.6 TB | 4.68 TB/year |
| 100 GB/day | 3 TB | 36 TB | 46.8 TB/year |
| 1 TB/day | 30 TB | 360 TB | 468 TB/year |
| 10 TB/day | 300 TB | 3.6 PB | 4.68 PB/year |

> Buffer includes: replication overhead, backup snapshots, index bloat, and “unknown unknowns.”

# 7. Cache and Database Capacity Estimation

### Cache Sizing Rule
`Cache Size ≈ (Hot Data %) × (Total Dataset)`
E.g., 10% of 2 TB dataset → **200 GB cache**

### Database Storage

#### What to remember
- **Replication Factor (RF):** often **×3** (3 AZs).
- **Index Overhead:** **20–100%** depending on schema (secondary indexes, FKs).
- **Write-ahead logs / binlogs / snapshots:** budget **10–30%**.
- **Backups:** e.g., **7 daily** + **4 weekly** (incremental vs full matters).
- **Compression:** row vs columnar; apply if your engine uses it.

#### Example:
“Raw data is **2 TB**. With **×3 replication**, yearly retention **×1** → **6 TB**.** **
Add **~30%** for indexes/binlogs/backups: **~7.8 TB**. Round to **8–10 TB** for headroom.”
# 8. Back-of-the-Envelope Examples

### Example 1: Design an Instagram-like System
**Assumptions**: 500M Daily Active Users (DAU). 10% of users upload 1 photo per day. Average photo size is 2 MB.
**Storage Estimation**:
**Design Implications**: This volume is too large for a traditional database. You need a distributed object store like Amazon S3.

### Example 2: Design a Log Storage System
**Assumptions**: 1 million servers, each generating 1 KB of logs per second.
**Ingestion Rate**:
- 1M servers × 1 KB/log/sec = 1M KB/sec = **1 GB/sec**
- Daily Volume = 1 GB/sec × 86,400 sec/day ≈ **86 TB/day**

**Optimization**: Logs are highly compressible (often 10:1 ratio).
- Compressed Daily Volume = 86 TB / 10 = **8.6 TB/day**

**Design Implications**: You need a high-throughput ingestion pipeline (like Kafka) to handle 1 GB/sec and a cheap storage layer (like S3) for the massive daily volume.
# Quiz

## Estimation Cheatsheet Quiz
For interview math, how should you treat 1 KB?