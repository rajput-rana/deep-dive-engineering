# Design Calendar System

## What is a Calendar System?

A calendar system allows users to schedule, organize, and manage events and appointments across time. It provides features like creating events, setting reminders, handling recurring schedules, and sharing calendars with others.
The core functionality seems simple: store events with start and end times. However, the complexity emerges when handling recurring events, time zones, conflict detection, and real-time collaboration across multiple users.
**Popular Examples:** Google Calendar, Microsoft Outlook Calendar, Apple Calendar
This system design problem tests several important skills: complex data modeling for recurring events, time-based queries that span different time zones, conflict detection algorithms, and real-time synchronization across multiple users.
In this chapter, we will explore the **high-level design of a calendar system**.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
Before jumping into architecture diagrams, we need to understand what exactly we are building. 
Calendar systems can vary significantly in scope. Are we building a personal calendar app, or a collaborative enterprise tool? Do we need to handle recurring events, or just one-off appointments? These questions shape our entire design.
Let's walk through how this requirements discussion might unfold in an interview:
**Candidate:** "What is the expected scale? How many users and events should the system support?"
**Interviewer:** "Let's design for 100 million users, with an average of 10 events per user per week."
**Candidate:** "Should we support recurring events like daily standups or weekly meetings?"
**Interviewer:** "Yes, recurring events are a core feature. Users should be able to create daily, weekly, monthly, and yearly recurring events with end dates or occurrence limits."
**Candidate:** "Do we need to support calendar sharing and collaboration?"
**Interviewer:** "Yes. Users should be able to share calendars with others and invite attendees to events."
**Candidate:** "Should the system send reminders and notifications?"
**Interviewer:** "Yes. Users should receive reminders before events via email or push notifications."
**Candidate:** "How should we handle time zones? Users might travel or schedule events with people in different zones."
**Interviewer:** "Events should be stored in UTC and displayed in the user's local time zone. Support scheduling across time zones."
**Candidate:** "Do we need to detect scheduling conflicts?"
**Interviewer:** "Yes. The system should warn users about overlapping events and help find available time slots."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core features our system must support:
- **Create/Update/Delete Events:** Users can create events with title, description, location, start time, end time, and attendees.
- **Recurring Events:** Support daily, weekly, monthly, and yearly recurring events.
- **Calendar Sharing:** Users can share their calendars with others and set permissions (view-only or edit).
- **Event Invitations:** Users can invite others to events and track RSVP responses.
- **Reminders:** Send notifications before events via email or push notifications.
- **Conflict Detection:** Warn users about overlapping events and suggest available slots.

## 1.2 Non-Functional Requirements
Beyond features, we need to think about the qualities that make the system production-ready:
- **High Availability:** The system must be highly available (99.99% uptime).
- **Low Latency:** Calendar views and event queries should return within 200ms.
- **Scalability:** Handle 100 million users with billions of events.
- **Consistency:** Event changes should be visible to all attendees within seconds.
- **Data Durability:** Events must never be lost once created.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our architectural decisions, particularly around storage, caching, and how we handle recurring events.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:

#### Write Traffic (Event Creation)
With 100 million users creating an average of 10 events per week, we can calculate the daily volume:
Converting to queries per second:
Traffic patterns are rarely uniform. Monday mornings and the start of business hours see spikes as people schedule their week. Assuming a 3x peak factor:

#### Read Traffic (Calendar Views)
Users check their calendars frequently throughout the day, opening the day view, week view, or month view. Let's assume each user performs about 5 calendar views per day on average:
The read-to-write ratio is roughly 3.5:1. This is less extreme than systems like Pastebin (10:1) but still indicates we should optimize for read performance.

### 2.2 Storage Estimates
Each event needs to store several pieces of information. Let's break down the storage per event:
| Component | Size | Notes |
| --- | --- | --- |
| Event ID | ~16 bytes | UUID |
| Calendar ID, Creator ID | ~32 bytes | Foreign key references |
| Title | ~100 bytes | Typically short |
| Description | ~500 bytes | Optional, varies widely |
| Start/End times | ~16 bytes | Timestamps |
| Location | ~100 bytes | Often empty or short |
| Attendees list | ~200 bytes | Average 5 attendees |
| Recurrence rule | ~50 bytes | RRULE string if recurring |
| Other metadata | ~100 bytes | Status, reminders, etc. |

**Total: approximately 1 KB per event**
Now let's project storage growth:
| Time Period | Total Events | Storage Required |
| --- | --- | --- |
| 1 Day | 143 million | ~143 GB |
| 1 Month | 4.3 billion | ~4.3 TB |
| 1 Year | 52 billion | ~52 TB |
| 5 Years | 260 billion | ~260 TB |

### 2.3 The Recurring Events Problem
Here is where calendar storage gets tricky. Consider a simple daily standup meeting that repeats every weekday for a year. If we stored each occurrence as a separate row, that single recurring event would create 260 rows (52 weeks × 5 days).
Let's do the math on recurring event expansion:
This highlights a critical design decision: we should not materialize all recurring instances upfront. A single recurring event definition should generate instances dynamically when queried, not be pre-expanded into hundreds of database rows.

