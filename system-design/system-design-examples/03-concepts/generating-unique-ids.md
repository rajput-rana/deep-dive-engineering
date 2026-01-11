# Generating Unique IDs

You're designing a URL shortener. Each shortened URL needs a unique identifier. Simple enough, you think. Just use an auto-incrementing database ID.
Then you scale to multiple database servers. Now you have a problem. Two servers might generate the same ID at the exact same moment. Your "unique" IDs are no longer unique.
This is one of those problems that seems trivial until you actually have to solve it at scale.
In this chapter, we'll explore the most common approaches to generating unique IDs, understand their trade-offs, and learn when to use each one. 
This topic comes up frequently in system design interviews because it touches on coordination, scalability, and the kinds of practical engineering decisions you'll face in real distributed systems.
# Why Is This Problem Hard?
On a single server, generating unique IDs is almost embarrassingly simple. You maintain a counter, increment it for each new ID, and the database handles everything atomically with `AUTO_INCREMENT` or `SERIAL`. Each ID is guaranteed to be unique and sequential.
The moment you add a second server, this approach falls apart. Without some form of coordination, both servers might increment their counters to the same value at the same time.

### The Coordination Dilemma
The obvious solution is to add coordination. Before generating an ID, have each server check with a central authority. But coordination comes with significant costs:
**Latency:** Every ID generation now requires a network round-trip. If you're generating millions of IDs per second, those round-trips add up quickly.
**Single point of failure:** If the central authority goes down, no server can generate new IDs. Your entire system grinds to a halt.
**Throughput bottleneck:** The central authority becomes a chokepoint that limits how fast your entire system can operate.
The best ID generation schemes avoid coordination entirely. Each server generates IDs independently, yet collisions never happen. This sounds like magic, but as we'll see, there are clever ways to achieve it.

### Different Systems Have Different Needs
Before diving into solutions, it's worth understanding that different use cases have different requirements. Not every system needs the same properties from its IDs.
| Requirement | Description | Example Use Case |
| --- | --- | --- |
| Uniqueness | No duplicates across all servers, all time | Every system needs this |
| Sortable | IDs can be ordered by creation time | Time-series data, activity feeds |
| Compact | Small storage footprint | URL shorteners, bandwidth-constrained mobile apps |
| Unpredictable | Cannot guess next or previous IDs | User-facing IDs, security-sensitive contexts |
| High throughput | Generate millions per second | Social media, high-scale services |
| No coordination | Generate independently | Microservices, distributed databases |

No single approach satisfies all these requirements perfectly. The art is understanding which trade-offs matter most for your specific system.
# Approach 1: Database Auto-Increment
Let's start with the simplest approach. Let the database handle ID generation.
The database maintains a counter internally. Each insert increments it atomically, and the counter persists across restarts. For a single database server, this works perfectly.

### Scaling with Multiple Databases
When you need multiple database servers, you can make auto-increment work by giving each server a different range or stepping pattern:
**Step-based approach:**
Server 1 generates odd numbers (start=1, step=2), Server 2 generates even numbers (start=2, step=2). They never overlap.
**Range-based approach:**
Each server gets a dedicated range and operates independently within it.

### Trade-offs
| Pros | Cons |
| --- | --- |
| Simple to implement and understand | Requires database round-trip for every ID |
| Sequential and naturally sortable | Database becomes a single point of failure |
| Compact (64-bit integer) | Hard to scale horizontally |
| Human-readable | Predictable (security concern for public IDs) |

### When This Approach Makes Sense
Auto-increment works well for small to medium-scale systems where you already have a single primary database and don't need horizontal scaling. It's also fine for internal systems where ID predictability isn't a concern.
However, if you're building microservices with independent databases, or if you need to generate IDs at massive scale without database dependencies, you'll need something else.
# Approach 2: UUID (Universally Unique Identifier)
UUIDs are 128-bit identifiers designed to be unique without any coordination between servers. They look like this:
The beauty of UUIDs is that any server can generate them independently, and the probability of collision is so astronomically low that it's effectively zero for practical purposes.

