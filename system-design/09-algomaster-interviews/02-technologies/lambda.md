# AWS Lambda Deep Dive for System Design Interviews

AWS Lambda is the most widely used serverless compute service. When you need to run code without managing servers, handle variable workloads, or build event-driven architectures, Lambda is often the go-to solution.
But knowing **when** to use Lambda, **how** it scales, and understanding its limitations is what separates good answers from great ones. Many candidates propose Lambda without understanding cold starts, concurrency limits, or when it becomes more expensive than containers.
This chapter covers the practical knowledge you need for interviews: execution model, scaling behavior, cold starts, event sources, pricing trade-offs, and how Lambda compares to alternatives like ECS and Kubernetes.
Whether you are designing an image processing pipeline, a webhook handler, or a real-time data processor, understanding Lambda will help you make better architectural decisions.
# 1. When to Choose Lambda
In interviews, you need to justify your technology choice with specific reasons. Here is when Lambda excels and when it does not.

### 1.1 Choose Lambda When You Have
**Event-driven workloads**: Lambda is designed for responding to events. S3 uploads, API requests, queue messages, database changes, or scheduled tasks all trigger Lambda naturally.
**Variable or unpredictable traffic**: Lambda scales from zero to thousands of concurrent executions automatically. You pay nothing when idle and scale instantly during spikes.
**Short-lived operations**: Tasks that complete in seconds or minutes are ideal. Image resizing, webhook handling, data transformation, and API backends fit well.
**Minimal operational overhead**: No servers to patch, no capacity planning, no scaling configuration. AWS handles all infrastructure management.
**Rapid development cycles**: Deploy new versions in seconds. No container builds, no cluster management, no deployment pipelines for infrastructure.
**Microservices with independent scaling**: Each Lambda function scales independently. High-traffic endpoints scale without affecting others.

### 1.2 Avoid Lambda When You Need
**Long-running processes**: Lambda has a 15-minute maximum execution time. Batch jobs, ML training, or complex data processing may not fit.
**Consistent sub-millisecond latency**: Cold starts add 100ms-10s of latency. For latency-critical applications, warm containers or instances are better.
**High, steady throughput**: At high, consistent request rates, Lambda becomes more expensive than reserved containers or instances.
**Large memory or compute**: Lambda maxes out at 10 GB memory and 6 vCPUs. For memory-intensive or compute-heavy tasks, use EC2 or ECS.
**Stateful applications**: Lambda functions are stateless by design. Long-lived connections, in-memory caches, or local state require different architectures.
**Complex networking requirements**: Lambda in VPC has cold start overhead. Applications needing fine-grained network control may be better on EC2/ECS.
# 2. Lambda Execution Model
Understanding how Lambda executes code is essential for designing reliable systems and answering deep-dive questions.

### 2.1 Execution Environment
Each Lambda function runs in an isolated execution environment (sandbox) with its own resources.
**Components:**
- **Your Code**: The function handler and dependencies
- **Runtime**: Language-specific execution environment (Node.js, Python, Java, Go, etc.)
- **Runtime API**: Interface between Lambda service and your code
- **Extensions**: Optional components for monitoring, security, or governance

### 2.2 Function Lifecycle
**INIT Phase (Cold Start):**
**INVOKE Phase (Warm):**
**SHUTDOWN Phase:**

### 2.3 Handler Structure

### 2.4 Execution Environment Reuse
Lambda reuses execution environments for subsequent invocations. This is crucial for performance.
**What persists between invocations:**
- Variables declared outside the handler
- /tmp directory contents (up to 10 GB)
- Database connections
- SDK clients

**What does NOT persist:**
- Handler function variables
- Request-specific data
- Anything you explicitly clear

**Best practice:**
# 3. Cold Starts and Performance
Cold starts are Lambda's most discussed limitation. Understanding them thoroughly is essential for interviews.

### 3.1 What Causes Cold Starts
**Cold starts happen when:**
- First invocation of a function
- Scaling up (new concurrent executions needed)
- After environment timeout (typically 5-15 minutes of inactivity)
- Code or configuration changes

### 3.2 Cold Start Duration by Runtime
| Runtime | Typical Cold Start | Notes |
| --- | --- | --- |
| Python | 100-300ms | Fast initialization |
| Node.js | 100-300ms | Fast initialization |
| Go | 50-150ms | Compiled binary, fastest |
| Java | 500ms-10s+ | JVM startup, class loading |
| .NET | 200-500ms | CLR initialization |
| Ruby | 200-400ms | Interpreter startup |
| Custom Runtime | Varies | Depends on implementation |

### 3.3 Factors Affecting Cold Start Duration

### 3.4 Cold Start Optimization Strategies
**Strategy 1: Minimize Package Size**
**Strategy 2: Increase Memory**
**Strategy 3: Lazy Initialization**
**Strategy 4: Provisioned Concurrency**
**Strategy 5: Keep Functions Warm (Anti-pattern)**

