# Design Google Docs

## What is Google Docs?

Google Docs is a cloud-based word processing application that allows users to create, edit, and share documents online. Unlike traditional editors, it enables real-time collaboration where multiple users can work on the same document simultaneously.
Every change is saved automatically, and users can see edits, comments, and suggestions from others in near real time.
To design a system like Google Docs, we must solve several complex challenges like:
- Real-time editing with low latency
- Consistent document state across multiple users
- Conflict resolution when edits overlap
- Efficiently storing the documents
- Version history support
- and fine-grained access control

And all of this needs to scale to **millions of users** and **thousands of concurrent document edits** without sacrificing performance.
In this article, we will explore the **high-level architecture**, **low-level details, **and the **database and API design** of a real-time collaborative editing system that supports all these features.
Let’s begin by clarifying the requirements.
# 1. Requirement Gathering
Before diving into the architecture, let's summarize the core functional and non-functional requirements:

## 1.1 Functional Requirements
- **Create & Retrieve Documents:** Users should be able to create new documents and retrieve them instantly.
- **Collaborative Editing:** Multiple users should be able to edit the same document simultaneously, and view each other’s changes in real-time.
- **Rich Text Formatting:** The system should support full document structure and formatting including headings, bold/italic text, lists, hyperlinks, etc.
- **Live Cursors & Presence: **Users should be able to see the cursor positions and presence of others.
- **Offline Access and Sync:** Users should be able to edit documents offline (e.g. without internet), and the system should automatically sync changes once they reconnect.
- **Access Control and Sharing:** Users should be able to share documents with specific permissions (view-only, comment, or edit).

## 1.2 Non-Functional Requirements
- **Real-Time Collaboration: **Edits should be reflected to all participants within milliseconds**.**
- **Scalability:** The system should handle millions of users, and thousands of documents being edited concurrently.
- **Version History:** The system should keep a history of changes for each document, allowing users to view or revert to earlier versions.
- **Data Consistency:** Despite concurrent edits, all users should eventually see the same final document state.

# 2. Capacity Estimation

### Users and Documents
- **Monthly Active Users (MAU)**: 100 million
- **Daily Active Users (DAU)**: ~50 million
- **Peak Concurrent Users**: ~1 million
- **Average Documents per User**: 20
- **Total Documents**: `100M users × 20 docs = 2 billion documents`

### Document Characteristics
- **Average Document Size**: 100 KB (structured text with formatting, comments, metadata)
- **Total Document Storage**: `2B docs × 100 KB = ~200 TB (Terabytes)`
- **Version History Storage**: Assume 50 versions per document, and each version is a delta of ~1 KB: `2B docs × 50 × 1 KB = ~100 TB`

### Real-Time Edits
- **Active Collaborative Sessions at Peak**: ~100K
- **Keystrokes per User per Minute**: 100
- **Total Keystrokes/sec at Peak**: `100K × 100 / 60 = ~167K operations/sec`

Each of these keystrokes is typically sent as a separate operation to the server and then broadcast to all other collaborators on the same document.
# 3. High-Level Architecture
The architecture can be broken into several key components, as illustrated below:

### 3.1 Clients (Web, Mobile, Desktop)
Users access the system using a client that:
- Captures **user input** (like typing, formatting, or comments)
- Applies **incoming updates** from other collaborators
- Queues changes locally** **when offline and syncs on reconnection
- Maintains a **WebSocket connection** with the server to push/receive live updates

### 3.2 WebSocket Server
To support **real-time, bi-directional, low-latency communication** between the client and the server, we use WebSockets.
When a user opens a document:
- The client establishes a persistent WebSocket connection with a WebSocket server.
- As the user types, each **edit operation is instantly** sent to the WebSocket server.
- The WebSocket server **forwards incoming operations** to a **message queue** for further processing.
- It receives updates from the Collaboration service and forwards it to other users editing the same document.

Each WebSocket server node handles multiple connections and can be **horizontally scaled**. To simplify broadcasting, all users editing the same document are usually connected to the **same server instance**.

