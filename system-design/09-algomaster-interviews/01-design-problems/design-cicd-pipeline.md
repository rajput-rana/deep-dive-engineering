# Design CI/CD Pipeline

## What is a CI/CD Pipeline?

A CI/CD (Continuous Integration/Continuous Deployment) Pipeline is an automated workflow that builds, tests, and deploys code changes from development to production.
The core idea is to automate the software delivery process so that developers can push code frequently while maintaining quality and reliability. Every code commit triggers a series of automated steps: building the application, running tests, creating artifacts, and deploying to various environments.
**Popular Examples:** [Jenkins](https://www.jenkins.io/), [GitHub Actions](https://github.com/features/actions), [GitLab CI/CD](https://docs.gitlab.com/ee/ci/), [CircleCI](https://circleci.com/), [Azure DevOps](https://azure.microsoft.com/en-us/products/devops)
This system design problem touches on distributed systems, job scheduling, artifact management, and deployment strategies, concepts that are fundamental to modern software engineering.
In this chapter, we will explore the **high-level design of a CI/CD Pipeline**.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
Before jumping into architecture diagrams, we need to understand what we are actually building. CI/CD pipelines can range from simple "run tests on every push" systems to complex orchestration platforms that manage thousands of concurrent builds across multiple data centers. The requirements dramatically affect the design.
Here is how a requirements discussion might unfold in an interview:
**Candidate:** "What is the expected scale? How many builds per day and how many concurrent builds should we support?"
**Interviewer:** "Let's aim for 100,000 builds per day with up to 1,000 concurrent builds at peak times."
**Candidate:** "Should we support multiple programming languages and build environments?"
**Interviewer:** "Yes, the system should be language-agnostic and support custom build environments via containers."
**Candidate:** "Do we need to support both CI and CD, or just CI?"
**Interviewer:** "Both. The system should handle building, testing, and deploying to multiple environments."
**Candidate:** "Should the system support parallel job execution within a single pipeline?"
**Interviewer:** "Yes, pipelines should support both sequential and parallel stages."
**Candidate:** "How should we handle build artifacts? Do we need long-term storage?"
**Interviewer:** "Yes, artifacts should be stored and versioned. We need to retain them for at least 30 days."
**Candidate:** "What deployment strategies should we support?"
**Interviewer:** "At minimum, rolling deployments. Blue-green and canary deployments are nice-to-have."
This conversation reveals several important constraints that will influence our design. Let's formalize these into functional and non-functional requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core capabilities our system must support:
- **Pipeline Execution:** Execute multi-stage pipelines with sequential and parallel steps.
- **Build Isolation:** Run builds in isolated environments (containers) to ensure reproducibility.
- **Artifact Management:** Store, version, and retrieve build artifacts.
- **Deployment:** Deploy applications to multiple environments (staging, production).
- **Notifications:** Notify users of build status via webhooks, email, or Slack.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Availability:** The system must be highly available (99.9% uptime).
- **Scalability:** Handle 100,000+ builds per day with 1,000+ concurrent builds.
- **Low Latency:** Build queue time should be under 30 seconds during normal load.
- **Durability:** Pipeline logs and artifacts must be persisted reliably.
- **Security:** Secrets management, build isolation, and access control.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our architectural decisions, particularly around compute resources, storage, and queue design.

### 2.1 Traffic Estimates
Let's start with the numbers from our requirements discussion and work through what they mean for our infrastructure.

#### Build Triggers
We expect 100,000 new builds per day. Converting to queries per second:
That does not sound like much, but builds are not evenly distributed throughout the day. Monday mornings are busy as developers push their weekend work. Afternoons before a release deadline see spikes. During peak hours, we might see 3x the average load:

#### Concurrent Builds
Here is where things get interesting. Unlike a typical web request that completes in milliseconds, builds take a long time. If the average build runs for 10 minutes, we need to think about how many builds are running at any given moment.
This means we need infrastructure to run 1,000 builds simultaneously, and each build needs its own isolated environment with dedicated CPU and memory.

### 2.2 Storage Estimates
Each build generates several types of data that we need to store:

#### Component Breakdown:
- **Build logs:** Console output, typically 500 KB on average (can range from a few KB to several MB for verbose builds)
- **Artifacts:** Compiled binaries, Docker images, test reports. The average is around 50 MB, though some builds produce gigabytes of artifacts
- **Metadata:** Pipeline configuration, timing data, status information, about 5 KB

Now let's project storage needs over our 30-day retention period:
| Component | Daily Storage | 30-Day Storage |
| --- | --- | --- |
| Logs | 100K × 500 KB = 50 GB | ~1.5 TB |
| Artifacts | 100K × 50 MB = 5 TB | ~150 TB |
| Metadata | 100K × 5 KB = 500 MB | ~15 GB |

A few observations from these numbers:
1. **Artifacts dominate storage:** At 150 TB for 30 days, artifacts are 99% of our storage needs. This suggests we should use cost-effective object storage (like S3) rather than expensive database storage.
2. **Log storage is manageable:** 1.5 TB of logs fits comfortably in most logging solutions. We might consider compression, which typically achieves 5-10x reduction for text logs.
3. **Cleanup is essential:** Without retention policies, storage would grow unbounded. After 30 days, expired artifacts need to be cleaned up automatically.

### 2.3 Compute Estimates
This is where CI/CD systems get expensive. Each build needs dedicated compute resources.
If we use 2-vCPU workers, we need roughly 1,000 worker nodes at peak. With some buffer for headroom and failed nodes, a pool of around 1,200 workers is reasonable.

### 2.4 Key Insights
These estimates reveal several important design implications:
1. **Compute is the bottleneck:** Unlike typical web services where we worry about requests per second, here we worry about build-minutes. The limiting factor is how many parallel builds we can support.
2. **Scaling must be dynamic:** Build traffic varies wildly throughout the day and week. We cannot afford to run 1,200 workers 24/7 when we only need 200 at night. Auto-scaling is essential.
3. **Artifact storage needs its own strategy:** 150 TB of artifacts per month means we need cost-effective object storage with lifecycle policies, not database storage.
4. **Workers should be ephemeral:** At this scale, worker nodes will fail regularly. The system must handle workers coming and going without losing builds in progress.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. A CI/CD system has two main types of users: developers who want to trigger and monitor builds, and the build workers themselves that need to fetch jobs and upload artifacts. We will design RESTful APIs for both.

### 3.1 Trigger Pipeline

#### Endpoint: POST /pipelines/{pipeline_id}/runs
This is the primary endpoint for starting a build. It can be called by a developer through the UI, by a git webhook when code is pushed, or by another system like a scheduler.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| branch | string | No | Git branch to build. Defaults to the repository's default branch |
| commit_sha | string | No | Specific commit to build. If not provided, uses the latest commit on the branch |
| variables | object | No | Key-value pairs to override pipeline variables (e.g., {"DEPLOY_ENV": "staging"}) |

#### Example Request:

#### Success Response (201 Created):
The response includes a `web_url` so developers can immediately click through to watch the build progress.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Pipeline does not exist | The pipeline_id is invalid or the user does not have access |
| 429 Too Many Requests | Rate limited | User has triggered too many builds in a short period |
| 400 Bad Request | Invalid parameters | The branch or commit_sha does not exist |

### 3.2 Get Pipeline Run Status

#### Endpoint: GET /pipelines/{pipeline_id}/runs/{run_id}
Developers and monitoring systems poll this endpoint to track build progress. It returns the overall status along with details about each stage.

#### Success Response (200 OK):
The `stages` array shows each stage's status, making it easy to see where the build currently is and where it might have failed.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Run does not exist | The run_id is invalid or has been deleted |

### 3.3 Upload Artifact

#### Endpoint: POST /runs/{run_id}/artifacts
Build workers call this endpoint to upload artifacts at the end of a build stage. This might be a compiled binary, a Docker image manifest, test coverage reports, or any other file the pipeline produces.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | A descriptive name for the artifact (e.g., "app-binary", "coverage-report") |
| file | binary | Yes | The artifact file, sent as multipart form data |
| stage_id | string | No | Which stage produced this artifact |

#### Success Response (201 Created):
The `download_url` is typically a signed URL that allows temporary access without authentication, useful for deployment scripts.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Run does not exist | The run_id is invalid |
| 413 Payload Too Large | Artifact too big | The file exceeds the maximum allowed size (typically 1-5 GB) |

### 3.4 Download Artifact

#### Endpoint: GET /artifacts/{artifact_id}
Developers, deployment scripts, and other pipelines use this endpoint to retrieve previously uploaded artifacts.

#### Success Response (200 OK):
Returns the binary file with appropriate `Content-Type` and `Content-Disposition` headers for download.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Artifact does not exist | The artifact_id is invalid |
| 410 Gone | Artifact expired | The artifact was deleted after its retention period |

### 3.5 API Design Considerations
A few design decisions worth noting:
**Webhook-style notifications:** Rather than requiring clients to poll for status, we could also support webhooks. Clients register a URL, and we POST status updates as they happen. This reduces API load and provides faster feedback.
**Long polling for logs:** Build logs stream in real-time as the build runs. A dedicated endpoint like `GET /runs/{run_id}/logs?follow=true` can use long polling or server-sent events to stream logs to the UI.
**Idempotency:** Triggering a build with the same branch and commit should be idempotent within a short window, returning the existing run rather than creating a duplicate. This prevents issues when webhooks are delivered multiple times.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible flow and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system needs to handle three fundamental concerns:
1. **Pipeline Orchestration:** Parse pipeline definitions and coordinate execution, figuring out which stages can run in parallel and which need to wait for dependencies.
2. **Build Execution:** Actually run the builds in isolated environments with dedicated compute resources.
3. **Artifact and Deployment Management:** Store what the builds produce and deploy those artifacts to target environments.

These concerns have different scaling characteristics. Pipeline orchestration is mostly database and queue operations. Build execution is compute-intensive. Artifact storage is I/O-intensive. Separating them into distinct services lets us scale each independently.
Let's visualize the overall flow before diving into each piece:
Let's build this architecture step by step, starting with pipeline triggering and orchestration.

## 4.1 Requirement 1: Triggering and Orchestrating Pipelines
When a developer pushes code or manually triggers a build, several things need to happen behind the scenes:
1. Authenticate the request and check permissions
2. Fetch the pipeline configuration from the repository
3. Parse the YAML to understand the stages and their dependencies
4. Create a record for this pipeline run
5. Queue the first stage(s) for execution
6. Return a run ID so the developer can track progress

Let's introduce the components we need to make this work.

### Components for Pipeline Orchestration

#### API Gateway
Every request enters through the API Gateway. Think of it as the front door to our system, handling concerns that are common across all requests.
The gateway terminates SSL connections, authenticates requests using API keys or OAuth tokens, enforces rate limits to prevent abuse, and routes requests to the appropriate backend service. By handling these cross-cutting concerns at the edge, we keep our application services focused on business logic.
For a CI/CD system, the gateway also needs to handle webhook payloads from Git providers like GitHub and GitLab. These webhooks have specific signature verification requirements that the gateway should validate before passing the request along.

#### Pipeline Service
This is the brain of our operation. It orchestrates the entire workflow: parsing pipeline configurations, creating run records, determining execution order, and queueing jobs for workers to pick up.
The Pipeline Service needs to be smart about dependencies. Consider a pipeline where unit tests and linting can run in parallel after the build stage, but integration tests must wait for both to complete. The service builds a directed acyclic graph (DAG) from the pipeline configuration and uses it to determine which stages are ready to run at any given moment.
We want this service to be stateless so we can run multiple instances behind a load balancer. All state lives in the database and job queue, making horizontal scaling straightforward.

#### Pipeline Database
Stores everything about pipelines and their runs: the pipeline configuration, every run's status, the status of each stage within a run, timing information, and who triggered the build. We need fast lookups by run ID (the primary use case) and efficient queries by pipeline ID and status (for listing runs and monitoring).

### The Trigger Flow in Action
Here is how all these components work together when a developer pushes code or manually triggers a build:
Let's walk through this step by step:
1. **Request arrives at API Gateway:** A developer clicks "Run Pipeline" in the UI or pushes code that triggers a webhook. The gateway authenticates the request and checks rate limits.
2. **Pipeline Service takes over:** The service receives the request and needs to understand what pipeline to run. It fetches the pipeline configuration file (typically `pipeline.yaml` or `.github/workflows/main.yaml`) from the repository at the specified commit.
3. **Parse the configuration:** The YAML file defines stages, their commands, dependencies, and resource requirements. The service parses this into an internal representation, essentially building a DAG of stages.
4. **Create database records:** The service creates a new run record with status "queued" and creates stage records for each stage defined in the pipeline. Initially, all stages have status "pending".
5. **Queue the first stages:** The service identifies which stages have no dependencies (typically just "build" or "checkout") and adds them to the job queue. Workers will pick these up and execute them.
6. **Return immediately:** The developer gets back a run ID immediately. They do not wait for the build to complete, just for it to be queued.

By putting stages in a queue, we decouple orchestration from execution. The Pipeline Service does not need to know how many workers are available or which one is free. The queue handles distribution, retries, and load balancing. This separation of concerns makes both components simpler and more scalable.

## 4.2 Requirement 2: Executing Build Jobs
Now for the compute-intensive part. Jobs are sitting in the queue, waiting to be executed. We need workers to pick them up, run them in isolated environments, and report results back to the Pipeline Service so it can queue the next stages.
This is where CI/CD systems spend most of their resources. Each build needs a fresh environment, dedicated CPU and memory, and the ability to run arbitrary commands. The challenge is doing this at scale while keeping queue times low.

### Components for Build Execution

#### Job Queue
A distributed message queue sits between the Pipeline Service and the workers. When stages are ready to execute, the Pipeline Service adds them to the queue. Workers poll the queue for jobs.
The queue needs to handle several tricky scenarios:
- **Priority:** A production hotfix should jump ahead of routine CI builds
- **Visibility timeouts:** If a worker takes a job but crashes, the job should become available again after a timeout
- **Dead letter queue:** Jobs that fail repeatedly should be moved aside for investigation rather than retried forever

RabbitMQ, Amazon SQS, and Redis Streams are all reasonable choices here. For a cloud deployment, SQS is often the simplest option because it is fully managed and handles the distributed systems complexity for you.

#### Worker Pool
This is where the actual builds happen. Each worker is a machine (physical or virtual) that can execute build jobs. When a worker picks up a job, it:
1. Pulls the Docker image specified in the pipeline configuration
2. Creates a fresh container with that image
3. Clones the source code into the container
4. Injects any secrets the build needs (API keys, credentials)
5. Executes the build commands
6. Streams logs to the Log Service
7. Reports success or failure back to the Pipeline Service

Workers need to be stateless. Any job should be able to run on any worker. This makes scaling simple: add more workers to handle more concurrent builds.

#### Worker Manager
Someone needs to watch over the worker pool. The Worker Manager monitors queue depth and scales the worker pool up or down to match demand. It also health-checks workers and replaces any that become unresponsive.
This is where the cost optimization happens. Running 1,200 workers 24/7 would be expensive. The Worker Manager scales down to 200 workers at night and on weekends, then scales back up on Monday morning when developers start pushing code.

#### Log Service
Build logs are critical for debugging. When a build fails, developers need to see exactly what happened. The Log Service collects log streams from all running builds and stores them durably.
Logs should be streamable in real-time so developers can watch builds in progress. They also need to be searchable after the fact. A common pattern is to stream logs through a service like Kafka or Kinesis, then persist them to object storage with indexing in Elasticsearch.

#### Secret Manager
Builds often need credentials: database passwords for integration tests, API keys for external services, signing certificates for release builds. These secrets cannot be stored in source control.
The Secret Manager securely stores secrets and provides them to builds at runtime. It should support fine-grained access control (this secret is only available to builds of this repository) and audit logging (who accessed which secret when).

### The Build Execution Flow
Here is how a build job moves from queue to completion:
Let's trace through what happens when a worker picks up a job:
1. **Worker polls the queue:** The worker continuously polls the job queue looking for work. When a job is available, the queue returns the job details including which stage to run, the Docker image to use, the repository URL, and the commit SHA.
2. **Pull the Docker image:** The pipeline configuration specifies an image like `node:18` or `python:3.11`. The worker pulls this image from a container registry. For common images, this is often cached locally for speed.
3. **Create an isolated container:** The worker spins up a fresh container from the image, with strict resource limits. A typical configuration might be 2 vCPUs, 4 GB RAM, and 10 GB disk. The container is completely isolated from other builds.
4. **Clone the source code:** The worker clones the repository at the exact commit specified in the job. This ensures reproducibility: running the same job twice will always start with the same code.
5. **Inject secrets:** If the pipeline needs credentials (API keys, database passwords), the worker fetches them from the Secret Manager and injects them as environment variables. The secrets are never written to disk in the container.
6. **Execute build commands:** This is where the actual work happens. The worker runs whatever commands are defined in the pipeline: `npm install`, `npm test`, `docker build`, and so on. Output is streamed to the Log Service in real-time.
7. **Report results:** When the commands complete, the worker reports back to the Pipeline Service. If the stage succeeded, the Pipeline Service checks whether any dependent stages can now run and queues them. If the stage failed and it was a required stage, the entire run is marked as failed.
8. **Clean up:** The container is destroyed, ensuring no state leaks between builds.

This is where the visibility timeout matters. When a worker takes a job from the queue, the job becomes invisible to other workers for a configurable period (say, 30 minutes). The worker must periodically send heartbeats to extend this timeout. 
If the worker crashes, it stops sending heartbeats, the timeout expires, and the job becomes visible again. Another worker picks it up and tries again.

## 4.3 Requirement 3: Managing Artifacts and Deployments
The CI part of our system is now working: we can trigger builds and execute them in isolated containers. But the build outputs need to go somewhere. When a build compiles a binary, where does that binary get stored? When it is time to deploy, how does the deployment service find the right artifact?
This is where the Artifact Service and Deployment Service come in. They handle the "CD" part of CI/CD, moving build outputs from workers to persistent storage and from storage to running infrastructure.

### Components for Artifacts and Deployment

#### Artifact Service
The Artifact Service is responsible for storing and retrieving build outputs. When a worker finishes building a Docker image or compiling a binary, it uploads the artifact to this service.
The service handles several concerns:
- **Storage:** Artifacts are stored in object storage (S3, GCS, or similar) for durability and cost-effectiveness
- **Versioning:** Each artifact is tagged with the pipeline run ID and stage, so you can always trace back to the exact build that produced it
- **Signed URLs:** When someone needs to download an artifact, the service generates a time-limited signed URL that allows temporary access without authentication
- **Retention:** Artifacts are automatically deleted after the retention period (30 days in our case) to control storage costs

#### Object Storage
We use object storage like Amazon S3 or Google Cloud Storage for the actual artifact files. Object storage is perfect for this use case: it is cheap, durable (11 nines on S3), and scales without any management overhead on our part.
The key insight is that we do not need a traditional database for artifact content. We store metadata (artifact name, size, which run produced it, expiration date) in PostgreSQL, but the actual bytes go to object storage.

#### Deployment Service
The Deployment Service takes artifacts and puts them into running infrastructure. When a pipeline includes a deployment stage, the Pipeline Service calls the Deployment Service with details about what to deploy and where.
The service supports different deployment strategies:
- **Rolling deployment:** Replace instances one at a time, ensuring the service never goes fully down
- **Blue-green deployment:** Bring up a complete parallel environment, then switch traffic all at once
- **Canary deployment:** Route a small percentage of traffic to the new version, then gradually increase if metrics look good

The service also tracks deployment history, making rollbacks easy: just redeploy the previous artifact.

### The Artifact Upload Flow
After a build stage completes successfully, the worker needs to upload any artifacts it produced:
The upload is designed to handle large files efficiently:
1. **Streaming upload:** We stream the file directly from the worker to object storage without buffering the entire file in memory. This handles large artifacts (Docker images can be gigabytes) without overwhelming the Artifact Service.
2. **Checksum verification:** Both the worker and object storage calculate checksums. We verify they match to detect corruption during transfer.
3. **Automatic expiration:** When we insert the artifact record, we calculate `expires_at` based on the retention policy (30 days). A background job periodically scans for expired artifacts and deletes them.

### The Deployment Flow
When the pipeline reaches a deployment stage, here is what happens:
Let's trace through a deployment to staging:
1. **Pipeline Service triggers deployment:** The test stage passed, so the Pipeline Service queues the deploy stage. When a worker picks it up, it calls the Deployment Service rather than running commands in a container.
2. **Fetch the artifact:** The Deployment Service asks the Artifact Service for the download URL of the Docker image or binary produced earlier in the pipeline.
3. **Fetch secrets:** Deployment usually requires credentials, things like Kubernetes cluster access, database connection strings for migrations, or API keys for health checks.
4. **Apply the deployment:** For a Kubernetes environment, the Deployment Service generates a manifest with the new image tag and applies it to the cluster. For VMs, it might use Ansible or SSH to deploy.
5. **Monitor health:** This is critical. The service does not just fire-and-forget. It watches the deployment progress, checking that new pods come up healthy and old pods drain gracefully.
6. **Handle failure:** If health checks fail, the service automatically rolls back to the previous version and reports failure to the Pipeline Service. Nobody wants a deployment that takes down production.

## 4.4 Putting It All Together
Now that we have designed all three pieces, let's step back and see the complete architecture. We have built a system that can take a git push and turn it into a running deployment, automatically.
The architecture follows a layered approach, with each layer having a specific responsibility:
**Client Layer:** Builds can be triggered by developers manually, by git webhooks when code is pushed, or by scheduled jobs for nightly builds. From our system's perspective, they all enter through the same API.
**Gateway Layer:** The API Gateway sits at the edge, handling authentication, rate limiting, and routing. It protects our backend services from invalid requests and abuse.
**Core Services:** These are the brains of the operation. The Pipeline Service orchestrates execution. The Artifact Service manages build outputs. The Deployment Service handles deployments. The Log Service collects and stores logs. The Secret Manager securely provides credentials.
**Queue Layer:** The Job Queue decouples orchestration from execution. The Dead Letter Queue catches jobs that fail repeatedly so they can be investigated without blocking the main queue.
**Worker Layer:** The Worker Manager scales the worker pool based on demand. Workers are stateless and ephemeral. They pick up jobs, run them in containers, and report results.
**Storage Layer:** PostgreSQL stores structured data: pipeline configurations, run history, stage status. Object storage holds large unstructured data: artifacts and logs.
**Deployment Targets:** These are the environments we deploy to. In a real system, there might be many more: dev, staging, canary, production-us-east, production-eu-west, and so on.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| API Gateway | Auth, rate limiting, routing | Managed service (auto-scales) |
| Pipeline Service | Pipeline orchestration, state management | Horizontal (stateless) |
| Job Queue | Work distribution, retry handling | Managed service or cluster |
| Worker Pool | Build execution | Horizontal (add workers) |
| Worker Manager | Auto-scaling, health monitoring | Single leader with failover |
| Artifact Service | Artifact storage and retrieval | Horizontal (stateless) |
| Deployment Service | Deployment orchestration | Horizontal (stateless) |
| Log Service | Log collection and storage | Horizontal with sharding |
| Secret Manager | Credential storage | Managed service (Vault, AWS Secrets Manager) |
| PostgreSQL | Metadata storage | Read replicas, then sharding |
| Object Storage | Artifact and log storage | Managed service (auto-scales) |

This architecture handles our requirements well: the stateless services scale horizontally for load, the queue absorbs traffic spikes, and the storage layer provides durability without breaking the bank.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Choosing the right database and designing an efficient schema are critical decisions that affect performance, scalability, and operational complexity.

## 5.1 Choosing the Right Database
The database choice is not always obvious. Let's think through our access patterns and requirements:

#### What we need to store:
- Pipeline configurations that define what stages to run
- Pipeline runs (hundreds of thousands per month) with status and timing information
- Stages within each run, with their individual statuses and dependencies
- Artifact metadata (not the artifacts themselves, those go to object storage)

#### How we access the data:
- Most reads are point lookups by run_id (developers checking their build status)
- We need to list runs by pipeline_id with pagination
- We need to query by status to find running or queued builds
- We need to update stage statuses as builds progress

#### Consistency requirements:
- When a stage completes, we need to atomically update its status and check if dependent stages can run
- Developers should see their build status immediately after triggering (no eventual consistency delays)

Given these requirements, a relational database like PostgreSQL is a good fit:
PostgreSQL gives us the transactional guarantees we need when updating stage statuses. It supports the varied query patterns (by run_id, by status, by time range). And it has mature operations tooling for backups, replication, and monitoring.
**What about NoSQL?** A document database like MongoDB could work, but we do not really benefit from schemaless flexibility here. Our data model is quite structured. And we would lose the transactional guarantees that make stage dependency management simpler.
**What about artifacts and logs?** These go to object storage, not the database. Artifacts are large binary files (megabytes to gigabytes). Logs are append-only text streams. Neither fits well in a relational database, and object storage is much cheaper and more scalable for this data.

## 5.2 Database Schema
With our database choice made, let's design the schema. We have four main tables that form the core data model: Pipelines, Pipeline Runs, Stages, and Artifacts.

### Pipelines Table
This table stores the pipeline definitions. Each row represents a repository's CI/CD configuration.
| Field | Type | Description |
| --- | --- | --- |
| pipeline_id | UUID (PK) | Unique identifier. Using UUID avoids predictable IDs |
| name | VARCHAR(255) | Human-readable name (e.g., "backend-api-ci") |
| repository_url | VARCHAR(512) | Git repository URL |
| config_path | VARCHAR(255) | Path to the config file (e.g., .github/workflows/main.yaml) |
| created_at | TIMESTAMP | When the pipeline was first created |
| updated_at | TIMESTAMP | Last time the configuration was refreshed |

Most organizations have tens to hundreds of pipelines, so this table stays small. The primary access pattern is lookup by pipeline_id when triggering a run.

### Pipeline Runs Table
This is the heart of our schema. Each row represents one execution of a pipeline.
| Field | Type | Description |
| --- | --- | --- |
| run_id | UUID (PK) | Unique identifier for this run |
| pipeline_id | UUID (FK) | Which pipeline this run belongs to |
| status | ENUM | One of: queued, running, success, failed, cancelled |
| branch | VARCHAR(255) | Git branch being built (e.g., "main", "feature/auth") |
| commit_sha | CHAR(40) | The exact commit hash (40 hex characters for git) |
| triggered_by | VARCHAR(255) | User ID or "webhook" or "scheduled" |
| started_at | TIMESTAMP | When the first stage started executing |
| finished_at | TIMESTAMP | When the last stage completed (null if still running) |
| created_at | TIMESTAMP | When the run was queued |

This table grows quickly (100,000 rows per day in our case). We need careful indexing:
The partial index on status only indexes rows that are queued or running, which is a small fraction of total runs. This keeps the index small and fast.

### Stages Table
Each pipeline run consists of multiple stages. This table tracks each stage's status independently.
| Field | Type | Description |
| --- | --- | --- |
| stage_id | UUID (PK) | Unique identifier for this stage execution |
| run_id | UUID (FK) | Which pipeline run this stage belongs to |
| name | VARCHAR(255) | Stage name (e.g., "build", "test", "deploy-staging") |
| status | ENUM | One of: pending, running, success, failed, skipped |
| order | INTEGER | Execution order (for UI display) |
| depends_on | UUID[] | Array of stage_ids that must complete first |
| started_at | TIMESTAMP | When this stage started executing |
| finished_at | TIMESTAMP | When this stage completed |
| worker_id | VARCHAR(255) | Which worker executed this stage (for debugging) |
| logs_url | VARCHAR(512) | URL to retrieve logs for this stage |

The `depends_on` field is interesting. It is an array of stage IDs that must complete successfully before this stage can run. When a stage completes, we query for stages that depend on it and check if all their dependencies are now satisfied.

### Artifacts Table
Stores metadata about build artifacts. The actual artifact bytes go to object storage.
| Field | Type | Description |
| --- | --- | --- |
| artifact_id | UUID (PK) | Unique identifier for this artifact |
| run_id | UUID (FK) | Which pipeline run produced this artifact |
| stage_id | UUID (FK) | Which stage produced this artifact |
| name | VARCHAR(255) | Artifact name (e.g., "app-binary", "test-results.xml") |
| storage_path | VARCHAR(512) | Path in object storage (e.g., "s3://bucket/artifacts/abc123") |
| size_bytes | BIGINT | File size for display and quota enforcement |
| checksum | CHAR(64) | SHA-256 checksum for integrity verification |
| expires_at | TIMESTAMP | When this artifact should be deleted |
| created_at | TIMESTAMP | When the artifact was uploaded |

**Why store the storage_path?** We could derive it from the artifact_id, but storing it explicitly makes it easier to change storage locations or migrate between storage providers.
**Index for cleanup:**
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts of our design: how to orchestrate complex pipelines, how to isolate builds securely, how to design the job queue, deployment strategies, handling failures, and scaling the worker pool.

## 6.1 Pipeline Orchestration Strategies
The Pipeline Service needs to execute stages in the right order. This sounds simple, but real pipelines have complex dependencies. 
The build stage must complete before tests run. Unit tests and linting can run in parallel. Integration tests wait for both. Deployment to staging happens only if all tests pass. And the whole thing might need to run across multiple OS versions simultaneously.
In this example, Unit Tests and Lint can run in parallel after Build completes. But Integration Tests must wait for both to finish. How do we implement this orchestration? 
There are two main approaches.

### Approach 1: Event-Driven Orchestration
In this approach, the Pipeline Service reacts to events. When a stage completes, it emits a `StageCompleted` event. The orchestrator processes this event, updates the database, and checks which stages can now run.

#### How It Works:
1. When a pipeline run starts, the orchestrator parses the YAML configuration and builds a directed acyclic graph (DAG) representing stage dependencies.
2. Stages with no dependencies (typically just "build") are immediately queued for execution.
3. Workers pick up these stages and execute them. When finished, they report back to the Pipeline Service.
4. The Pipeline Service receives the completion event and does two things:
5. Any stages whose dependencies are all satisfied get queued. The process continues until all stages complete or a required stage fails.

#### Why This Works Well:
The event-driven approach is naturally efficient. We only do work when something actually happens. If the queue is empty, we do nothing. If a stage completes, we immediately check what can run next.
It also handles parallelism naturally. When Build completes, we queue both Unit Tests and Lint. They run on different workers concurrently. When both complete, Integration Tests becomes unblocked.

#### The Tricky Part: Out-of-Order Events
In a distributed system, events can arrive out of order. What if the "lint completed" event arrives before the "unit-tests started" event? The orchestrator must be careful to only queue Integration Tests when both dependencies are truly complete, not just when one event arrives.
The solution is to always check the database state, not rely solely on event content. When we receive "lint completed", we query the database to check all of lint's dependents. For each dependent, we verify all its dependencies are satisfied before queuing.

### Approach 2: Polling-Based Orchestration
A simpler alternative is to have a scheduler that periodically scans the database for stages ready to run.

#### How It Works:
This query finds stages that are pending and have all dependencies satisfied. The scheduler queues any stages that match.

#### Pros:
- Simpler to implement and reason about
- No event handling complexity
- Easy to debug by inspecting the database

#### Cons:
- Adds latency: if you poll every 5 seconds, stages wait up to 5 seconds after their dependencies complete
- Database load: running this query frequently across many active runs adds up
- Less efficient: keeps polling even when nothing is ready

### Which Approach Should You Choose?
**Use event-driven orchestration** for production systems. The latency benefits and efficiency gains outweigh the additional complexity. GitHub Actions, GitLab CI, and CircleCI all use event-driven approaches.
**Add a fallback polling mechanism** to catch any missed events. Run a lightweight scanner every 30 seconds that finds stages stuck in "pending" status for too long and queues them. This ensures forward progress even if an event gets lost.

### Pipeline and Stage State Transitions
A clear state machine helps with debugging and ensures correct behavior. Here is how pipeline runs transition between states:
A run starts in **Queued** when created. It moves to **Running** as soon as the first stage begins executing. It ends in **Success** if all stages complete successfully, **Failed** if any required stage fails, or **Cancelled** if a user explicitly cancels it.
Individual stages have their own state machine:
A stage starts in **Pending** when the pipeline run is created. It moves to **Running** when all its dependencies are satisfied and a worker picks it up. It ends in **Success**, **Failed**, or **Skipped** (if a conditional rule determined it should not run).

#### The Retry Case:
When a stage fails, a user can trigger a retry. This moves the stage back to **Pending**, and the orchestrator checks if its dependencies are still satisfied. If they are (dependencies do not need to re-run), the stage immediately becomes **Running** again.

## 6.2 Build Isolation and Containerization
Imagine what would happen if builds were not isolated. Team A's Python 2.7 project runs on the same machine as Team B's Python 3.11 project. Team A's build installs dependencies that break Team B's build. Or worse, Team C's build runs malicious code that steals secrets from Team A's environment.
Build isolation prevents these scenarios. Each build runs in a clean, reproducible environment. When the build finishes, the environment is destroyed, leaving no trace that could affect subsequent builds.
There are three main approaches to isolation, each with different trade-offs.

### Approach 1: Docker Containers
Docker containers are the most common choice for CI/CD isolation. Each build runs inside a fresh container with its own filesystem, network namespace, and process tree.

#### How It Works:
The pipeline configuration specifies a Docker image (e.g., `node:18`, `python:3.11`, or a custom image). When the worker receives a build job, it:
1. Pulls the Docker image from a container registry (usually cached locally for common images)
2. Creates a container with strict resource limits: CPU quota, memory limit, disk quota
3. Mounts the source code as read-only and a workspace directory as read-write
4. Injects secrets as environment variables (never written to disk)
5. Runs the build commands inside the container
6. Destroys the container after the build, regardless of success or failure

#### Why Docker Works Well:
Containers start in seconds. The image provides a reproducible environment, the same image always has the same tools installed. Filesystem and process isolation mean builds cannot interfere with each other. And resource limits prevent runaway builds from starving other builds on the same machine.

#### The Limitation:
Docker containers share the host kernel. For most CI workloads, this is fine. But if you need to test kernel modules or run builds that modify system-level settings, containers are not isolated enough.

### Approach 2: Virtual Machines
For stronger isolation, each build can run inside a dedicated VM. The VM is provisioned from a template, the build runs, and the VM is terminated.

#### When to Use VMs:
- Security-sensitive builds that cannot share a kernel with other builds
- Testing kernel-level features or operating system behavior
- Running Docker inside your build (Docker-in-Docker has security implications in a multi-tenant environment)

#### The Trade-off:
VMs take 30-60 seconds to provision, compared to 2-5 seconds for containers. This adds significant latency to builds. For most CI workloads, the security benefit is not worth the speed cost.

### Approach 3: Kubernetes Pods
If your infrastructure already runs on Kubernetes, you can run builds as Kubernetes pods. The Pipeline Service creates a Job resource, Kubernetes schedules the pod onto an available node, the build runs, and the pod is deleted.

#### Benefits:
- Kubernetes handles scheduling and resource management
- Easy to scale: just add more nodes to the cluster
- Multi-container pods: run sidecars like database containers alongside your build

#### Trade-offs:
- Adds pod scheduling latency (5-15 seconds)
- Requires Kubernetes expertise to operate
- More complex debugging when things go wrong

### Which Approach Should You Choose?
| Strategy | Startup Time | Isolation | Best For |
| --- | --- | --- | --- |
| Docker | 2-5 seconds | Process-level | Most CI workloads |
| VMs | 30-60 seconds | Kernel-level | Security-sensitive builds |
| Kubernetes | 5-15 seconds | Process-level | Organizations already on K8s |

**For most organizations:** Start with Docker containers. They are fast, well-understood, and provide sufficient isolation. Offer VM-based builds as a premium option for teams that need stronger isolation.

## 6.3 Job Queue Design
The job queue sits between the Pipeline Service and the workers. It is the traffic cop that distributes work, handles priorities, and ensures jobs are not lost if workers crash.
Getting the queue design right matters because it affects how quickly builds start, how reliably they complete, and how fairly resources are shared between teams.

### Priority Handling
Not all builds are equal. A production hotfix must not wait behind 100 feature branch builds. We implement priorities using multiple queues.
Workers check the critical queue first. Only if it is empty do they check high, then normal, then low. This ensures urgent work gets picked up immediately while still making progress on lower priority work.

#### Priority Assignment:
- **Critical:** Manual trigger with "urgent" flag, or builds on release branches
- **High:** Builds on main/master branch
- **Normal:** Feature branch builds triggered by push
- **Low:** Scheduled builds, rebuild requests

### Visibility Timeout and Heartbeats
Here is a tricky scenario: a worker picks up a job and starts processing it. Five minutes later, the worker crashes. What happens to the job?
If we simply removed the job from the queue when the worker took it, the job would be lost. We need a way to recover.
The solution is **visibility timeout**. When a worker takes a job, the job becomes invisible to other workers for a set period (say, 30 minutes). The worker must periodically send heartbeats to extend this timeout. If the worker crashes, it stops sending heartbeats, the timeout expires, and the job becomes visible again for another worker to pick up.

### Dead Letter Queue
Some jobs fail repeatedly. Maybe the build has a bug that causes an infinite loop. Maybe it depends on an external service that is down. After three failures, we stop retrying and move the job to a dead letter queue.
The dead letter queue is a holding area for problem jobs. Operations can investigate: Was it infrastructure? Bad code? A configuration issue? Once fixed, the job can be moved back to the main queue.

### Deduplication
Users sometimes spam the "run build" button, or webhooks can be delivered multiple times. We do not want to run five identical builds for the same commit.
The solution is deduplication. When a job is queued, we generate a deduplication key from (pipeline_id, branch, commit_sha). If a job with the same key was queued in the last 60 seconds, we reject the duplicate and return the existing run_id.

### Choosing a Queue Technology
| Technology | Strengths | Considerations |
| --- | --- | --- |
| Amazon SQS | Managed, scales automatically, visibility timeout built-in | No strict ordering, 256KB message limit |
| RabbitMQ | Priority queues, flexible routing, proven | Requires self-management or a managed service |
| Redis Streams | Very fast, supports consumer groups | Need to handle durability carefully |

**For cloud deployments:** Amazon SQS (or Google Pub/Sub, Azure Service Bus) is the simplest choice. It scales automatically, handles retries, and provides the visibility timeout feature out of the box.
**For on-premise:** RabbitMQ with quorum queues provides good durability and priority support without depending on cloud services.

## 6.4 Deployment Strategies
The "CD" in CI/CD is where things get risky. A bug in the deployment can take down production, affecting real users and real revenue. We need strategies that minimize risk and allow quick recovery when things go wrong.
There are three main approaches, each with different trade-offs between speed, safety, and infrastructure cost.

### Strategy 1: Rolling Deployment
In a rolling deployment, we replace instances one at a time. At any moment during the deployment, some instances run the old version and some run the new version, but the service never goes fully down.

#### How It Works:
1. Start with N instances all running v1
2. Take one instance out of the load balancer rotation
3. Deploy v2 to that instance and run health checks
4. If healthy, add it back to the load balancer
5. Repeat until all instances run v2

#### Why It Works Well:
- Zero downtime: always some instances serving traffic
- Simple: supported natively by Kubernetes, ECS, and most orchestrators
- Resource efficient: no extra infrastructure needed

#### The Trade-offs:
- Rollback is slow: you have to redeploy the old version
- Version mixing: during deployment, some requests hit v1 and some hit v2. If the versions have incompatible APIs, clients might get inconsistent responses

### Strategy 2: Blue-Green Deployment
Blue-green maintains two identical environments. "Blue" runs the current version in production. "Green" sits idle until deployment time, when we deploy the new version to it. Once green is tested and ready, we switch traffic all at once.

#### How It Works:
1. Blue environment serves all production traffic (v1)
2. Deploy v2 to green environment
3. Run smoke tests and integration tests against green
4. Switch the load balancer to route all traffic to green
5. Keep blue running as a hot standby. If something goes wrong, switch back instantly

#### Why It Works Well:
- Instant rollback: flip the load balancer back to blue in seconds
- Full testing: you can run your entire test suite against green before switching
- Clean separation: all traffic goes to one version or the other, no version mixing

#### The Trade-offs:
- Double infrastructure: you need to run two complete environments
- Database migrations are tricky: both blue and green share the same database, so any schema changes must be backwards-compatible

### Strategy 3: Canary Deployment
Canary deployment sends a small percentage of real traffic to the new version. If the new version works well (low error rate, good latency), we gradually increase traffic until it handles everything. If metrics degrade, we immediately pull traffic back.

#### How It Works:
1. Deploy v2 to a small canary pool (5% of capacity)
2. Route 5% of traffic to the canary
3. Monitor error rates, latency, and business metrics
4. If metrics look good after 10-15 minutes, increase to 25%, then 50%, then 100%
5. If metrics degrade, immediately route all traffic back to v1

#### Why It Works Well:
- Real traffic validation: catches issues that synthetic tests miss
- Limited blast radius: if something breaks, only 5% of traffic is affected
- Data-driven decisions: metrics tell you when it is safe to proceed

#### The Trade-offs:
- Requires sophisticated monitoring to detect subtle regressions
- Need traffic splitting capability in your load balancer
- Version mixing: like rolling deployments, both versions serve traffic simultaneously

### Which Strategy Should You Choose?
| Strategy | Rollback Time | Infrastructure Cost | Complexity | Best For |
| --- | --- | --- | --- | --- |
| Rolling | Minutes | 1x | Low | Most services |
| Blue-Green | Seconds | 2x | Medium | Critical services |
| Canary | Seconds | ~1.1x | High | High-traffic services |

**Our recommendation:** Start with rolling deployments. They work well for most services and do not require extra infrastructure. Add canary capability once you have robust monitoring in place. Reserve blue-green for services where even a few minutes of degraded service would be costly.

## 6.5 Handling Build Failures and Retries
Builds fail. A lot. Sometimes it is a legitimate code bug. Sometimes it is a flaky test that passes 9 times out of 10. Sometimes a network timeout causes npm install to fail. Sometimes a worker runs out of disk space.
The key insight is that not all failures are equal. Some should be retried automatically. Some should fail fast and notify the developer. And some should be investigated by operations. Let's design a system that handles each type appropriately.

### Categorizing Failures
The first step is figuring out what kind of failure occurred. We look at the exit code, error messages, and timing to classify failures:
| Category | Examples | What To Do |
| --- | --- | --- |
| Infrastructure | Worker crash, network timeout, disk full, OOM kill | Retry automatically |
| Flaky | Intermittent test failure, rate limited API | Retry with limits |
| Deterministic | Compile error, test assertion failed | Fail immediately |

**Infrastructure failures** are not the developer's fault. The worker ran out of memory, the network hiccuped, or a disk filled up. These should be retried automatically on a fresh worker.
**Flaky failures** are trickier. The code might have a race condition, or it might depend on external services that are occasionally slow. We should retry, but with limits. If something fails 3 times in a row, it is probably not flaky; there is a real problem.
**Deterministic failures** are actual code problems. The code does not compile. A test assertion failed. Retrying will not help; the developer needs to fix the code.

### Retry Strategy
For infrastructure and flaky failures, we use exponential backoff:
The backoff gives transient issues time to resolve. If a network partition caused the failure, waiting 30 seconds might let it heal. If the failure was due to a spike in load, waiting spreads out the retry attempts.

### Detecting Flaky Tests
Flaky tests are a plague on CI systems. They cause developers to ignore failures ("oh, that test is flaky, just re-run it") and waste compute running retries.
We can detect flakiness by tracking test outcomes over time. If a test fails 10% of the time across many runs, it is flaky. The system should:
1. Flag the test as flaky in the UI
2. Allow auto-retry specifically for that test (so developers do not have to re-run the whole suite)
3. Alert the test owner that their test needs to be fixed

### The Decision Flow
When a job fails, the worker reports the failure type. The Pipeline Service decides what to do next:
The dead letter queue catches jobs that keep failing despite retries. Something is systematically wrong, maybe a bad worker image, a misconfigured secret, or a persistent infrastructure issue. Operations needs to investigate.

## 6.6 Scaling the Worker Pool
Remember our back-of-envelope calculation? We need about 1,200 workers at peak, but only 200 at night. Running 1,200 workers 24/7 would waste money. Running 200 workers always would mean long queue times on Monday morning.
We need to scale the worker pool dynamically: add workers when demand increases, remove them when demand drops. The question is how to detect demand changes and react quickly enough.

### Scaling Strategies
There are two complementary approaches: reactive scaling based on current queue depth, and proactive scaling based on known patterns.

#### Queue Depth Scaling (Reactive)
The simplest approach is to watch the job queue. If the queue is growing, add workers. If the queue is empty, remove workers.
The cooldown is important. We do not want to scale down immediately when the queue empties, only to scale back up 30 seconds later when new jobs arrive. A 5-10 minute cooldown smooths out the scaling behavior.

#### Schedule-Based Scaling (Proactive)
Build traffic follows predictable patterns. Monday morning is busy. Friday afternoon is quiet. Weekends are dead. We can pre-scale based on these patterns:
Proactive scaling avoids cold-start delays. If we wait for Monday morning traffic to hit, builds will queue while we scramble to provision workers. Pre-scaling means workers are ready when developers start pushing code.

### The Best of Both Worlds
In practice, you want both approaches working together:
1. **Schedule-based baseline:** Set minimum capacity based on historical patterns
2. **Queue-based elasticity:** Add workers above baseline when queue depth grows
3. **Cost optimization:** Use spot/preemptible instances for the elastic capacity (they are 60-90% cheaper)

The baseline handles predictable load. The elastic layer handles spikes. Spot instances keep the elastic layer affordable.

### Reducing Cold Start Time
When a fresh worker receives its first job, it has to pull the Docker image before it can start the build. For a large image like `node:18` or `python:3.11`, this can take 30 seconds or more. That is a long time for a developer to wait just for the build to start.
The solution is to pre-pull common images onto workers before they receive jobs. We call these "warm" workers.

#### How to Implement Warm Workers:
The Worker Manager tracks which images are used most frequently. When a new worker joins the pool (either a fresh instance or one returning from another job), it pre-pulls the top 10 most common images before accepting jobs.
This trades some worker startup time for faster build startup time. A worker might take an extra 2 minutes to become ready, but every build it runs starts 30 seconds faster. Over the worker's lifetime, that is a significant win.
# References
- [Designing a CI/CD Pipeline](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment) - Atlassian's guide to CI/CD principles
- [GitHub Actions Architecture](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions) - How GitHub implements workflow orchestration
- [Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/) - Running batch jobs in Kubernetes
- [AWS CodePipeline Design](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html) - AWS's approach to pipeline orchestration
- [Martin Fowler on Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html) - Foundational article on CI practices
- [Deployment Strategies](https://thenewstack.io/deployment-strategies/) - Comparison of deployment patterns

# Quiz

## Design CI/CD Pipeline Quiz
In a CI/CD system, what is the primary purpose of the pipeline orchestrator?