### 3.5 VPC Cold Starts
Lambda functions in a VPC have additional cold start overhead.
# 4. Concurrency and Scaling
Understanding Lambda's scaling behavior is critical for designing systems that handle load correctly.

### 4.1 Concurrency Model
**Key concept:** Each concurrent execution requires its own execution environment. One environment processes one request at a time.

### 4.2 Scaling Behavior

### 4.3 Concurrency Limits

### 4.4 Reserved Concurrency
Guarantee a portion of account concurrency for a specific function.
**Use reserved concurrency to:**
- Protect critical functions from noisy neighbors
- Limit function concurrency (throttle at N)
- Prevent runaway costs from scaling issues

### 4.5 Provisioned Concurrency
Pre-warm execution environments to eliminate cold starts.

### 4.6 Concurrency Best Practices
| Scenario | Recommendation |
| --- | --- |
| Critical API | Reserved + Provisioned concurrency |
| Database-connected | Reserved = Max DB connections |
| Batch processing | No reservation, use full account capacity |
| Cost-sensitive | No provisioned, accept cold starts |
| Latency-sensitive | Provisioned concurrency |
| Multi-function account | Reserve for critical, pool the rest |

# 5. Event Sources and Triggers
Lambda integrates with numerous AWS services. Understanding these integrations is essential for designing event-driven systems.

### 5.1 Invocation Models
| Model | How It Works | Retry Behavior | Use Case |
| --- | --- | --- | --- |
| Synchronous | Caller waits for response | Caller handles retry | API Gateway, SDK |
| Asynchronous | Fire and forget | Lambda retries twice | S3, SNS, EventBridge |
| Poll-based | Lambda polls source | Source-dependent | SQS, Kinesis, DynamoDB |

### 5.2 Common Event Sources
**API Gateway (Synchronous)**
**S3 (Asynchronous)**
**SQS (Poll-based)**
**DynamoDB Streams (Poll-based)**
**Kinesis (Poll-based)**

### 5.3 Event Source Mappings
For poll-based sources, Lambda manages the polling through event source mappings.

### 5.4 Scaling by Event Source
| Source | Scaling Behavior |
| --- | --- |
| API Gateway | 1 execution per request |
| SQS (Standard) | Up to 1,000 batches concurrently |
| SQS (FIFO) | 1 batch per message group |
| Kinesis | 1 execution per shard (or more with parallelization) |
| DynamoDB Streams | 1 execution per shard |
| S3 | 1 execution per event (can spike) |
| SNS | 1 execution per message |

**Interview tip:** When designing event-driven systems, explain how the event source affects Lambda scaling. SQS Standard scales aggressively, while FIFO and Kinesis scale by partition/shard.
# 6. Lambda with Other AWS Services
Lambda integrates deeply with AWS services. Understanding these patterns is valuable for interviews.

### 6.1 API Gateway + Lambda
The most common pattern for building serverless APIs.

### 6.2 S3 + Lambda Pipeline
Event-driven file processing.

### 6.3 SNS + Lambda Fan-out
Broadcast events to multiple Lambdas.

### 6.4 Step Functions + Lambda
Orchestrate complex workflows with state machines.

### 6.5 EventBridge + Lambda
Event-driven architecture with filtering and routing.

### 6.6 Common Integration Patterns
| Pattern | Components | Use Case |
| --- | --- | --- |
| Serverless API | API GW + Lambda + DynamoDB | REST/GraphQL APIs |
| File Processing | S3 + Lambda | Image/video processing |
| Event Fan-out | SNS + Lambda[] | Broadcast events |
| Queue Processing | SQS + Lambda | Async task processing |
| Stream Processing | Kinesis + Lambda | Real-time analytics |
| Workflow Orchestration | Step Functions + Lambda | Multi-step processes |
| Scheduled Jobs | EventBridge + Lambda | Cron jobs |
| Change Data Capture | DynamoDB Streams + Lambda | Replication, triggers |

# 7. Cost Optimization
Lambda pricing can be counterintuitive. Understanding costs is essential for interview discussions about trade-offs.

### 7.1 Pricing Model

### 7.2 Cost Calculation Examples

### 7.3 Lambda vs EC2/ECS Cost Comparison

### 7.4 Cost Optimization Strategies
**Strategy 1: Right-size Memory**
**Strategy 2: Minimize Cold Starts**
**Strategy 3: Efficient Code**
**Strategy 4: Use Graviton2 (ARM)**

### 7.5 Cost Monitoring
# 8. Lambda vs Other Compute Options
Interviewers often ask you to compare Lambda with alternatives. Understanding trade-offs is essential.