### 2.4 Key Insights from These Numbers
These estimates reveal several important design implications:
1. **Moderate QPS, not extreme:** Peak read traffic of 17,500 QPS is significant but manageable with proper caching. We are not at Twitter or Google scale here.
2. **Storage is substantial but not extreme:** 52 TB per year is large but well within the capabilities of modern distributed databases.
3. **Recurring events need special handling:** Materializing all instances would explode our storage requirements by 5-10x. We need a smarter approach.
4. **Caching helps significantly:** Calendar views are highly cacheable. Most users check the same week repeatedly. A good caching strategy can reduce database load dramatically.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Calendar systems have more API surface area than something like Pastebin because we are dealing with multiple related entities: calendars, events, attendees, and shares. Let's focus on the most important endpoints.

### 3.1 Create Event

#### Endpoint: POST /events
This is how users add events to their calendars. The request needs to specify which calendar to add the event to, along with the event details.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| calendar_id | string | Yes | The calendar to add the event to |
| title | string | Yes | Event title (e.g., "Team Standup") |
| start_time | datetime | Yes | Start time in ISO 8601 format with timezone |
| end_time | datetime | Yes | End time in ISO 8601 format with timezone |
| description | string | No | Detailed description or agenda |
| location | string | No | Physical address or video call link |
| attendees | array | No | List of email addresses to invite |
| recurrence | string | No | Recurrence rule in RRULE format |
| reminders | array | No | List of reminder offsets (e.g., ["10m", "1h"]) |
| timezone | string | No | IANA timezone (e.g., "America/New_York") |

#### Example Request:

#### Success Response (201 Created):
For recurring events, we return a `recurrence_id` that groups all instances together. This becomes important when updating or deleting recurring events.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Malformed datetime, end before start, invalid RRULE |
| 401 Unauthorized | Not authenticated | Missing or invalid auth token |
| 403 Forbidden | No permission | User cannot add events to this calendar |
| 409 Conflict | Scheduling conflict | Overlaps with existing event (if strict mode enabled) |

### 3.2 Get Events

#### Endpoint: GET /calendars/{calendar_id}/events
This is the workhorse endpoint. Every time a user opens their calendar app and views a day, week, or month, this endpoint gets called. It needs to be fast.

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| start_date | date | Yes | Beginning of the query range |
| end_date | date | Yes | End of the query range |
| expand_recurring | boolean | No | Whether to expand recurring events into instances (default: true) |
| timezone | string | No | Display timezone for returned events |

#### Example Request:

#### Success Response (200 OK):
Notice that recurring events are expanded into individual instances, each with their specific date. The `is_recurring` flag and `recurrence_id` let the client know this event is part of a series.

### 3.3 Update Event

#### Endpoint: PUT /events/{event_id}
Updating events is where things get interesting, especially for recurring events. If a user changes the time of a weekly meeting, do they mean just this week, or all future occurrences?

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| update_scope | enum | No | For recurring events: this_event, this_and_following, or all_events |

The `update_scope` parameter is critical for recurring events:
- **this_event:** Only modify this specific instance. Creates an exception.
- **this_and_following:** Modify this and all future instances. Splits the series.
- **all_events:** Modify the entire recurring series, past and future.

**Example:** User wants to move just this Monday's standup from 9 AM to 10 AM:
This creates an exception: the recurring pattern still says 9 AM, but this specific instance has been overridden to 10 AM.

### 3.4 Delete Event

#### Endpoint: DELETE /events/{event_id}
Similar to updates, deletions on recurring events need scope control.

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| delete_scope | enum | No | For recurring events: this_event, this_and_following, or all_events |
| notify_attendees | boolean | No | Send cancellation emails (default: true) |

Deleting `this_event` on a recurring series adds the date to an exceptions list. The recurring pattern continues, but that specific date is skipped.

### 3.5 Share Calendar

#### Endpoint: POST /calendars/{calendar_id}/share
Allows calendar owners to share access with others.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| email | string | Yes | Email of the user to share with |
| permission | enum | Yes | view (read-only) or edit (full access) |

#### Success Response (200 OK):
The invitee receives a notification and can accept or decline the share. Once accepted, the shared calendar appears in their calendar list.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible solution and adding components as we encounter new requirements. This mirrors how you would approach the problem in an interview.
Our system needs to handle four main concerns:
1. **Event Management:** The core CRUD operations for creating, reading, updating, and deleting events.
2. **Recurring Events:** Efficiently handle events that repeat on a schedule without exploding storage.
3. **Notifications:** Send reminders before events occur through various channels.
4. **Calendar Sharing:** Allow users to collaborate by sharing calendars and inviting attendees.

Let's visualize how these concerns map to our read and write paths:
The write path is straightforward: requests flow through the API Gateway to the Calendar Service, which persists data and potentially schedules reminders. The read path includes caching because calendar views are highly repetitive. Most users check the same week multiple times per day, so caching provides significant performance benefits.
Let's build this architecture step by step.


The foundation of any calendar system is the ability to manage events. This is the starting point for our design.

### Components for Event Management
Let's introduce the components we need to make this work.

### API Gateway
Every request enters through the API Gateway. Think of it as the front door to our system, handling concerns that are common across all requests.
The gateway authenticates users (typically via JWT tokens), validates that requests are well-formed, enforces rate limits to prevent abuse, and routes requests to the appropriate backend service. By handling these cross-cutting concerns at the edge, we keep our application services focused on business logic.

### Calendar Service
This is the brain of our operation for event management. It orchestrates the entire workflow: validating input, storing events, expanding recurring event patterns for display, and checking for scheduling conflicts.
We want this service to be stateless so we can run multiple instances behind a load balancer. All persistent state lives in the database and cache, making horizontal scaling straightforward.

