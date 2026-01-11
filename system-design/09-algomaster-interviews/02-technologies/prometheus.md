# Prometheus Deep Dive for System Design Interviews

Prometheus is the monitoring system you reach for when you want **clear visibility into a distributed system, **not just dashboards, but an explainable model for how metrics are collected, stored, queried, and alerted on. 
It’s become the default for cloud-native observability because it’s simple at the edges (apps expose `/metrics`) and powerful at the core (PromQL + alerting), without requiring agents everywhere or a heavyweight centralized pipeline.
It is a complete monitoring system with service discovery, a powerful query language, and sophisticated alerting. 
This chapter gives you that depth. We will cover the pull-based architecture, metric types and when to use each, PromQL queries for common patterns, storage internals, alerting strategies, and scaling approaches. 
By the end, you will be able to design monitoring into your systems and explain those decisions confidently.
# 1. When to Choose Prometheus
Prometheus is not the right choice for every monitoring need. Understanding when it shines and when it struggles helps you make better architectural decisions and justify those choices in interviews.

### 1.1 Choose Prometheus When You Have

#### Metrics-based monitoring needs
Prometheus is purpose-built for numeric time-series data, values that change over time. CPU usage, request latency, error rates, queue depths, memory consumption. If you can express it as a number that you sample periodically, Prometheus handles it well.

#### Dynamic environments
In Kubernetes or cloud environments, services come and go. Pods scale up and down. New instances appear and old ones terminate. Prometheus's service discovery automatically finds and monitors new targets without manual configuration. When a new pod starts with the right annotations, Prometheus starts scraping it. When the pod dies, it stops. This is essential for autoscaling environments.

#### Need for powerful querying
Prometheus's query language, PromQL, lets you ask sophisticated questions. "What is the 99th percentile latency for requests to /api/users across all pods in the last hour?" A single PromQL expression answers that. You can aggregate across dimensions, calculate rates, compare to historical data, and build complex alerts.

#### Alerting requirements
Prometheus integrates with Alertmanager for production-grade alerting. You can route different alerts to different teams, group related alerts to avoid notification storms, silence alerts during maintenance, and prevent cascading alerts with inhibition rules.

#### Reliability over completeness
Here is an important design philosophy. Prometheus prioritizes being available over being perfectly accurate. Each Prometheus server is independent with its own local storage. It does not depend on external databases or coordination services. When your network is partitioned, when other systems are failing, Prometheus keeps working. This is intentional. When things are breaking, you need your monitoring to work most of all.

#### Multi-dimensional data
Labels let you slice and dice metrics without predefining hierarchies. A single metric like `http_requests_total` can have labels for method, endpoint, status code, and instance. You can aggregate by any combination: all requests to /api/users, all 500 errors, all requests from a specific instance. This flexibility is powerful for debugging.

### 1.2 Avoid Prometheus When You Need
Understanding Prometheus's limitations is as important as knowing its strengths. Here is when to look elsewhere:

#### Long-term storage
Prometheus's local storage is designed for short to medium-term retention, typically days to weeks. Storing a year of metrics on a single Prometheus server is not practical. 
For long-term retention, use solutions like Thanos, Cortex, or VictoriaMetrics that store data in object storage like S3. Prometheus handles recent data; these systems handle historical queries.

#### Log aggregation
Metrics and logs are different. Prometheus handles numeric measurements sampled at intervals. It does not store log lines, stack traces, or unstructured text. 
For logs, use Loki (which integrates well with Prometheus), Elasticsearch, or cloud solutions like CloudWatch Logs. A common pattern is Prometheus for metrics, Loki for logs, and a tracing system for distributed traces.

#### Distributed tracing
When a request flows through multiple services, you need to trace its path to find where latency is introduced. Prometheus cannot do this. 
Use Jaeger, Zipkin, or Tempo for distributed tracing. These systems record individual request traces with timing for each hop. Prometheus tells you the 99th percentile latency is 2 seconds; tracing tells you which service is responsible.