### 8.1 Lambda vs EC2
| Aspect | Lambda | EC2 |
| --- | --- | --- |
| Scaling | Automatic (ms) | Manual or Auto Scaling (minutes) |
| Pricing | Pay per invocation | Pay per hour |
| Cold start | Yes (100ms-10s) | No (always running) |
| Max runtime | 15 minutes | Unlimited |
| Max memory | 10 GB | Terabytes |
| Control | Limited | Full OS access |
| Maintenance | None | Patches, updates, security |
| Best for | Event-driven, variable load | Steady load, long-running |

### 8.2 Lambda vs ECS/Fargate
| Aspect | Lambda | ECS/Fargate |
| --- | --- | --- |
| Unit | Function | Container |
| Scaling granularity | Per request | Per task |
| Min running | 0 | 0 (Fargate) |
| Cold start | 100ms-10s | 30s-2min |
| Max runtime | 15 minutes | Unlimited |
| Networking | Limited VPC | Full VPC control |
| Cost model | Per invocation | Per second running |
| Best for | Short tasks, events | Long-running, steady |

### 8.3 Lambda vs Kubernetes
| Aspect | Lambda | Kubernetes |
| --- | --- | --- |
| Management | Fully managed | Self-managed or EKS |
| Learning curve | Low | High |
| Portability | AWS only | Multi-cloud |
| Scaling | Automatic | Configurable |
| Cost (low traffic) | Very low | Higher (cluster overhead) |
| Cost (high traffic) | Can be higher | More predictable |
| Ecosystem | AWS services | Kubernetes ecosystem |

### 8.4 Lambda vs App Runner
| Aspect | Lambda | App Runner |
| --- | --- | --- |
| Trigger | Events, HTTP | HTTP only |
| Scaling | Per request | Per container |
| Cold start | Per function | Per container |
| Runtime | 15 minutes | Unlimited |
| Pricing | Per request | Per vCPU-hour + requests |
| Best for | Event-driven | Web apps, APIs |

### 8.5 Decision Matrix
| Use Case | Recommended | Why |
| --- | --- | --- |
| API with variable traffic | Lambda | Scales to zero, pay per use |
| API with steady high traffic | ECS/Fargate | More cost-effective |
| Image processing | Lambda | Event-driven, parallel |
| Real-time streaming | Lambda + Kinesis | Per-shard processing |
| Long-running batch | ECS Batch | No time limit |
| ML inference (latency-critical) | ECS + GPU | Consistent latency |
| Microservices (portable) | Kubernetes | Multi-cloud, ecosystem |
| Quick prototype | Lambda | Fast to deploy |

### 8.6 Hybrid Approaches
# Summary
AWS Lambda is ideal for event-driven architectures with variable workloads. Here are the key takeaways for interviews:
1. **Know when to use Lambda.** Event-driven workloads, variable traffic, short-duration tasks, and when operational simplicity matters. Not for steady high throughput, long-running processes, or ultra-low latency requirements.
2. **Understand cold starts.** Know the factors (runtime, package size, VPC, memory) and mitigation strategies (provisioned concurrency, optimization, architectural choices).
3. **Master the concurrency model.** Understand burst limits, scaling behavior, reserved vs provisioned concurrency, and how to protect downstream systems.
4. **Know event source behaviors.** Synchronous (API Gateway), asynchronous (S3, SNS), and poll-based (SQS, Kinesis) have different scaling and retry characteristics.
5. **Integrate with AWS services.** Lambda's power comes from integration. Know patterns: API Gateway APIs, S3 processing, SQS queuing, Step Functions orchestration.
6. **Understand cost trade-offs.** Lambda is cost-effective for variable load but can be expensive at high steady throughput. Know the crossover point with containers.
7. **Compare with alternatives.** EC2 for full control, ECS/Fargate for containers, Kubernetes for portability. Lambda for serverless event processing.
8. **Handle errors properly.** Use DLQs or destinations, partial batch failure reporting, and appropriate retry strategies for each invocation type.

When proposing Lambda in an interview, emphasize the operational benefits while acknowledging limitations. Show awareness of cold starts and your mitigation strategy. Demonstrate cost awareness by explaining when Lambda makes sense versus when containers might be better.
# References
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/) - Official AWS documentation covering all Lambda features
- [AWS Lambda FAQs](https://aws.amazon.com/lambda/faqs/) - Common questions about Lambda capabilities and limits
- [AWS re:Invent 2023: Best Practices for Serverless](https://www.youtube.com/results?search_query=aws+reinvent+2023+lambda) - Deep-dive presentations from AWS experts
- [Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning) - Open-source tool for optimizing Lambda memory
- [AWS Well-Architected Serverless Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/) - Best practices for serverless applications
- [The Serverless Handbook](https://serverlesshandbook.dev/) - Practical guide to building serverless applications

# Quiz

## AWS Lambda Quiz
Which workload is generally the best fit for AWS Lambda?