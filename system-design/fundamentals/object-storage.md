# Object Storage

**Reference:** [AlgoMaster - Object Storage](https://algomaster.io/learn/system-design/object-storage)

## Problem / Concept Overview

Object storage stores data as objects (files + metadata) in a flat namespace, unlike hierarchical file systems. It's designed for unstructured data at scale—images, videos, documents, backups.

## Key Ideas

### Object Storage vs File Storage vs Block Storage

| Feature | Object Storage | File Storage | Block Storage |
|---------|---------------|--------------|---------------|
| Structure | Flat namespace | Hierarchical | Raw blocks |
| Access | REST API | File system | Block device |
| Use Case | Unstructured data | Shared files | Databases |
| Scalability | Highly scalable | Limited | Limited |
| Metadata | Rich metadata | Basic | None |

### Object Components

1. **Data:** The actual file content
2. **Metadata:** Key-value pairs (size, type, created date, custom tags)
3. **Unique Identifier:** Globally unique key (URL or UUID)

```
Object = {
  key: "user-123/profile-photo.jpg",
  data: <binary>,
  metadata: {
    size: 2MB,
    type: "image/jpeg",
    created: "2024-01-01",
    owner: "user-123"
  }
}
```

## Why It Matters

**Scalability:** Handles petabytes of data across distributed systems.

**Durability:** Replicated across multiple locations, 99.999999999% (11 9's) durability.

**Cost:** Cheaper than block storage for large-scale data.

**Accessibility:** REST API access from anywhere, any platform.

**Metadata:** Rich metadata enables intelligent data management.

## Real-World Examples

**AWS S3:** Industry standard, stores trillions of objects.

**Google Cloud Storage:** Multi-region, integrated with GCP services.

**Azure Blob Storage:** Integrated with Azure services, tiered storage.

**Dropbox:** Uses object storage for file synchronization.

**Netflix:** Stores video content in object storage.

## Architecture Pattern

```
┌─────────┐
│ Client  │
└────┬────┘
     │ HTTP/REST
     ▼
┌──────────────┐
│ Object Store │
│  (S3-like)   │
└──────┬───────┘
       │
   ┌───┴───┬────┬────┐
   │       │    │    │
   ▼       ▼    ▼    ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Obj1│ │Obj2│ │Obj3│ │Obj4│
└────┘ └────┘ └────┘ └────┘
```

## Key Features

### 1. Flat Namespace
- No directories/folders
- Keys are just strings: `user-123/photos/image.jpg`
- Simpler than hierarchical systems

### 2. REST API
```
PUT    /bucket/object-key    # Upload
GET    /bucket/object-key    # Download
DELETE /bucket/object-key    # Delete
HEAD   /bucket/object-key    # Metadata
```

### 3. Versioning
- Keep multiple versions of objects
- Enable point-in-time recovery
- Useful for compliance

### 4. Lifecycle Policies
- Automatically move objects to cheaper storage
- Delete old objects
- Example: Move to Glacier after 90 days

### 5. Access Control
- Bucket-level policies
- Object-level ACLs
- Signed URLs for temporary access

## Storage Classes/Tiers

### Hot Storage
- Frequently accessed data
- Low latency, higher cost
- Example: Active user content

### Cold Storage
- Infrequently accessed
- Lower cost, higher latency
- Example: Archives, backups

### Glacier/Archive
- Rarely accessed
- Lowest cost, retrieval time (minutes to hours)
- Example: Compliance archives

## Tradeoffs

### Advantages
- ✅ Highly scalable (petabytes)
- ✅ Durable (11 9's)
- ✅ Cost-effective at scale
- ✅ REST API access
- ✅ Rich metadata

### Disadvantages
- ❌ Not for databases (no transactions)
- ❌ Higher latency than block storage
- ❌ Eventual consistency (some systems)
- ❌ Not suitable for frequently updated files

## Use Cases

### 1. Static Website Hosting
- Store HTML, CSS, JS files
- Serve via CDN
- Cost-effective

### 2. Media Storage
- Images, videos, audio files
- Serve to users globally
- Example: Instagram photos

### 3. Backup & Archive
- Long-term data retention
- Compliance requirements
- Disaster recovery

### 4. Data Lakes
- Store raw data for analytics
- Various formats (JSON, Parquet, CSV)
- Process with big data tools

### 5. Content Distribution
- Store content, serve via CDN
- Global distribution
- Low latency

## Design Considerations

### Naming Conventions
- Use prefixes for organization: `users/{id}/photos/`
- Include timestamps: `logs/2024/01/01/app.log`
- Avoid special characters

### Metadata Strategy
- Store frequently queried data in metadata
- Use tags for filtering/searching
- Don't store in object name (use metadata)

### Access Patterns
- **Read-heavy:** Use CDN in front
- **Write-heavy:** Consider batching/uploads
- **Update-heavy:** Object storage not ideal (use database)

### Cost Optimization
- Use appropriate storage class
- Enable lifecycle policies
- Compress before storing
- Delete unused objects

## Performance Optimization

1. **Multipart Upload:** For large files (>5GB)
2. **Parallel Downloads:** Download chunks in parallel
3. **CDN Integration:** Cache frequently accessed objects
4. **Compression:** Compress before upload
5. **Request Batching:** Batch operations when possible

## Security

1. **Encryption:** Encrypt at rest and in transit
2. **Access Control:** IAM policies, bucket policies
3. **Signed URLs:** Temporary access tokens
4. **VPC Endpoints:** Private access from VPC
5. **Audit Logging:** Track all access

## Common Patterns

### 1. Upload Flow
```
Client → API Server → Generate signed URL → Client uploads directly
```
- Reduces server load
- Faster uploads

### 2. CDN Integration
```
Client → CDN → Object Storage (cache miss)
```
- Low latency
- Reduced storage costs

### 3. Event-Driven Processing
```
Upload → Trigger Lambda → Process → Store result
```
- Automatic processing
- Serverless architecture

## Interview Tips

When discussing object storage:
1. Identify use case (static files, media, backups)
2. Choose appropriate storage class
3. Design access patterns (CDN, direct access)
4. Discuss lifecycle policies
5. Address security (encryption, access control)

## Comparison with Alternatives

**vs File Storage (NFS):**
- Object storage: REST API, better scalability
- File storage: POSIX interface, lower latency

**vs Block Storage:**
- Object storage: Higher-level abstraction, metadata
- Block storage: Lower-level, better for databases

**vs Database:**
- Object storage: Large files, unstructured data
- Database: Structured data, transactions, queries