#### Event-based data
Prometheus samples metrics at regular intervals (typically every 15 or 30 seconds). It is not designed for discrete events like user logins, purchases, or audit logs where you need to capture every occurrence. 
A 15-second scrape might miss a process that started and crashed in 5 seconds. For event data, use event streaming systems like Kafka or dedicated analytics databases.

#### 100% accuracy requirements
Related to the sampling issue, Prometheus does not guarantee capturing every data point. For billing systems where you need exact request counts or financial metrics where accuracy is legally required, use a different system that records every event directly, perhaps writing to a database from within your application.

#### High cardinality per metric
This is a common pitfall. Prometheus stores each unique combination of metric name and labels as a separate time series. If you add `user_id` as a label and you have a million users, you create a million time series just for that metric. 
Prometheus memory usage and query performance degrade badly with high cardinality. Never use user IDs, request IDs, or other high-cardinality values as labels.

### 1.3 Common Interview Systems Using Prometheus
| System | Why Prometheus Works |
| --- | --- |
| Rate Limiter | Track request counts, rejection rates, throttle thresholds |
| API Gateway | Latency percentiles, error rates, request volume per endpoint |
| Distributed Cache | Hit/miss ratios, eviction rates, memory usage |
| Message Queue | Queue depth, consumer lag, throughput metrics |
| Kubernetes Cluster | Pod resource usage, node health, deployment status |
| Microservices | Service-level SLIs (latency, error rate, throughput) |
| Database | Query performance, connection pool, replication lag |
| Load Balancer | Backend health, request distribution, connection counts |

# 2. Core Architecture
One of the most common interview questions about Prometheus is "why does it use a pull model instead of push?" Understanding the architecture helps you answer this and explains the trade-offs Prometheus makes.

### 2.1 Pull-Based Model
Prometheus takes an unusual approach compared to many monitoring systems. Instead of applications pushing metrics to a central collector, Prometheus actively pulls (scrapes) metrics from applications at regular intervals.
Every service you want to monitor exposes an HTTP endpoint, typically `/metrics`, that returns current metric values in a text format. Prometheus periodically sends HTTP GET requests to these endpoints and stores the results.

#### Why pull makes sense:
At first, pull seems counterintuitive. Why should the monitoring server have to know about every target? But the pull model has several advantages:
**Centralized control:** Prometheus decides what to scrape and how often. You can change scrape intervals, add new targets, or adjust timeouts in one place. With push, each application controls its own reporting, making coordinated changes difficult.
**Easier debugging:** If metrics look wrong, you can curl the `/metrics` endpoint directly and see exactly what the application is exposing. This makes debugging straightforward, no need to check if metrics are being received.
**Health indication built-in:** If Prometheus cannot scrape a target, that itself is information. A failed scrape means the target is down or unreachable. With push systems, silence is ambiguous: is the service healthy but has nothing to report, or is it dead?
**No client-side buffering needed:** Applications expose current state. They do not need to buffer metrics or retry failed sends. This simplifies client implementations and avoids memory issues if the monitoring server is temporarily unreachable.
**Backpressure is natural:** Prometheus controls the scrape rate. With push systems, a burst of events from applications can overwhelm the collector. In pull systems, the collector sets the pace.

#### Pull vs Push trade-offs:
That said, pull is not perfect. Here are the trade-offs:
| Aspect | Pull (Prometheus) | Push (StatsD, InfluxDB) |
| --- | --- | --- |
| Target discovery | Server-side service discovery | Client knows server address |
| Firewall friendly | Prometheus needs network access to targets | Targets push through firewall |
| Short-lived jobs | Needs Pushgateway workaround | Natural fit |
| Health detection | Missing scrape = target down | Requires separate health check |
| Backpressure | Server controls rate | Server can be overwhelmed |

The biggest limitation is short-lived jobs. A batch process that runs for 30 seconds and exits cannot be scraped because it is gone before the next scrape interval. Prometheus addresses this with the Pushgateway, which we will cover later.

### 2.2 Key Components
Let us understand each component:

#### Prometheus Server
The core component that does most of the work. It discovers targets, scrapes their metrics, stores the data in its time-series database, evaluates alerting and recording rules, and serves queries via its HTTP API. In small deployments, this might be the only Prometheus component you run.