### 3.3 Message Queue
To decouple real-time input from backend processing, the system uses a **message queue** (e.g., Kafka or Google Cloud Pub/Sub).
When a WebSocket server receives an operation, it **forwards it to the queue.**
The queue **buffers and orders** operations reliably. This allows backend services to process edits at their own pace, even during traffic spikes.

### 3.4 Collaboration Service
This is the **brain** of real-time editing. The collaboration service consumes operations from the message queue and:
- **Orders and processes** them
- Applies **conflict resolution** using an algorithm like **Operational Transformation (OT)** or **CRDT**
- Updates the **document metadata and content data stores**
- Appends operations to a **version history log store**
- Sends the **transformed changes** back to the WebSocket server for broadcasting

To ensure **sequential consistency**, updates to the same document goes to the same collaboration server.

### 3.5 Caching Layer
To ensure low-latency access and reduce load on backend databases, we can use caching for active documents and metadata.
- Frequently accessed documents are served from in-memory cache rather than hitting the database.
- Incoming operations are applied to the cached document first, enabling quick real-time updates.
- Active user session metadata is stored in a cache to support real-time features like live cursors and presence indicators.

A system like **Redis** or local in-memory stores on server nodes can serve this purpose.

### 3.6 Persistent Storage
The system stores three main types of data:
1. **Metadata Database**
2. **Document Content Store**
3. **Operation / Version History Store**

### Flow of a Single Edit
**1. User Types a Character: **As soon as the user types a character, the client captures the action and generates an **edit operation**, such as:
**2. Client Sends Operation via WebSocket: **The operation is immediately sent to the backend using an established **WebSocket connection**, along with metadata such as the current document version and user ID.
**3. WebSocket Server Forwards to Message Queue: **The WebSocket server receives the message and forwards it to a **message queue**. This decouples ingestion from processing and enables horizontal scaling.
**4. Collaboration Service Processes the Operation: **A dedicated collaboration server **consumes the operation** from the queue, transforms it (if needed, using OT or CRDT), and applies it to the **document state** stored in:
- In-memory cache (for low-latency access)
- Persistent storage (for durability and version history)

**5. Changes Broadcast Back to WebSocket Server: **Once the operation is processed, the collaboration service **notifies the WebSocket server**, which **broadcasts the updated operation** to all other connected clients working on the same document.
**6. Clients Apply the Update: **Each client receives the transformed operation and applies it to its local document view. This ensures that every user sees the change **almost instantly**, preserving consistency across all sessions.
> This loop repeats for every keystroke, deletion, or formatting change, ensuring everyone sees the same thing almost instantly.

# 4. Database Design
A system like Google Docs manages multiple types of data, each with distinct structures, access patterns, and consistency requirements.
To ensure performance and scalability, it’s critical to use the right **data model** and **storage engine** for each use case.

## 4.1 User & Document Metadata
These tables manage structured, relational data that benefits from ACID guarantees.
**Recommended Database: Relational Database (e.g., PostgreSQL, MySQL)**

### Schema
- `users:`** **Stores basic user details like email, name etc..
- `documents:`** **Stores document-level metadata such as title, owner, timestamps, and current version.
- `document_permissions:`** **Defines which users have what level of access to a document.

## 4.2 Document Content
Document content is **not stored as plain text**. Instead, it’s stored in a **structured, tree-like format**.
This allows the document to be:
- Rendered consistently
- Modified at any level (not just line-by-line)
- Patched efficiently (only change a node, not the entire doc)
- Collaborative-friendly (works with OT or CRDTs)

A common approach is to represent the document as a **hierarchical JSON object**. Each node represents a block (like paragraph or heading) or inline content (like text with bold/italic).

### Recommended Database: Document Store (e.g., MongoDB)
Document stores are ideal for this use case because:
- The entire document or a subtree can be retrieved as a single object
- JSON-like documents map directly to the internal structure
- Updates to nested fields are supported
- Schema-less storage allows flexible evolution of structure

#### Schema:
- `document_id (bigint): `Unique identifier for the document
- `content_blob (json): `Hierarchical representation of the document
- `last_saved_at (timestamp): `When the document was last persisted
- `current_version (int): `Current version number