### Event Database
Stores all event data. Given our query patterns (range queries by time for calendar views, point lookups by event ID for updates), we need a database that handles both efficiently. We will discuss the database choice in detail in the next section, but PostgreSQL is a good fit here.

### Flow: Creating an Event
Let's walk through this step by step:
1. **Request arrives at API Gateway:** The client sends a POST request with event details. The gateway authenticates the user and performs basic request validation.
2. **Calendar Service takes over:** Once validated, the request moves to the Calendar Service. It performs business-level validation: Are the times valid? Does the end time come after the start time? Does the user have permission to add events to this calendar?
3. **Time handling:** If the client sent local times with a timezone, the service stores both the local time and the timezone. This is important for recurring events and DST handling, which we will discuss in the deep dive section.
4. **Persistence:** The service generates a unique event ID and stores the event in the database. If this is a recurring event, it also stores the recurrence pattern.
5. **Response:** The created event is returned to the client, including the generated event_id that can be used for future updates or deletions.

### Flow: Fetching Events for a Date Range
This is the more interesting flow because it involves caching and recurring event expansion.
Let's trace through the different scenarios:

#### Best case: Cache hit
The Calendar Service first checks Redis for cached calendar data. The cache key includes the calendar ID and date range. If found, we can return immediately without touching the database. This should be the common case for users who check their calendar repeatedly throughout the day.

#### Cache miss: Full database query
When the cache does not have the data, we need to query the database. This involves two types of events:
1. **Single events:** Query for events where start_time falls within the requested range.
2. **Recurring events:** Query for recurring event patterns that could have instances in the range. A weekly meeting that started six months ago still needs to appear in this week's view.

The tricky part is recurring event expansion. We take each recurring event pattern and compute which instances fall within the requested date range. This computation happens in memory, not in the database. The results are merged with single events and sorted by start time.
Before returning, we populate the cache with the results so subsequent requests for the same range are fast.


    S5 --> QueueKafka