#### Service Discovery
Instead of manually configuring every target, Prometheus can automatically discover what to scrape. In Kubernetes, it watches the API server for pods with certain annotations. In AWS, it queries EC2 for instances with certain tags. This is essential for dynamic environments where instances come and go.

#### TSDB (Time Series Database)
Prometheus includes its own storage engine optimized specifically for time-series data. It is not a general-purpose database. It stores samples as (timestamp, value) pairs, compressed efficiently, and indexed by metric name and labels. Recent data lives in memory for fast access; older data is on disk.

#### Rule Engine
Prometheus periodically evaluates two types of rules. Recording rules pre-compute expensive queries and store the results as new metrics, speeding up dashboards. Alerting rules check conditions and fire alerts when thresholds are exceeded.

#### Alertmanager
When Prometheus fires an alert, it sends it to Alertmanager. Alertmanager handles the complexity of production alerting: grouping related alerts so you get one notification instead of 100, routing different alerts to different teams, silencing alerts during maintenance windows, and preventing alert storms through inhibition.

#### Pushgateway
A workaround for the short-lived job problem. Batch jobs push their metrics to the Pushgateway before exiting, and Prometheus scrapes the Pushgateway. Use it sparingly, as it introduces a single point of failure and loses some benefits of the pull model.

#### Exporters
Not everything exposes Prometheus-format metrics natively. Exporters bridge the gap. The MySQL exporter queries MySQL for statistics and exposes them as Prometheus metrics. The Node Exporter collects Linux system metrics. There are exporters for Redis, Kafka, PostgreSQL, and dozens of other systems.

### 2.3 Scrape Configuration
**Key settings:**
| Setting | Default | Purpose |
| --- | --- | --- |
| scrape_interval | 1m | Time between scrapes |
| scrape_timeout | 10s | Per-scrape timeout |
| evaluation_interval | 1m | Rule evaluation frequency |
| metrics_path | /metrics | HTTP path to scrape |

### 2.4 Data Flow
Understanding the complete data flow helps you debug issues and explain the system in interviews:
1. **Discovery:** Prometheus queries service discovery mechanisms (Kubernetes API, Consul, EC2 tags) to build a list of targets to scrape.
2. **Scrape:** Every scrape interval (typically 15-30 seconds), Prometheus sends HTTP GET requests to each target's /metrics endpoint.
3. **Parse:** Targets return metrics in Prometheus text format. Prometheus parses this into (metric name, labels, value) tuples.
4. **Store:** Samples are appended to the local TSDB. Recent data stays in memory; older data is flushed to disk in 2-hour blocks.
5. **Query:** When you run a PromQL query or Grafana loads a dashboard, the query engine reads from the TSDB and computes the result.
6. **Evaluate:** Every evaluation interval, the rule engine runs recording rules (creating new derived metrics) and alerting rules (checking thresholds).
7. **Alert:** When alerting rule conditions are met for the specified duration, alerts are sent to Alertmanager, which routes them to the appropriate notification channels.

# 3. Data Model and Metric Types
Getting metrics right is more important than it might seem. Choose the wrong metric type and your queries will give misleading results. Use the wrong labels and you will blow up cardinality or lose the ability to filter. This section covers how Prometheus models data and how to make good choices.

### 3.1 Time Series Data Model
At its core, Prometheus stores time series data: sequences of timestamped values. Each time series is uniquely identified by a metric name plus a set of key-value pairs called labels.
**Metric name**: Describes what is being measured. Convention: `<namespace>_<name>_<unit>`.
**Labels**: Key-value pairs that identify the specific instance of a metric. Used for filtering and aggregation.
Each unique combination of metric name and label values creates a new time series. This is powerful but can lead to high cardinality if not careful.

### 3.2 Metric Types
Prometheus has four core metric types:

#### Counter
Monotonically increasing value. Only goes up (or resets to zero on restart).
**Use for:**
- Request counts
- Error counts
- Tasks completed
- Bytes processed