#### Example
Suppose the user types:
It might be represented as:
Formatting such as bold, italic, or hyperlinks is represented using a `marks` array on inline nodes:
Non-text content like images, videos, and tables can be stored as structured nodes:

## 4.3 Version History and Snapshots
Every change made to a document is recorded as an operation (e.g., insert, delete, format). These operations are stored in an **append-only, time-ordered **structure to support:
- Real-time synchronization
- Undo and redo functionality
- Version history browsing
- Conflict resolution (OT/CRDT-based merging)
- Rollback and recovery

Over time, heavily edited or long-lived documents can accumulate **thousands or even millions of operations**. To ensure performance, we must combine two complementary mechanisms:
1. **Operation Log**: Fine-grained deltas that power real-time editing
2. **Snapshots**: Full document state stored periodically for fast recovery and replay

### 1. Operation Log (Version History)
The **operation log** tracks every edit as an immutable delta. It allows clients and servers to:
- Replay document history
- Transform concurrent operations in real-time
- Restore previous versions with precision

#### Recommended Database: Wide-Column Store (e.g., Cassandra)
Wide-column stores are ideal because they:
- Are optimized for time-series and append-only writes
- Scale horizontally to billions of rows
- Allow efficient querying by key ranges (e.g., all ops for a given document)

**Schema: **`document_versions`
- `document_id (bigint): `Unique identifier for the document
- `version_number (int): `Version number for the edit
- `operation (json): `Structured OT/CRDT-compatible delt
- `created_at (timestamp): `When the operation occurred
- `created_by (bigint): `Who performed the edit

**Partition key**: `document_id`**Clustering key**: `version_number` (ensures in-order replay within a document)
> This schema supports fast range scans: e.g., fetch operations from version 1050 to 1100.

### 2. Snapshots
While the operation log allows precise replay, reconstructing a document from version 0 can become expensive over time. To mitigate this, the system periodically takes **snapshots**: full copies of the document at specific versions.
Snapshots allow the system to:
- Start from a recent baseline instead of version 0
- Reconstruct documents quickly
- Speed up version restoration and rollback

#### Snapshot Frequency
Snapshots can be created:
- **After N operations** (e.g., every 100 ops)
- **On a timer** (e.g., every 5 minutes)
- **When log size exceeds a threshold** (e.g., 1MB of diffs)

The goal is to balance **storage cost** with **reconstruction speed**.

#### Snapshot Schema: document_snapshots
- `snapshot_id:` Unique ID for the snapshot
- `document_id:` Document the snapshot belongs to
- `version_number:` Corresponds to the version at snapshot time
- `content_blob:` Full structured representation of the document
- `created_at:` When the snapshot was taken

#### Storage Options for Snapshots
1. **Document Store** (e.g., MongoDB, Firestore)
2. **Blob Storage** (e.g., S3, GCS)

> Hybrid Strategy: Keep recent snapshots in a fast-access store (e.g., MongoDB). Move older snapshots to long-term blob storage.

#### Example Flow: Version Reconstruction
User wants to view version **1050**:
1. System loads latest snapshot ≤ 1050 (e.g., version 1000)
2. Loads operations from version 1001 to 1050 from `document_versions` in Cassandra
3. Applies those operations to snapshot state to rebuild version 1050

> This hybrid model ensures fast, memory-efficient replay, and scales to documents with years of editing history.

## 4.4 Real-Time Collaboration State
In a system like Google Docs, where multiple users are editing a document simultaneously, the server must maintain **transient state** about each participant’s session to enable real-time features like:
- Live cursors
- User presence indicators
- Viewport awareness (e.g., “User X is viewing section Y”)

This transient state is session-specific and changes rapidly, so it doesn’t need to be persisted to disk. Instead, it should be stored in a **fast, in-memory data store** that supports low-latency reads/writes and automatic expiration.

### Recommended Store: In-Memory Database (e.g., Redis)
Each collaboration session (user + document) is tracked using a unique key pattern:
**Key**: `session:{session_id}`
(Where `session_id` could be a hash of `document_id:user_id`)
**Fields:**
- `document_id (bigint): `The document being edited
- `user_id (bigint): `The active user in the session
- `started_at (timestamp): `When the session was initiated
- `last_activity (timestamp): `Timestamp of the most recent interaction
- `cursor_position (json): `Logical and visual location of the user’s cursor
- `view_port (json): `Scroll position, visible section, zoom level, etc.
- `role (enum): `Viewer, Commenter, Editor
- `device_info (json): `Optional: Browser type, platform, device resolution