### UUID Versions Explained
There are several UUID versions, each using different strategies to achieve uniqueness:
**UUID v1** combines the current timestamp with the machine's MAC address. This makes IDs sortable by time (with some parsing), but it exposes your hardware address, which can be a privacy concern.
**UUID v4** is the most commonly used version. It generates 122 bits of pure randomness. Simple, universally supported, but completely unsortable.
**UUID v7** is newer and combines a Unix timestamp in milliseconds with random bits. You get the sortability benefits of v1 without exposing hardware information. This is the recommended choice for new systems that need time-ordering.

### Collision Probability
With 122 random bits in UUID v4, the probability of collision is vanishingly small:
For any practical application, UUID v4 collisions will never happen. You're more likely to experience a hardware failure than a UUID collision.

### The Database Performance Problem
UUIDs have a significant drawback that isn't immediately obvious: they cause terrible database index performance.
When you use sequential IDs as primary keys, new inserts always go to the end of the B-tree index. The database can efficiently append data without reorganizing existing pages.
Random UUIDs, on the other hand, cause inserts to land all over the index:
This random access pattern causes page splits, fragmentation, and increased I/O. In high-write workloads, UUID v4 primary keys can be 10-100x slower than sequential IDs.

### Trade-offs
| Pros | Cons |
| --- | --- |
| No coordination needed | Large size (128 bits = 16 bytes) |
| Extremely low collision risk | Not sortable (v4) |
| Universally supported | Poor database index performance |
| Can be generated anywhere | Not human-readable |

### When This Approach Makes Sense
UUIDs work well for distributed systems where IDs need to be generated without any coordination, especially when ID generation happens on the client side. They're also useful when merging data from multiple sources that were created independently.
Avoid UUIDs for high-write databases where index performance matters, or for URL shorteners where the 36-character string representation is too long.
# Approach 3: Snowflake IDs
Twitter faced all of these challenges in the early 2010s. They needed IDs that were:
- Unique across thousands of servers
- Sortable by time for displaying tweets in chronological order
- 64 bits to fit in existing systems and databases
- Generated without central coordination

Their solution, Snowflake, has become one of the most influential ID generation schemes in the industry. Discord, Instagram, and many other high-scale services use variations of it.

### Understanding the Structure
A Snowflake ID packs a lot of information into 64 bits:
**Sign bit (1 bit):** Always zero. This ensures the ID is always a positive number.
**Timestamp (41 bits):** Milliseconds since a custom epoch. Twitter uses November 4, 2010, as their epoch. 41 bits gives you about 69 years of IDs before the space runs out.
**Machine ID (10 bits):** Identifies which server generated the ID. This allows up to 1,024 unique machines to generate IDs simultaneously.
**Sequence (12 bits):** A counter for IDs generated within the same millisecond on the same machine. This supports 4,096 IDs per millisecond per machine.

### How It Works in Practice
The algorithm is elegant in its simplicity:
Each machine operates independently. As long as machine IDs don't overlap, IDs will never collide. The timestamp component ensures IDs are roughly sortable by creation time.

### Throughput Capacity
The numbers are impressive:
A single machine can generate over 4 million IDs per second. A cluster of 1,024 machines can generate 4 billion IDs per second. That's enough for virtually any application.

### Extracting Information from IDs
One useful property of Snowflake IDs is that you can extract the timestamp:
This is useful for debugging, auditing, and estimating when entities were created without querying additional metadata.

### The Clock Problem
Snowflake has one vulnerability: it depends on accurate system clocks. Two scenarios cause problems:
**Clock moving backward:** If a server's clock is adjusted backward (common with NTP corrections), the generator might produce timestamps it has already used. Most implementations handle this by refusing to generate IDs until the clock catches up.
**Clock skew between servers:** Different servers may have slightly different times. This means IDs from different servers aren't perfectly ordered by creation time. In practice, this is usually acceptable. NTP keeps servers synchronized to within a few milliseconds.

### Trade-offs
| Pros | Cons |
| --- | --- |
| Compact (64-bit) | Requires machine ID coordination |
| Time-sortable | Depends on clock synchronization |
| High throughput | 69-year limit from epoch |
| No central coordination for ID generation | More complex than simpler approaches |

### When This Approach Makes Sense
Snowflake is the right choice for high-scale services that need time-sortable, 64-bit IDs. It's battle-tested at companies like Twitter, Discord, and Instagram.
It's overkill for simple applications, and it can be awkward in serverless or ephemeral environments where assigning stable machine IDs is difficult.
# Approach 4: ULID (Universally Unique Lexicographically Sortable Identifier)
ULID was created to combine the best properties of UUID (no coordination needed) with the sortability of Snowflake.