**Important:** Never use counters for values that can decrease. Use `rate()` or `increase()` to get meaningful values.

#### Gauge
Value that can go up and down. Represents a current state.
**Use for:**
- Current temperature
- Memory usage
- Queue depth
- Active connections
- In-progress requests

#### Histogram
Samples observations and counts them in configurable buckets. Also provides sum and count.
**Use for:**
- Request latency
- Response sizes
- Any distribution you want to analyze

**Calculating percentiles:**

#### Summary
Similar to histogram but calculates quantiles on the client side.
**Histogram vs Summary:**
| Aspect | Histogram | Summary |
| --- | --- | --- |
| Quantile calculation | Server-side (PromQL) | Client-side |
| Aggregatable | Yes | No (cannot aggregate quantiles) |
| Accuracy | Depends on bucket boundaries | Configurable |
| Configuration | Choose buckets | Choose quantiles |
| Performance | More time series (per bucket) | Lower cardinality |

**Recommendation:** Use histograms for most cases. They are aggregatable and you can calculate any percentile after the fact.

### 3.3 Naming Conventions
**Conventions:**
- Use snake_case
- Start with namespace (app name, subsystem)
- Include unit suffix (_seconds, _bytes, _total)
- Use base units (seconds not milliseconds, bytes not megabytes)
- Counters should end in _total

### 3.4 Label Best Practices
**Guidelines:**
- Labels should have bounded cardinality
- Use labels for dimensions you will filter or aggregate by
- Avoid user IDs, request IDs, or other high-cardinality values
- Prometheus adds `instance` and `job` labels automatically

# 4. PromQL Query Language
PromQL is what makes Prometheus powerful. It is a functional query language designed specifically for time-series data. You can calculate rates, aggregate across dimensions, compute percentiles, and build complex expressions. Knowing the common patterns will serve you well in interviews and in practice.

### 4.1 Basic Queries
Let us start with the fundamentals.

### 4.2 Functions

#### Rate and Increase
**When to use:**
- `rate()`: Most common, smoothed average rate
- `irate()`: When you need to see spikes
- `increase()`: When you want total count over period

#### Aggregation

#### Math Functions

#### Time Functions

### 4.3 Histogram Queries

### 4.4 Common Patterns

#### Error Rate

#### Availability

#### Saturation

#### Request Rate

### 4.5 Query Examples for Common Scenarios
| Metric | Query |
| --- | --- |
| Request rate | sum(rate(http_requests_total[5m])) |
| Error rate | sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) |
| P99 latency | histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m]))) |
| Avg latency | sum(rate(http_request_duration_seconds_sum[5m])) / sum(rate(http_request_duration_seconds_count[5m])) |
| Memory usage | container_memory_usage_bytes / container_spec_memory_limit_bytes |
| CPU usage | sum(rate(container_cpu_usage_seconds_total[5m])) by (pod) |

# 5. Instrumentation and Exporters
Prometheus can only monitor what exposes metrics. There are two ways to get metrics: instrument your own applications with Prometheus client libraries, or use exporters that bridge existing systems. Understanding both is essential for designing complete monitoring.

### 5.1 Direct Instrumentation
For your own applications, you add Prometheus client libraries that expose a /metrics endpoint. The library handles metric storage and the HTTP endpoint; you just update the metrics when interesting things happen.
**Client libraries available for:** Go, Java, Python, Ruby, .NET, Node.js, Rust, and more.

### 5.2 Exporters
Exporters bridge third-party systems to Prometheus format.
**Common exporters:**
| Exporter | Metrics Exposed |
| --- | --- |
| Node Exporter | CPU, memory, disk, network for Linux/Unix |
| MySQL Exporter | Query performance, connections, replication |
| Redis Exporter | Memory, commands, keyspace, replication |
| PostgreSQL Exporter | Connections, locks, replication, query stats |
| MongoDB Exporter | Operations, connections, memory, replication |
| Kafka Exporter | Consumer lag, partition count, broker metrics |
| Nginx Exporter | Requests, connections, response codes |
| Blackbox Exporter | Probe HTTP, TCP, ICMP, DNS endpoints |
| kube-state-metrics | Kubernetes object state (pods, deployments) |
| cAdvisor | Container resource usage |