#### Example Record in Redis

#### TTL: Expiry for Inactivity
Each session record is set with a **TTL (Time-To-Live)**, often around 1–5 minutes.
- If `last_activity` is not updated within this period, Redis will evict the record.
- On reconnect or resumed activity, the session is recreated.

This reduces memory usage and avoids stale presence data.

### Example Flow: Live Cursors
1. When a user moves their cursor or selects text: The client captures the new `cursor_position`
2. The client sends a cursor update message:
3. The WebSocket server:
- Validates the session
- Updates the user's `cursor_position` in Redis (key: `session:{doc_id}:{user_id}`)
- Broadcasts the update to other clients connected to `doc_123`:

# 5. API Design
To support document creation, editing and sharing, lets define a set of well-structured RESTful APIs.

### 5.1 Create Document

#### POST /documents

##### Request Body:

##### Response:

### 5.2 Get Document Metadata

#### GET /documents/{documentId}

##### Response:

### 5.3 Get Document Content

#### GET /documents/{document_id}/content

##### Response:

### 5.4 Delete Document

#### DELETE /documents/{documentId}

### 5.5 Share Document with User

#### POST /documents/{documentId}/share
Share Document with a User

##### Request Body:

### 5.6 Get Sharing Settings

#### POST /documents/{documentId}/permissions

##### Response:

### 5.7 Get Version History

#### GET /documents/{document_id}/versions

##### Response:

### 5.8 Real-Time Collaboration API (WebSocket)

#### wss://docs.example.com/collaborate

##### Message: Send User Operation

##### Server Broadcast Message (to other users):
# 6. Design Deep Dive

## 6.1 Real-Time Collaborative Editing and Conflict Resolution
One of the biggest challenges in Google Docs’ design is enabling **real-time collaboration**.
Imagine three users editing the same document simultaneously:
- one is typing a sentence
- another is deleting a paragraph
- and a third is reordering bullet points

*How do we ensure that everyone sees a consistent and correct version of the document without anyone’s changes being lost, overwritten, or applied incorrectly?*

### Challenges in Concurrent Editing
When multiple users edit a shared document at the same time, several issues arise:
- **Out-of-order operations**: Edits may reach the server in a different order than they were made.
- **Divergent document states**: Each client may have a slightly different local view of the document at any given moment.
- **Conflicting changes**: Two users might insert or delete text in the same location, or edit the same sentence at once.

Without a proper conflict resolution strategy, these overlapping operations would lead to inconsistencies, lost data, or corrupted document states.
To solve this, lets explore two popular algorithms:
- **Operational Transformation (OT)**
- **Conflict-Free Replicated Data Type (CRDT)**

### Operational Transformation (OT)
**Operational Transformation** is an algorithmic technique that enables multiple users to concurrently modify a shared document without conflicts or overwriting each other’s work.
**The core idea is simple:**
When edits arrive at different times or in different orders, we **transform each operation against others** to preserve all user intents while maintaining a consistent final document state.
Let’s walk through how OT handles concurrent editing using a real-world scenario.

#### Step 1: Operation Generation
When a user makes an edit (e.g., types a character, deletes text, changes formatting), the client creates a structured **operation**.
**Example: **If the user types the letter **A** at position 5:
`Insert("A", position=5)`
This operation is tagged with the **document version** the client last saw (e.g., revision 12).
The client:
- **Applies the operation locally** immediately for responsiveness (called local echo)
- **Sends the operation** to the server for global coordination

This means the user sees their change instantly, even before the server responds.

#### Step 2: Queuing and Ordering at the Server
The server receives operations from multiple clients, often simultaneously.
However:
- The **order of arrival** may differ from the **order of creation**
- Operations may be based on **different document revisions**

The server must:
- Assign a **global revision number** (or use a consistent timestamp-based ordering strategy)
- Identify which operations are **concurrent** (i.e., based on the same version)
- Queue these operations for transformation and resolution