```mermaid
graph TB
    subgraph Clients
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Load Balancing
        LB[Load Balancer]
    end

    subgraph Application Services
        S1[Managed Service]
        S2[push Service]
        S3[Sharing Service]
        S4[This Service]
        S5[the Service]
    end

    subgraph Data Storage
        DBPostgreSQL[PostgreSQL]
        DBDynamoDB[DynamoDB]
        DBCassandra[Cassandra]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
        QueueRabbitMQ[RabbitMQ]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBPostgreSQL
    S1 --> DBDynamoDB
    S1 --> CacheRedis
    S1 --> QueueKafka
    S1 --> QueueRabbitMQ
    S2 --> DBPostgreSQL
    S2 --> DBDynamoDB
    S2 --> CacheRedis
    S2 --> QueueKafka
    S2 --> QueueRabbitMQ
    S3 --> DBPostgreSQL
    S3 --> DBDynamoDB
    S3 --> CacheRedis
    S3 --> QueueKafka
    S3 --> QueueRabbitMQ
    S4 --> DBPostgreSQL
    S4 --> DBDynamoDB
    S4 --> CacheRedis
    S4 --> QueueKafka
    S4 --> QueueRabbitMQ
    S5 --> DBPostgreSQL
    S5 --> DBDynamoDB
    S5 --> CacheRedis
    S5 --> QueueKafka
    S5 --> QueueRabbitMQ



## 4.2 Notifications and Reminders
Users need to be reminded of upcoming events. Missing a meeting because you forgot about it is frustrating, so reminders are a core feature of any calendar system.
This requires a dedicated system that tracks reminder times and delivers notifications at exactly the right moment.

### Additional Components for Reminders
We need three new components to handle the notification workflow.

#### Reminder Service
This service is responsible for scheduling and triggering reminders at the right time. When an event is created with reminders, the Calendar Service tells the Reminder Service about it. The Reminder Service then watches the clock and fires off notification jobs when reminder times arrive.
The challenge here is scale. With millions of users and multiple reminders per event, we might have billions of reminder timestamps to track. The Reminder Service needs an efficient way to find reminders that are due soon without scanning the entire dataset.

#### Message Queue
We use a message queue (like Kafka or RabbitMQ) to decouple reminder triggering from notification delivery. When a reminder comes due, the Reminder Service publishes a message to the queue. The Notification Service consumes these messages and handles delivery.
Why not send notifications directly? Two reasons: reliability and rate limiting. If the notification fails (email server down, push service unavailable), the message stays in the queue for retry. And if a million reminders come due at 9 AM on Monday, the queue buffers them so we do not overwhelm the notification providers.

#### Notification Service
This service handles the actual delivery of notifications through various channels: push notifications to mobile devices, emails, and potentially SMS. It also tracks delivery status, which is useful for debugging and analytics.

### Flow: Scheduling and Sending Reminders
Let's walk through this flow:
1. **Event creation triggers reminder scheduling:** When the Calendar Service creates an event with reminders (like "10 minutes before" and "1 hour before"), it calculates the actual trigger times and sends them to the Reminder Service.
2. **Reminder storage:** The Reminder Service stores each reminder with its trigger timestamp. These are typically stored in a database with an index on trigger_time for efficient querying.
3. **Polling for due reminders:** A background job runs every minute (or more frequently for high precision) to find reminders where `trigger_time <= now`. These are the reminders that need to fire.
4. **Publishing to the queue:** Due reminders are published to the message queue. Each message contains enough information to send the notification: user ID, event details, notification preferences.
5. **Delivery:** The Notification Service consumes messages and delivers through the appropriate channel. If delivery fails, the message can be retried.

The key insight here is that we separate "when should this reminder fire?" (Reminder Service) from "how do we deliver this reminder?" (Notification Service). This separation makes each service simpler and more focused.

## 4.3 Calendar Sharing and Invitations
Calendars are not just personal tools. In most organizations, collaboration is essential. Team members need visibility into each other's schedules to find meeting times, managers need to see their team's availability, and assistants often manage calendars for executives.
This requires two related features: sharing entire calendars with others, and inviting specific people to individual events.

### Additional Components for Sharing

#### Sharing Service
This service manages calendar permissions and access control. It answers questions like: "Can Alice view Bob's calendar?" and "Does Carol have permission to edit this event?"
The Sharing Service stores permission records (who can access what, with which permission level) and validates access for every calendar operation. When you share a calendar or invite someone to an event, this service handles the workflow: storing the permission, sending notifications to the invitee, and tracking their response.

### Flow: Sharing a Calendar
When a user wants to share their calendar with a colleague, here is what happens:
1. **Share request:** The calendar owner sends a request to share their calendar, specifying the recipient's email and permission level (view or edit).
2. **Permission storage:** The Sharing Service stores the permission record. At this point, the share is "pending" until the invitee accepts.
3. **Invitation notification:** An email is sent to the invitee explaining that someone wants to share a calendar with them. The email includes a link to accept or decline.
4. **Invitee response:** When the invitee accepts, the share status changes to "active." The shared calendar now appears in their calendar list.
5. **Access enforcement:** From now on, whenever the invitee requests events from this calendar, the Sharing Service validates that they still have permission before serving the data.

Event invitations work similarly, but at the individual event level rather than the entire calendar.

## 4.4 Putting It All Together
Now that we have designed each component, let's step back and see the complete architecture. We have also added a Load Balancer in front of the API Gateway for distributing traffic across multiple instances.
The architecture follows a layered approach, with each layer having a specific responsibility:
**Client Layer:** Users interact with our system through web browsers, mobile apps, or API clients. From our perspective, they all look the same, just HTTP requests.
**Gateway Layer:** The Load Balancer distributes traffic across multiple API Gateway instances. The gateway handles authentication, rate limiting, and request validation before passing requests to the application layer.
**Application Layer:** Four stateless services handle the business logic. They are stateless, meaning any instance can handle any request, which makes horizontal scaling straightforward.
**Data Layer:** PostgreSQL stores our data with proper indexing. Redis provides caching for frequently accessed calendar views.
**Background Services:** The Reminder Service runs in the background, watching for due reminders and publishing them to the message queue.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| Load Balancer | Traffic distribution | Managed service (auto-scales) |
| API Gateway | Auth, rate limiting, routing | Horizontal (add instances) |
| Calendar Service | Event CRUD, recurring expansion | Horizontal (stateless) |
| Reminder Service | Track and trigger reminders | Horizontal with partitioning |
| Sharing Service | Permissions and invitations | Horizontal (stateless) |
| Notification Service | Deliver notifications | Horizontal (stateless) |
| PostgreSQL | Event storage | Read replicas, then sharding |
| Redis Cache | Calendar view caching | Redis Cluster |
| Message Queue | Buffer reminder jobs | Kafka/RabbitMQ cluster |

# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Choosing the right database and designing an efficient schema are critical decisions that affect performance, scalability, and how we handle tricky features like recurring events.

## 5.1 SQL vs NoSQL
The database choice is not always obvious. Let's think through our access patterns and requirements to make an informed decision.

#### What we need to store:
- Millions of events with various attributes
- Recurring event patterns and exceptions
- Calendar sharing permissions
- Attendee responses and RSVP status

#### How we access the data:
- Range queries by time are the primary pattern (get events between Jan 15 and Jan 22)
- Point lookups by event ID for updates and deletions
- Queries involving multiple tables (events with attendees, shared calendars)
- Complex queries for conflict detection

#### Consistency requirements:
- When someone updates an event, all attendees should see the change quickly
- Double-booking prevention requires checking for conflicts atomically

Given these requirements, a relational database like **PostgreSQL** is a good fit:
**Why not NoSQL?** Systems like DynamoDB or Cassandra excel at simple key-value lookups with extreme scale. But our query patterns involve range queries, joins across tables, and transactions that span multiple records. These are exactly the scenarios where relational databases shine.
For caching, we use **Redis** to store computed calendar views. When a user views a week, we cache the result so subsequent views of the same week are instant.

## 5.2 Database Schema
With our database choice made, let's design the schema. Calendar systems have several interconnected entities: users, calendars, events, recurring patterns, attendees, and sharing permissions. Let's walk through each table.

### Users Table
This is straightforward, storing basic account information.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | Unique identifier for the user |
| email | VARCHAR | User's email address (unique) |
| name | VARCHAR | User's display name |
| timezone | VARCHAR | User's default timezone (e.g., "America/New_York") |
| created_at | TIMESTAMP | Account creation time |

The `timezone` field is important. When a user creates an event, we need to know their default timezone to interpret times correctly.

### Calendars Table
Users can have multiple calendars. Most people have at least two: Work and Personal. Some have more for specific projects, family schedules, or shared team calendars.
| Field | Type | Description |
| --- | --- | --- |
| calendar_id | UUID (PK) | Unique identifier for the calendar |
| owner_id | UUID (FK) | User who owns this calendar |
| name | VARCHAR | Calendar name (e.g., "Work", "Personal") |
| color | VARCHAR | Display color for events (#hex format) |
| is_primary | BOOLEAN | Whether this is the user's primary calendar |
| created_at | TIMESTAMP | Calendar creation time |

When a user creates an event without specifying a calendar, it goes to their primary calendar. The color helps visually distinguish events from different calendars when viewing them together.

### Events Table
This is the heart of our schema. Each row represents either a single event or a modified instance of a recurring event.
| Field | Type | Description |
| --- | --- | --- |
| event_id | UUID (PK) | Unique identifier for the event |
| calendar_id | UUID (FK) | Calendar containing this event |
| creator_id | UUID (FK) | User who created the event |
| title | VARCHAR | Event title |
| description | TEXT | Event description (optional) |
| location | VARCHAR | Event location (optional) |
| start_time | TIMESTAMP | Start time (stored in UTC) |
| end_time | TIMESTAMP | End time (stored in UTC) |
| timezone | VARCHAR | Original timezone for recurring events |
| is_all_day | BOOLEAN | Whether this is an all-day event |
| recurrence_id | UUID (FK) | Reference to recurring event pattern (null for single events) |
| original_start | TIMESTAMP | For modified instances, the original occurrence time |
| status | ENUM | 'confirmed', 'tentative', 'cancelled' |
| created_at | TIMESTAMP | Event creation time |
| updated_at | TIMESTAMP | Last modification time |

A few fields need explanation:
- **timezone:** For recurring events, we store the original timezone so that "9 AM every Monday" stays at 9 AM local time even when daylight saving time changes. More on this in the deep dive section.
- **recurrence_id:** Links to the recurring pattern. If null, this is a single event. If set, this event is either the master event or an exception instance.
- **original_start:** When a user modifies a single instance of a recurring event (like moving this week's standup to 10 AM instead of 9 AM), we create a new event row with `original_start` set to when that instance would have occurred. This lets us know which instance was modified.

**Indexes:**

### Recurring Events Table
This table stores the pattern definition, not the individual instances. One row represents "every Monday at 9 AM" regardless of how many Mondays that covers.
| Field | Type | Description |
| --- | --- | --- |
| recurrence_id | UUID (PK) | Unique identifier for the recurrence pattern |
| event_id | UUID (FK) | Reference to the master event (the first instance) |
| rrule | VARCHAR | Recurrence rule in RRULE format |
| dtstart | TIMESTAMP | Start date of the recurrence |
| until | TIMESTAMP | End date of the recurrence (if specified) |
| count | INTEGER | Number of occurrences (if specified instead of until) |
| exceptions | JSONB | List of exception dates (cancelled/modified instances) |

The `exceptions` field is a JSONB array containing dates that should be skipped when expanding the pattern. When a user deletes or modifies a single instance, we add its date to this list rather than creating a "deleted" event row.

### Attendees Table
This table links users to events they are invited to. Each row represents one attendee on one event.
| Field | Type | Description |
| --- | --- | --- |
| attendee_id | UUID (PK) | Unique identifier |
| event_id | UUID (FK) | Event the user is invited to |
| user_id | UUID (FK) | Invited user (null for external guests) |
| email | VARCHAR | Attendee email (for external invites) |
| response_status | ENUM | 'accepted', 'declined', 'tentative', 'needs_action' |
| is_organizer | BOOLEAN | Whether this attendee is the organizer |

We have both `user_id` and `email` because attendees might be external. If you invite  who does not have an account, we still need to track their invitation. The `response_status` starts as 'needs_action' when the invite is sent and updates based on their RSVP.

### Calendar Shares Table
Stores permissions for shared calendars. This is separate from event attendees, as sharing a calendar gives access to all events, not just one.
| Field | Type | Description |
| --- | --- | --- |
| share_id | UUID (PK) | Unique identifier |
| calendar_id | UUID (FK) | Shared calendar |
| user_id | UUID (FK) | User the calendar is shared with |
| permission | ENUM | 'view', 'edit' |
| status | ENUM | 'pending', 'accepted', 'declined' |
| created_at | TIMESTAMP | When the share was created |

The `permission` field determines what the sharee can do. With 'view' permission, they can see events but not modify them. With 'edit' permission, they can create, update, and delete events on the shared calendar.

### Reminders Table
Stores reminder settings and tracks which reminders have been sent.
| Field | Type | Description |
| --- | --- | --- |
| reminder_id | UUID (PK) | Unique identifier |
| event_id | UUID (FK) | Event this reminder is for |
| user_id | UUID (FK) | User to remind |
| trigger_time | TIMESTAMP | When to send the reminder |
| method | ENUM | 'email', 'push', 'both' |
| sent | BOOLEAN | Whether the reminder has been sent |

**Index:**
This partial index only includes unsent reminders, keeping the index small and fast even as we accumulate millions of sent reminders over time.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts of our design: handling recurring events without exploding storage, managing time zones correctly, detecting scheduling conflicts, and scaling the reminder system.

## 6.1 Handling Recurring Events
Recurring events are arguably the most challenging aspect of calendar system design. On the surface, it seems simple: store a pattern like "every Monday at 9 AM" and generate instances. But the complexity emerges when you think through all the edge cases.
What happens when a user modifies just one instance of a recurring meeting? What if they delete this week's occurrence but want to keep all the others? What if they change the time of "this and all future" occurrences? How do you handle a daily meeting that started two years ago when someone queries for this week's events?

### The Challenge
Let's do some math to understand why naive approaches fail. Consider a daily standup meeting that runs indefinitely:
Now multiply that by the number of users with recurring events:
This explosion in storage is one problem. The other is updates: if someone changes their weekly team meeting from 2 PM to 3 PM, you might need to update hundreds of rows across future instances.

### Approach 1: Store All Instances (Materialization)
Pre-generate all recurring event instances as separate database rows.

#### How It Works
When a user creates a recurring event, the system immediately generates individual event records for each occurrence up to a limit (e.g., 2 years ahead).

#### Pros
- **Simple queries:** Fetching events for a date range is straightforward.
- **Easy conflict detection:** All instances exist as regular events.
- **Simple single-instance modifications:** Changing one occurrence is just an update.

#### Cons
- **Storage explosion:** A daily event for 2 years creates 730 rows per event.
- **Update complexity:** Changing "all future events" requires updating many rows.
- **Cleanup overhead:** Need background jobs to generate future instances and clean old ones.

### Approach 2: Store Pattern Only (Virtual Expansion)
Store only the recurrence pattern and expand instances at query time.

#### How It Works
1. Store a single event with an RRULE (recurrence rule) like `FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR`.
2. When fetching events for a date range, compute which instances fall within that range.
3. Return the computed instances along with regular single events.

#### The RRULE Standard
The iCalendar RRULE format is the industry standard for defining recurrence patterns:
The following diagram shows how virtual expansion works at query time:

#### Pros
- **Storage efficient:** One row per recurring event regardless of occurrences.
- **Easy pattern updates:** Changing "all events" updates one row.
- **No cleanup needed:** No materialized instances to manage.

#### Cons
- **Complex queries:** Must compute instances for every query.
- **Conflict detection complexity:** Need to expand events to check conflicts.
- **Exception handling:** Modified/deleted instances require special tracking.

### Approach 3: Hybrid (Recommended)
Combine both approaches for optimal performance.

#### How It Works
1. **Store the pattern:** Keep the RRULE in the recurring_events table.
2. **Materialize a window:** Pre-generate instances for the next 3-6 months.
3. **Store exceptions:** Save modified or cancelled instances explicitly.
4. **Expand on demand:** Compute instances beyond the materialization window at query time.

#### Handling Exceptions
When a user modifies a single instance of a recurring event:
1. Store the modified instance in the events table with `original_start` set to the original occurrence time.
2. Add the original time to the `exceptions` list in the recurring_events table.
3. When expanding, skip dates in the exceptions list and include the modified instances.

**Example:**
- Recurring event: Daily standup at 9 AM
- User changes Thursday's standup to 10 AM
- Exception added: `2025-01-16T09:00:00Z`
- New event stored: Thursday standup at 10 AM with `original_start = 2025-01-16T09:00:00Z`

The following diagram illustrates how exception handling works in the hybrid approach:

### Summary and Recommendation
| Strategy | Pros | Cons | Best For |
| --- | --- | --- | --- |
| Full Materialization | Simple queries, easy modifications | Storage heavy, update complexity | Small-scale systems |
| Virtual Expansion | Storage efficient | Complex queries, slow for large ranges | Read-heavy, few modifications |
| Hybrid | Balanced storage and query performance | Implementation complexity | Production calendar systems |

The following diagram visually compares the three approaches:
**Recommendation:** Use the hybrid approach. Materialize 3-6 months of instances for fast queries, store the pattern for long-term events, and track exceptions for modifications.

## 6.2 Time Zone Handling
Time zones are one of those problems that seem simple until you actually try to implement them. A meeting scheduled for "3 PM" needs context. Is that 3 PM in New York, which is 8 PM in London and 4 AM tomorrow in Tokyo? And what happens when daylight saving time kicks in and suddenly your 9 AM standup is at 8 AM for half your team?

### The Challenge
Time zone handling in calendars faces several tricky problems:
**Users travel.** When you fly from New York to London, your existing meetings should not suddenly move by 5 hours. That 2 PM client call should still be at 2 PM New York time, even if you are viewing it from London.
**Meetings have attendees in different zones.** A meeting between New York, London, and Tokyo teams needs to display the correct local time for each attendee.
**Daylight Saving Time exists.** Twice a year, clocks shift by an hour in many regions, but not at the same time globally. A "9 AM daily" meeting should stay at 9 AM local time, even when the UTC offset changes.
**All-day events are special.** Christmas Day is December 25th everywhere. It should not shift to December 24th or 26th just because the user traveled to a different timezone.

### Strategy 1: Store Everything in UTC
Store all event times as UTC timestamps in the database.

#### How It Works
1. Client sends event time with timezone: `2025-01-15T15:00:00-05:00` (3 PM EST)
2. Server converts to UTC: `2025-01-15T20:00:00Z`
3. Database stores UTC timestamp
4. When displaying, convert UTC to user's current timezone

#### Pros
- **Consistent storage:** All times comparable without conversion.
- **Simple range queries:** Compare UTC timestamps directly.
- **Handles travel:** Event stays at same absolute time.

#### Cons
- **Recurring event DST issues:** A "9 AM daily" meeting shifts by an hour during DST.
- **All-day event problems:** New Year's Day shouldn't change when you travel.

### Strategy 2: Store Local Time with Timezone (Recommended)
Store the local time and the timezone it was created in.

#### How It Works
Database stores:
- `start_time_local`: `2025-01-15T15:00:00`
- `timezone`: `America/New_York`

For queries and display:
1. Convert local time to UTC for the specific date (handling DST).
2. Compare with query range in UTC.
3. Display in user's current timezone.

#### Handling Recurring Events with DST
For a "9 AM daily" meeting in New York:
- Before DST (EST, UTC-5): 9 AM local = 2 PM UTC
- After DST (EDT, UTC-4): 9 AM local = 1 PM UTC

By storing local time + timezone, the meeting stays at 9 AM local time year-round.

#### All-Day Events
All-day events should be stored as dates without times:
- `start_date`: `2025-12-25`
- `is_all_day`: `true`

Display as December 25th regardless of the user's current timezone.

### Implementation
The following diagram visualizes how timezone conversion works across the system:

### Handling DST Transitions
For recurring events, storing local time with timezone ensures events stay at the intended local time across DST changes:

## 6.3 Conflict Detection and Free/Busy Queries
Nobody wants to accidentally double-book themselves, and scheduling a meeting with a team of 10 people is a nightmare without tooling support. Conflict detection and free/busy queries are essential features for any production calendar system.

### Use Cases
There are three main scenarios where we need to detect conflicts or query availability:
**Conflict Warning:** When a user creates or moves an event, warn them if it overlaps with something they already have scheduled. This is a gentle nudge, not a hard block, since sometimes double-booking is intentional (like marking tentative time).
**Find Available Slots:** When scheduling a meeting with multiple attendees, help find times when everyone is free. This is surprisingly complex because you need to check availability across multiple calendars, potentially in different time zones.
**Free/Busy Sharing:** Allow users to share their availability without revealing event details. A colleague might be able to see that you are "busy" from 2-3 PM without seeing that it is a dentist appointment.

### Basic Conflict Detection
The fundamental algorithm for detecting overlaps is straightforward. When creating or updating an event, check for overlapping events on the same calendar:
Two events overlap if:
- Event A starts before Event B ends, AND
- Event A ends after Event B starts

The following diagram illustrates different overlap scenarios:

### Handling Recurring Events in Conflict Detection
For recurring events, we need to:
1. **Query single events:** Use the SQL query above.
2. **Expand recurring events:** For each recurring event that might have instances in the range, compute instances.
3. **Check each instance:** Compare with the new event's time.

This is why the hybrid materialization approach helps. If instances are materialized, conflict detection is a simple query.

### Free/Busy API
The free/busy query returns availability without event details:

#### Endpoint: GET /users/{user_id}/freebusy

##### Request Parameters:
- **start_time**: Beginning of the query range
- **end_time**: End of the query range

##### Response:

### Finding Available Slots
To find a time when multiple attendees are free:
1. Fetch free/busy for each attendee in the desired range.
2. Merge all busy periods.
3. Find gaps that are long enough for the meeting.
4. Return available slots.

#### Algorithm:
The following diagram visualizes the algorithm for finding available slots:

### Performance Optimization
For fast free/busy queries:
1. **Pre-compute busy blocks:** When events change, update a separate free_busy table.
2. **Cache aggressively:** Free/busy data changes infrequently.
3. **Limit range:** Cap queries to reasonable ranges (e.g., 30 days).

## 6.4 Reminder System Design
Reminders are what make calendars actually useful. Without them, a calendar is just a storage system for events you will forget about. The challenge is delivering millions of reminders at precisely the right time, without overwhelming system resources or missing deadlines.

### The Challenge
Think about the scale of the reminder problem:
**Timing precision matters.** A reminder that arrives 5 minutes late might mean a missed meeting. Users expect reminders to arrive within seconds of their scheduled time, not minutes.
**Volume is substantial.** With 100 million users, many with multiple daily events and multiple reminders per event, we might have tens of millions of reminders firing per day. And they are not evenly distributed: 9 AM Monday has far more reminders than 3 AM Saturday.
**Recurring events complicate things.** A daily standup has a reminder that fires every weekday. Should we store 260 reminder rows for a year's worth of standups? That seems wasteful.
**Changes cascade.** When a user moves a meeting from 3 PM to 4 PM, all the reminders need to update. When they delete the meeting, reminders need to be cancelled.
**Delivery must be reliable.** A reminder that silently fails is worse than useless. We need at-least-once delivery semantics, with retries for transient failures.

### Approach 1: Store All Reminders
Create a reminder row for every event instance.

#### How It Works
When an event is created with a "10 minutes before" reminder:
1. Calculate the trigger time: `event_start - 10 minutes`
2. Insert into reminders table with `trigger_time` and `sent = false`
3. Background job queries for due reminders every minute
4. Mark as sent after delivery

#### Pros
- Simple to implement
- Easy to query for due reminders

#### Cons
- Storage explosion for recurring events
- Must update reminders when events change
- Cleanup needed for past reminders

### Approach 2: Compute Reminders Dynamically (Recommended)
Store reminder preferences with events, compute trigger times on demand.

#### How It Works
1. **Event stores reminder offsets:** `reminders: [-10m, -1h]` (10 minutes and 1 hour before)
2. **Reminder scanner runs periodically:**
3. **Use a scheduled job queue:** Push jobs to trigger at specific times

#### Implementation with Message Queue
The following diagram illustrates the reminder scanning and delivery flow:

#### Handling Event Updates
When an event is modified:
1. If start time changes, recalculate reminder times
2. Cancel pending reminder jobs for old times
3. Schedule new reminder jobs

#### Idempotency
To prevent duplicate reminders:
1. Include a unique reminder ID in each job: `{event_id}_{instance_date}_{offset}`
2. Before sending, check if this ID was already processed
3. Use Redis SET with expiration to track sent reminders

### Delivery Channels

#### Push Notifications
- Fast, real-time delivery
- Requires device tokens
- Handle token expiration and app uninstalls

#### Email
- Reliable but slower
- Good for important events
- Include calendar attachment (.ics) for easy adding

## 6.5 Scaling Calendar Reads
Calendar views are the most frequent operations by far. Users check their calendars constantly: opening the day view to see what is coming up, switching to week view for planning, and occasionally looking at the month view for the big picture. If these views are slow, the entire product feels sluggish.
With our estimated read QPS of 17,500 at peak, we need to think carefully about read optimization. Database queries for every request will not scale.

### Caching Strategy
The key insight is that calendar data changes infrequently relative to how often it is read. Most users check the same week dozens of times between making any changes. This makes caching highly effective.

#### What to Cache
**Calendar views:** When a user requests events for January 15-21, we compute the result (including recurring event expansion) and cache it. The next time they request the same range, we return the cached result instantly.
**User's calendar list:** The list of calendars a user owns or has access to changes rarely. Cache this for fast navigation.
**Individual events:** When displaying event details or checking for conflicts, we often need to look up single events by ID. Cache these for fast point lookups.

#### Cache Key Design
The cache key structure determines how efficiently we can invalidate data when it changes:
Including `user_id` in the calendar view key is important because shared calendars might need different views for different users (based on timezone settings or permission levels).

#### Cache Invalidation
Caching is easy. Invalidation is hard. When an event changes, we need to clear any cached views that included it:
1. **Clear the event cache:** Delete `event:{event_id}`
2. **Clear affected views:** Any cached view whose date range contains this event needs to be cleared
3. **Handle shared calendars:** If the calendar is shared, clear views for all users with access

For efficiency, we can use pattern-based deletion or tag-based invalidation:
The following diagram shows the caching architecture and invalidation flow:

### Read Replicas
For high read volume:
1. Route read queries to PostgreSQL read replicas
2. Accept slight staleness (seconds) for calendar views
3. Route writes to primary

### Materialized Views
Pre-compute common queries:
1. "Events this week" per user
2. "Upcoming events with reminders"
3. Refresh periodically or on event changes

## 6.6 Event Synchronization
Calendar systems are inherently collaborative. When Alice moves the 2 PM meeting to 3 PM, Bob and Carol need to see that change immediately, not the next time they refresh. And when Carol is on the subway with no connectivity, any changes she makes need to sync back when she gets signal.
This section covers how we keep all clients in sync, both in real-time and after periods of offline usage.

### Real-Time Updates with WebSockets
For users who have the calendar app open, we want changes to appear instantly. The standard approach is WebSockets, which maintain a persistent connection between the client and server.
1. **Subscribe on load:** Client connects to WebSocket and subscribes to their calendars.
2. **Broadcast changes:** When an event changes, push update to all subscribed users.
3. **Selective updates:** Only send changes relevant to the user's current view.

### Conflict Resolution
What happens when Alice and Bob both try to update the same meeting at the same time? This is a classic distributed systems problem, and there are several approaches:
**Last-write-wins:** The simplest approach. Whatever update arrives at the server last becomes the authoritative version. This works but can silently lose changes. If Alice updates the title while Bob updates the location, only one set of changes survives.
**Optimistic locking:** Include a version number with each event. When updating, check that the version matches. If someone else updated first, reject the stale update and ask the user to retry with the latest data.
**Field-level merging:** Track changes at the field level. If Alice updates the title and Bob updates the location, merge both changes. Only flag a conflict if both touched the same field.
For calendar systems, optimistic locking is usually the right choice. It is simple to implement and calendar conflicts are rare enough that occasional retry prompts are acceptable. Add a `version` column to the events table and use this update pattern:
If zero rows are updated, someone else modified the event first. Fetch the latest version and prompt the user to retry.

### Sync Protocol for Mobile
Mobile apps face a unique challenge: they need to work offline. A user might be on a plane, in a subway, or simply in an area with poor connectivity. Any changes they make while offline need to sync back when connectivity returns.
1. **Sync tokens:** Track last sync point, fetch only changes since then.
2. **Local-first:** Store events locally, sync when online.
3. **Conflict detection:** When syncing, detect and resolve conflicts.

# References
- [Google Calendar API Documentation](https://developers.google.com/calendar) - Official documentation for Google Calendar's API design and features
- [RFC 5545: iCalendar Specification](https://datatracker.ietf.org/doc/html/rfc5545) - The standard for calendar data exchange including RRULE format
- [Time Zones and Daylight Saving Time](https://www.iana.org/time-zones) - IANA time zone database documentation

# Quiz

## Design Calendar System Quiz
Why is it generally better to store event timestamps in UTC in a calendar system?