### 5.3 Pushgateway
For short-lived jobs that cannot be scraped:
**When to use Pushgateway:**
- Batch jobs that run and exit
- Jobs behind firewalls that Prometheus cannot reach
- Jobs without persistent endpoints

**Caveats:**
- Pushgateway is a single point of failure
- Metrics persist until deleted (can show stale data)
- Loses "up" metric semantics (cannot detect job failures through missing scrapes)

### 5.4 Service Discovery
Prometheus can automatically discover targets:
**Supported discovery mechanisms:**
- Kubernetes (pods, services, endpoints, nodes)
- Consul
- AWS EC2, ECS
- Azure
- GCP GCE
- DNS
- File-based (JSON/YAML files)
- Static configuration

### 5.5 Relabeling
Transform labels during scrape or before storage:
**Use cases:**
- Filter targets to scrape
- Rename labels from service discovery
- Add environment or team labels
- Drop high-cardinality labels

# 6. Storage and Retention
Prometheus includes its own time-series database rather than relying on external storage. This design choice prioritizes reliability (no external dependencies) and performance (storage optimized for time-series patterns). Understanding how it works helps you plan capacity, configure retention, and know when you need external long-term storage.

### 6.1 Local Storage Architecture
The storage engine is optimized for a specific access pattern: recent data is queried frequently, older data is queried rarely, and writes are append-only (you never update old samples).
**How it works:**
1. **Head Block**: Recent data (last 2 hours) in memory
2. **Write-Ahead Log (WAL)**: Durability for in-memory data
3. **Block Creation**: Every 2 hours, head block is persisted to disk
4. **Compaction**: Old blocks are merged for efficiency

**Block structure:**

### 6.2 Retention Configuration

### 6.3 Storage Capacity Planning
**Key factors:**
- Number of active time series
- Scrape interval
- Retention period
- Label cardinality (more labels = larger index)

### 6.4 Remote Storage
For long-term retention, Prometheus supports remote write and read.
**Configuration:**
**Long-term storage options:**
| Solution | Description | Use Case |
| --- | --- | --- |
| Thanos | Sidecar + object storage | Multi-cluster, global view |
| Cortex | Horizontally scalable | Large scale, multi-tenant |
| VictoriaMetrics | High performance | Single tenant, high cardinality |
| Mimir | Grafana's long-term storage | Grafana ecosystem |

### 6.5 Performance Tuning
**Best practices:**
- Use SSDs for storage
- Allocate enough memory for head block
- Monitor cardinality with `prometheus_tsdb_head_series`
- Use recording rules to pre-compute expensive queries

# 7. Alerting with Alertmanager
Metrics are only useful if someone acts on them. Alerting bridges the gap between data and action. But alerting done poorly leads to alert fatigue, where on-call engineers ignore notifications because too many are false positives. Prometheus and Alertmanager together provide a sophisticated alerting system that, when configured well, pages you for real problems and stays quiet otherwise.

### 7.1 Alerting Architecture
Alerting in Prometheus is split into two parts: Prometheus evaluates alert rules and decides when to fire; Alertmanager handles routing, grouping, and notification.

### 7.2 Alert Rules
Alert rules are defined in Prometheus:
**Key components:**
| Field | Purpose |
| --- | --- |
| alert | Alert name |
| expr | PromQL expression (true = firing) |
| for | Duration before firing (pending period) |
| labels | Additional labels for routing |
| annotations | Human-readable information |

### 7.3 Alert States
**States:**
- **Inactive**: Condition not met
- **Pending**: Condition met, waiting for `for` duration
- **Firing**: Condition met for `for` duration, alert sent to Alertmanager

### 7.4 Alertmanager Configuration

### 7.5 Alertmanager Features
**Grouping**: Combine related alerts into single notification.
**Routing**: Send alerts to different receivers based on labels.
**Silencing**: Temporarily mute alerts (maintenance windows).
**Inhibition**: Suppress alerts when related alert is firing.