#### Step 3: Transformation
This is where the real magic happens.
The server **transforms each incoming operation** against previously applied operations to ensure that all edits are preserved and applied consistently.
> If two operations conflict (e.g., both insert at the same position), the server transforms the second operation to account for the first, preserving the intent of both.

**Example: **Let’s say the document is initially: `"BC"`
Two users edit concurrently:
- **Sam** inserts `"A"` at position `0` → `Insert('A', pos=0)`
- **Aditi** inserts `"D"` at position `2` → `Insert('D', pos=2)`

**Scenario 1: Sam’s operation arrives first**
- The document becomes `"ABC"`
- Aditi’s insert at position 2 now needs adjustment: since one character ("A") was inserted before position 2, we **shift her operation** to position 3.
- Transformed: `Insert("D", pos=3)`
- Final document: `"ABCD"`

**Scenario 2: Aditi’s operation arrives first**
- The document becomes `"BCD"`
- Sam’s insert at position 0 still works without adjustment.
- Final document: `"ABCD"`

In both cases, the result is the same.
This is the power of OT. It ensures that all operations are **adjusted relative to one another**, maintaining document consistency without explicit locking.

#### Step 4: Broadcast and Acknowledgment
Once an operation is transformed and applied:
- It is **broadcast to all other clients**
- It is **acknowledged** to the original sender
- Clients **transform incoming operations** against their own unacknowledged local operations to maintain consistency

This ensures:
- Every user eventually sees the same content
- Each user’s **cursor and selection position remain stable**
- Edits happen **fluidly and predictably**, even during high concurrency

#### Conflict Resolution Rules
OT includes a set of transformation rules to handle overlapping or conflicting edits
A common strategy is: “**whoever’s operation arrived first on the server gets priority**”
In other cases, the system may **interweave the changes**, or apply a **last-writer-wins** approach.
**Examples:**
- **Two users insert at the same position: **The system may give priority to the operation that arrived first, or use user ID or timestamp as a tie-breaker.
- **One user inserts, another deletes at overlapping positions: **The delete may be adjusted to avoid removing the newly inserted content.
- **Both replace the same word: **The system might choose one, merge both changes, or apply a deterministic rule.

#### Local OT and Client-Side Echo
To reduce perceived latency and ensure a fast typing experience, OT is also implemented on the **client side**.
Each client maintains:
- The **latest acknowledged revision** from the server
- A **queue of unacknowledged local operations**
- A **queue of unsent local operations**

When a new operation arrives from the server, the client:
1. **Transforms it** against any unacknowledged local edits
2. **Applies it** to the local document
3. Updates the **cursor** or selection accordingly

> This local OT loop ensures your typing feels instant even as the server processes dozens of concurrent edits.

#### Why Not Locking or Merging?
Locking the document (or a section of it) when someone edits would prevent concurrency and break the collaborative experience.
Similarly, using merge algorithms like in Git would interrupt the flow with conflict dialogs.
OT avoids both. It allows **concurrent editing without locking or manual merges**, making real-time collaboration feel natural and reliable.
In the world of real-time collaboration, **Operational Transformation (OT)** isn’t the only game in town. A newer and increasingly popular alternative is **Conflict-Free Replicated Data Types (CRDTs)**.

### Conflict-Free Replicated Data Types (CRDTs)
**CRDTs** are a powerful alternative to **Operational Transformation (OT)** for building real-time collaborative systems.
Unlike OT, which requires a central server to order and transform operations, CRDTs are designed for **decentralized, eventually consistent systems** where edits can happen offline, out of order, and across disconnected peers.
CRDTs are specially designed data structures with the following core properties:
- **Local-first edits: **Users can apply changes without waiting for a server
- **Commutative and idempotent: **Operations can be applied in any order and still yield the same result
- **Mergeable without conflict: **All replicas eventually converge to the same final state, automatically
- **Offline-ready: **CRDTs support full document editing even when disconnected from the network

They are ideal for environments where users may be offline, disconnected, or distributed across a peer-to-peer network.