### Structure
**Timestamp (48 bits):** Milliseconds since Unix epoch. This gives about 8,000 years of IDs, far longer than Snowflake's 69 years.
**Randomness (80 bits):** Cryptographically random bits that ensure uniqueness within the same millisecond.
**Encoding:** Uses Crockford's Base32, which is case-insensitive and avoids ambiguous characters like 'I', 'L', 'O', '0'.

### Key Properties
The timestamp-first structure means that string sorting produces time ordering:
You can sort ULIDs as strings and get chronological order. No parsing or special comparison functions needed.

### ULID vs UUID Comparison
| Property | UUID v4 | ULID |
| --- | --- | --- |
| Size | 128 bits | 128 bits |
| Sortable | No | Yes |
| Timestamp extractable | No | Yes |
| String length | 36 characters | 26 characters |
| Case-sensitive | No | No |
| Coordination required | No | No |

ULID gives you everything UUID v4 provides, plus sortability and a shorter string representation. For most new systems, ULID is a better default choice than UUID v4.

### When This Approach Makes Sense
ULID is excellent when you need UUID-like properties with time-ordering. It works well in distributed systems without machine ID coordination, and the lexicographic sorting property makes it convenient for many use cases.
# Approach 5: MongoDB ObjectID
MongoDB's default ID format deserves mention because it's so widely used and represents an interesting design point between UUID and Snowflake.

### Structure
**Timestamp (4 bytes):** Unix timestamp in seconds. Provides rough time-ordering at second granularity.
**Random value (5 bytes):** Generated once per process. Unique per machine/process combination.
**Counter (3 bytes):** Incrementing counter, initialized to a random value. Supports 16 million IDs per second per process.

### Key Properties
ObjectID is smaller than UUID (12 bytes vs 16), roughly time-sortable, and requires no coordination. The counter component handles bursts of IDs within the same second.
This format is optimized for MongoDB's document-oriented storage model. If you're using MongoDB, there's rarely a reason to use anything else for document IDs.
# Approach 6: Ticket Servers
Sometimes you really do need sequential IDs, and the coordination costs are acceptable. Ticket servers provide a pragmatic middle ground.

### How It Works
Instead of coordinating for every ID, application servers request blocks of IDs in bulk:
Each application server requests a block of IDs (say, 1,000 at a time) and uses them locally without further coordination. When the block runs out, it requests a new one.
Flickr famously used this approach with MySQL:
For high availability, you can run two ticket servers with different offsets:

### Trade-offs
| Pros | Cons |
| --- | --- |
| Simple to understand | Central point of coordination |
| Sequential IDs | Network latency for new blocks |
| Works with any database | Block allocation adds complexity |
| Predictable capacity | Wasted IDs if server crashes mid-block |

This approach makes sense when sequential IDs are genuinely required and you have existing database infrastructure to leverage.
# Other Notable Schemes

### KSUID (K-Sortable Unique Identifier)
Segment's format: 27 characters, 160 bits total.
KSUID uses a custom epoch (May 13, 2014) and has a larger random component than Snowflake. Base62 encoded, making it URL-safe.

### Sonyflake
Sony's variation of Snowflake optimized for longer lifespan:
Sonyflake trades throughput for longevity: 174 years of IDs (vs 69), but only 256 IDs per 10ms (vs 4,096 per ms). It also supports 65,536 machines instead of 1,024.

### NanoID
Short, URL-friendly IDs with customizable alphabet:
NanoID is cryptographically secure, configurable in length and character set, and smaller than UUID for equivalent collision resistance.
# Choosing the Right Approach

### Decision Framework

### Decision Factors
**Scale:** For low scale (under 1K IDs/sec), auto-increment is perfectly fine. For medium scale (1K-100K IDs/sec), UUID, ULID, or ticket servers work well. For high scale (over 100K IDs/sec), consider Snowflake or similar schemes.
**Sortability:** If you need time-ordered IDs for feeds, time-series data, or debugging, use Snowflake, ULID, or UUID v7. If order doesn't matter, UUID v4 is simpler.
**ID Size:** If you need 64-bit IDs (for database compatibility, bandwidth, or existing systems), Snowflake or auto-increment are your options. If 128 bits is acceptable, UUID or ULID give you more flexibility.
**Infrastructure:** With a centralized database, auto-increment or ticket servers are easy. In distributed or serverless environments, UUID or ULID avoid coordination headaches. If you can assign machine IDs reliably, Snowflake is powerful.
**Security:** If IDs are user-facing and predictability is a concern, use UUID v4 or other random-heavy schemes. Sequential IDs expose information about your system's activity.