### 7.6 Alerting Best Practices
# 8. Scaling Prometheus
A single Prometheus server can handle a lot, often millions of time series and hundreds of thousands of samples per second. But at some point, you hit limits. Understanding when and how to scale helps you design monitoring for large deployments.
The good news is that you often do not need to scale early. The bad news is that when you do, Prometheus does not scale horizontally out of the box, you need to add architecture.

### 8.1 Single Server Limits

### 8.2 Vertical Scaling
Before horizontal scaling, optimize:

### 8.3 Functional Sharding
Split by job or team:
**Pros:**
- Simple to implement
- Clear ownership per Prometheus
- Independent failure domains

**Cons:**
- No single view without aggregation layer
- Cross-shard queries require federation or Thanos

### 8.4 Federation
Pull metrics from multiple Prometheus servers:
**Use federation for:**
- Hierarchical collection (edge → regional → global)
- Aggregated metrics only (use recording rules)
- Cross-datacenter views

**Limitations:**
- Adds latency and complexity
- Not suitable for high-cardinality data
- Can become bottleneck

### 8.5 Thanos Architecture
Thanos provides global query view and long-term storage:
**Components:**
| Component | Role |
| --- | --- |
| Sidecar | Ships blocks to object storage, serves as Store API |
| Query | Global PromQL queries across all data sources |
| Store Gateway | Serves historical data from object storage |
| Compactor | Compacts and downsamples blocks in object storage |
| Ruler | Evaluates recording and alerting rules |
| Receiver | Accepts remote write (alternative to sidecar) |

**Benefits:**
- Global query view across clusters
- Unlimited retention in object storage
- Deduplication across replicas
- Downsampling for historical queries

### 8.6 Recording Rules
Pre-compute expensive queries:
**Benefits:**
- Faster dashboard loading
- Reduced query load on Prometheus
- Consistent results across dashboards
- Required for federation

### 8.7 Scaling Decision Tree
# 9. Prometheus vs Other Monitoring Systems
In interviews, you might be asked why you chose Prometheus over alternatives, or when you would choose something else. Here is how Prometheus compares to common alternatives, with guidance on when each makes sense.

### 9.1 Prometheus vs InfluxDB
| Aspect | Prometheus | InfluxDB |
| --- | --- | --- |
| Data model | Pull-based, labels | Push-based, tags |
| Query language | PromQL | Flux (v2) / InfluxQL |
| Primary use | Monitoring & alerting | Time-series analytics |
| Storage | Local TSDB | Local TSM |
| High cardinality | Limited (~10M series) | Better support |
| Clustering | External (Thanos/Cortex) | Built-in (Enterprise) |
| Downsampling | External (Thanos) | Built-in |
| Cost | Open source | Open source + Enterprise |

**Choose Prometheus:**
- Cloud-native environments (Kubernetes)
- Operational monitoring and alerting
- Strong ecosystem (exporters, Grafana integration)

**Choose InfluxDB:**
- IoT and sensor data
- High cardinality requirements
- Time-series analytics beyond monitoring

### 9.2 Prometheus vs Datadog
| Aspect | Prometheus | Datadog |
| --- | --- | --- |
| Deployment | Self-hosted | SaaS |
| Cost | Free (infra costs) | Per-host pricing |
| Setup | DIY | Turnkey |
| Customization | Full control | Limited |
| Scale | Manual | Automatic |
| Integrations | Exporters | 600+ built-in |
| Logs & Traces | Separate tools | Unified platform |
| Support | Community | Enterprise support |

**Choose Prometheus:**
- Cost-sensitive environments
- Full control required
- Strong in-house expertise
- Data sovereignty requirements

**Choose Datadog:**
- Fast time-to-value
- Limited DevOps bandwidth
- Need unified observability platform
- Enterprise support requirements

### 9.3 Prometheus vs Graphite
| Aspect | Prometheus | Graphite |
| --- | --- | --- |
| Collection | Pull | Push |
| Data model | Multi-dimensional (labels) | Hierarchical (dot notation) |
| Query language | PromQL | Graphite functions |
| Alerting | Built-in + Alertmanager | External (Grafana) |
| Service discovery | Built-in | None |
| Storage | Efficient TSDB | Carbon + Whisper |