#### How CRDTs Works (High-Level)
Each user maintains a **local copy** of the document and performs edits directly.
These edits are:
1. **Assigned a globally unique identifier**
2. **Tagged with causal dependencies**
3. **Stored in a grow-only structure**
4. **Synchronized opportunistically**

#### Example: Concurrent Inserts
Assume the document initially contains `"BC"`.
- **User A** inserts `"A"` at position 0
- **User B** inserts `"D"` at position 2

Each insert is represented as:
- `Insert("A", after: null, id: (userA, 1001))`
- `Insert("D", after: "C", id: (userB, 1005))`

Both clients apply their own edit locally, so:
- A’s document becomes `"ABC"`
- B’s document becomes `"BCD"`

When they synchronize, the CRDT uses **reference-based ordering** and **deterministic sorting** (e.g., timestamp + user ID) to merge both inserts.
Both clients arrive at the same final document: `"ABCD"`
No conflicts. No server needed. No lock required.

#### Trade-Offs and Challenges with CRDTs
While CRDTs eliminate the need for centralized coordination, they introduce their own set of complexities and trade-offs:
1. **Metadata Overhead: **Each character might carry unique identifiers, vector clocks, and tombstone flags. In large documents, this can significantly increase the size of the data structure.
2. **Deletes Are Logical (Not Physical): **In many CRDT implementations, deleting a character does not remove it, it merely marks it as *tombstoned*. Over time, the document may grow larger than the visible content unless garbage collection is applied.
3. **Network Overhead: **In a peer-to-peer setting, every user must sync with every other user, leading to **O(N²)** message complexity. While this is manageable for small groups, it becomes impractical for massive-scale collaboration.
4. **Complex Garbage Collection: **Removing tombstoned content and cleaning up old metadata without compromising consistency is difficult and still an active area of research.

#### Why Google Docs Chooses OT over CRDTs
Google Docs continues to use OT for several practical reasons:
- Google’s infrastructure makes **centralized coordination** efficient and reliable.
- OT offers **strong consistency**, which aligns with user expectations. Everyone sees the same thing instantly.
- The memory and bandwidth overhead of CRDTs is unnecessary when edits can be funneled through a central server.
- Collaboration in Google Docs typically happens in **small groups** (2–10 users), where OT performs exceptionally well.
- Google can afford the **server-side compute** needed for transformation logic.

#### When CRDTs Shine
CRDTs are particularly well-suited for:
- **Offline-first applications**, where users expect to work without connectivity for long periods
- **Decentralized systems**, where no single source of truth exists
- **Peer-to-peer collaboration**, like local-first apps or distributed whiteboards
- Tools like **Figma**, which use CRDT-like data models optimized for graphical content and position-based structures

### Additional Note: Differential Synchronization
An earlier approach explored by Google was **Differential Synchronization**, introduced by Neil Fraser. This algorithm continuously syncs documents by diffing entire text states and sending deltas.
While conceptually simple, diff-based approaches struggle with real-time precision and conflict management, which is why OT and CRDTs have largely replaced it in modern editors.

## 6.2 Supporting Version History
The **Version History** feature in Google Docs allows users to browse previous versions of a document, see who made changes and when, and restore any earlier version as the current one.
Let’s break down how this functionality works end to end.

### 1. Displaying the Version History Panel
When a user clicks on "Version History," the system needs to retrieve a list of document versions with meaningful metadata for each version.
From the `document_versions` table, the system loads:
- Version number (logical revision ID)
- Author (user ID or display name)
- Timestamp (when the edit occurred)
- Optional: short summary (e.g., “Added conclusion”, if user added a version label)

**Example UI list:**

### 2. Viewing a Past Version
When a user selects a version from the history list, the system must reconstruct and render the document **as it looked at that exact point in time**.

#### Step 1: Identify the Nearest Snapshot
Search for the most recent **snapshot** (e.g., full copy of the document) **before or at** the target version.
If the user selects version 87, and a snapshot exists at version 80, we use that snapshot as a base.

#### Step 2: Replay Operations (Deltas)
From version 80 to 87, replay all operations in order: Insertions, Deletions, Format changes, Comments and annotations (if applicable)
Each delta is applied **in the same order** it was originally executed, ensuring document reconstruction is **lossless and accurate**.