### Common Patterns in Practice
**URL Shortener:** Snowflake or counter-based with Base62 encoding. Sequential nature helps with caching.
**Social Media Posts:** Snowflake (Twitter, Discord). Time-sortability is essential for feeds.
**User Accounts:** UUID v4 (unpredictable) or Snowflake with privacy considerations.
**Database Primary Keys:** ULID or UUID v7 for good index performance with sortability. Avoid UUID v4.
**API Idempotency Keys:** UUID v4, typically client-generated.
**Distributed Logs/Events:** ULID or Snowflake for time-sorted analysis.
# Comparison Summary
| Approach | Size | Sortable | Coordination | Throughput | Best For |
| --- | --- | --- | --- | --- | --- |
| Auto-Increment | 64 bits | Yes | Required | Medium | Single DB systems |
| UUID v4 | 128 bits | No | None | High | Distributed, no ordering |
| UUID v7 | 128 bits | Yes | None | High | Modern UUID replacement |
| Snowflake | 64 bits | Yes | Machine ID | Very High | High-scale services |
| ULID | 128 bits | Yes | None | High | General purpose |
| ObjectID | 96 bits | Roughly | None | High | MongoDB |
| Ticket Server | 64 bits | Yes | Block allocation | Medium | Sequential requirement |

# Implementation Considerations

### Clock Synchronization
Time-based schemes depend on accurate clocks. Ensure NTP is configured and running on all servers. Handle clock drift gracefully, and decide what happens if the clock jumps backward (most implementations refuse to generate IDs until the clock catches up).

### Machine ID Assignment
Snowflake and similar schemes need unique machine IDs. Options include:
- Configuration management (assign during deployment)
- Coordination services like ZooKeeper or etcd for dynamic assignment
- Last N bits of IP address or MAC address
- Cloud provider instance metadata

### Collision Handling
Even with extremely low collision probability, add defensive measures:
- Unique constraints in the database
- Graceful handling of duplicate key errors
- Logging and alerting on collisions (indicates a bug in your generation logic)

### Migration
Changing ID schemes after launch is painful. Choose carefully upfront. If you must migrate:
- Maintain a mapping table between old and new IDs
- Some schemes allow coexistence with different prefixes
- Plan for a long transition period

# Summary
| Need | Recommendation |
| --- | --- |
| Simple, small scale | Auto-increment |
| Distributed, no ordering | UUID v4 |
| Distributed, time-sorted | ULID or UUID v7 |
| High scale, 64-bit | Snowflake |
| MongoDB | ObjectID (default) |
| URL-friendly short IDs | NanoID or custom |

For most modern distributed systems, **ULID** or **UUID v7** provide a good balance of uniqueness, sortability, and simplicity without requiring coordination.
For very high-scale systems where 64-bit IDs are necessary (database performance, network bandwidth), **Snowflake** or its variants remain the gold standard, proven at Twitter, Discord, Instagram, and many others.
Whatever you choose, make the decision early. Changing ID schemes in a running production system is one of the most painful migrations you can undertake.
# References
- [Twitter Snowflake (GitHub)](https://github.com/twitter-archive/snowflake) - Original Snowflake implementation and design rationale
- [ULID Specification](https://github.com/ulid/spec) - Official ULID specification and implementations
- [UUID RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122) - The original UUID standard specification
- [UUID v7 Draft RFC](https://datatracker.ietf.org/doc/html/draft-peabody-dispatch-new-uuid-format) - New sortable UUID format proposal
- [Flickr Ticket Servers](https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/) - Flickr's practical approach to distributed IDs
- [Instagram Engineering: Sharding IDs](https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c) - How Instagram adapted Snowflake for their needs

# Quiz

## Generating Unique IDs Quiz
Why does simple database auto-increment become risky when you scale writes across multiple independent database servers?