**Choose Prometheus:**
- Dynamic environments
- Multi-dimensional queries
- Cloud-native deployments

**Choose Graphite:**
- Existing Graphite investment
- Simple hierarchical metrics
- StatsD compatibility needed

### 9.4 Prometheus vs CloudWatch
| Aspect | Prometheus | CloudWatch |
| --- | --- | --- |
| Deployment | Self-hosted | AWS managed |
| AWS integration | Exporters needed | Native |
| Query language | PromQL | Insights Query |
| Cost | Infrastructure | Per metric/query |
| Multi-cloud | Yes | AWS only |
| Alerting | Alertmanager | CloudWatch Alarms |

**Choose Prometheus:**
- Multi-cloud or hybrid
- Custom applications
- Complex queries
- Cost control

**Choose CloudWatch:**
- AWS-only deployment
- Native AWS service metrics
- Minimal operational overhead

### 9.5 Prometheus vs OpenTelemetry
OpenTelemetry is not a monitoring system but a collection standard:
**Relationship:**
- OpenTelemetry: Collection and instrumentation standard
- Prometheus: Metrics storage and querying backend
- They work together: OTel Collector can export to Prometheus

# Summary
Prometheus has become the standard for metrics monitoring in cloud-native environments. When you design a system in an interview and mention monitoring, Prometheus is often the right choice. Here are the key points to internalize:

#### Understand why pull works
Prometheus scrapes targets rather than receiving pushes. This gives centralized control over what gets monitored, implicit health checking through failed scrapes, and easier debugging since you can curl /metrics directly. The trade-off is needing network access to targets and challenges with short-lived jobs.

#### Choose metric types deliberately
Counters for things that only increase (requests, errors, bytes). Gauges for values that go up and down (temperature, queue depth, connections). Histograms for distributions where you want percentiles (latency, sizes). The wrong type gives misleading results.

#### Master the essential PromQL patterns
`rate()` converts counter increases to per-second rates. `sum by (label)` aggregates across dimensions. `histogram_quantile()` calculates percentiles from histogram buckets. These three patterns cover most monitoring needs.

#### Protect against cardinality explosions
Every unique combination of metric name and label values creates a time series. Adding user_id as a label with a million users creates a million series per metric. Prometheus memory and query performance degrade badly. Use bounded labels like status_code or endpoint, never unbounded ones like user_id or request_id.

#### Design alerts around symptoms and SLOs
Alert when error rate exceeds your SLA threshold, not when a specific database connection fails. Use the `for` clause to require conditions persist, avoiding pages for brief spikes. Route critical alerts to PagerDuty, warnings to Slack. Use inhibition to prevent alert storms.

#### Plan storage and scale deliberately
Local storage handles 15-30 days well. For longer retention, add Thanos or similar to ship blocks to object storage. For very large deployments, shard by team or job and use Thanos Query to federate views. Recording rules pre-compute expensive queries for fast dashboards.

#### Remember the ecosystem
Prometheus alone is just metrics storage. Grafana provides visualization. Alertmanager handles notification routing. Exporters bridge third-party systems. Thanos adds long-term storage and global querying. The complete stack is more powerful than any single component.
# References
- [Prometheus Documentation](https://prometheus.io/docs/) - Official Prometheus documentation covering all features and configuration
- [Prometheus: Up and Running](https://www.oreilly.com/library/view/prometheus-up/9781492034131/) - O'Reilly book by Brian Brazil covering Prometheus architecture and best practices
- [Designing Data-Intensive Applications](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) - Martin Kleppmann's book with excellent coverage of monitoring and observability
- [SRE Book: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) - Google's SRE book chapter on monitoring principles
- [Thanos Documentation](https://thanos.io/tip/thanos/getting-started.md/) - Documentation for scaling Prometheus with Thanos
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/) - Quick reference for PromQL functions and patterns

# Quiz

## Prometheus Quiz
What type of data is Prometheus primarily designed to collect and query?