#### Step 3: Render in Read-Only or Diff Mode
Once the full version is reconstructed:
- The system renders it in **read-only mode** (to prevent unintended edits)
- Optionally, it renders a **“diff view”** to highlight what changed from the previous version, similar to Git diffs

### 3. Restoring a Past Version
In a collaborative editing system, restoring a previous version of a document isn’t a simple rewind. Instead, it must be **treated as a new operation** to ensure:
- **Auditability**: The action appears in version history and can itself be undone or rolled back.
- **Consistency**: All clients see the change as part of the shared editing stream.
- **Continuity**: Real-time collaboration is preserved, without breaking session state or discarding concurrent edits.

Rather than rolling back the entire document history, the system **applies the restored version as a new edit**, producing a new version of the document.

#### Step 1: Reconstruct the Target Version
When a user selects a previous version (e.g., version 52):
- The system loads the **nearest snapshot ≤ 52**
- It replays the operations from that snapshot up to version 52
- The result is a **fully reconstructed document state**, represented in the same structured format used by the editor (e.g., ProseMirror or Slate-style JSON)

#### Step 2: Generate a "Replace All" Operation
Instead of overwriting state internally, the system creates a **new operation** representing the restoration:
This operation is:
- Applied just like any other operation
- Logged in the **operation log** for version 88
- Compatible with OT/CRDT engines (usually treated as a full content diff)

#### Step 3: Log and Broadcast
Once the "replace_all" operation is applied:
- It is **persisted** in the `document_versions` log
- It is **broadcast** to all active collaborators through the WebSocket server
- Each connected client:

This approach ensures transparency: if someone restores an older version, others are not silently reverted—they see it as a real-time update.

## 6.3 Offline Access and Synchronization
One of the standout features of Google Docs is the ability to work offline. Users can continue editing documents without an internet connection, and all changes are automatically synchronized once they reconnect.

### How Offline Editing Works
When a user opens a document while online, the system leverages browser technologies like **IndexedDB** and **Service Workers** to enable offline functionality.
- **Document content** and metadata are cached in **IndexedDB**
- **User session state** (e.g., cursor, scroll position) is stored locally
- A **Service Worker** is registered to:

### Editing While Offline
When the user goes offline:
- The editor loads the cached document state
- The user can freely **edit, format, and interact** with the document
- Each change is:

#### Example:
Suppose Alice loses connectivity and performs the following actions:
1. Insert `"Hello"` at position 0
2. Delete 3 characters at position 10
3. Apply bold formatting from position 5 to 15

The client queues the operations:
These operations are applied locally and instantly, giving the user a smooth, single-player editing experience.

### Reconnecting and Synchronization
When Alice reconnects:
1. The client re-establishes the WebSocket connection
2. Pulls the latest document state and server version
3. Transforms queued offline operations against any new edits made by others
4. Pushes the transformed operations to the server
5. The server:
6. The client receives and applies missed operations from others

This ensures that all changes, local and remote, are **applied in the correct order**, and all collaborators eventually converge on the same document state.

### Conflict Resolution
Offline edits may overlap with concurrent online edits. For example:
- Alice deletes a sentence that Bob formatted
- Carol inserts a heading in the same place Alice added a paragraph

These are resolved using the **same strategy as live editing**:
- **OT-based systems**: Transform offline edits against server-side updates
- **CRDT-based systems**: Merge all operations deterministically using timestamps and causal history

#### Result:
- All user edits are preserved
- The final document remains logically consistent
- Clients converge to the same document state without manual intervention

### Sync Strategy: Push-Pull Model
Synchronization generally follows a **push-pull** pattern when a user reconnects:
- **Pull**: Fetch the latest server revision and any missed operations
- **Push**: Send locally queued edits, along with their base revision

The server:
- Resolves ordering conflicts
- Applies all changes
- Sends acknowledgments and deltas to update the client

This model ensures **eventual consistency**, even if users edited the document while disconnected, at different times, or from different devices.
# Quiz

## Design Google Docs Quiz
Why is a persistent bi-directional connection typically used for Google Docs style collaboration?