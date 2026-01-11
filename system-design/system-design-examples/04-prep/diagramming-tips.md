# Diagramming Tips & Visual Notation

In a system design interview, **your diagram is your story**. It’s how you demonstrate structure, explain trade-offs, and visualize scalability—all at a glance. You don't need to be an artist; you just need to be a clear communicator.
Great diagrams act as a map for your conversation, helping the interviewer follow your thought process as you build, scale, and fortify your system. A poor diagram, on the other hand, can create confusion and ambiguity, even if your underlying design is solid.
The goal is to create visuals that are **structured, minimal, and layered**.
This guide will break down how to structure your diagrams, what symbols to use, and how to make them communicate like a professional system designer.
# 1. Why Diagramming Matters in System Design Interviews
Drawing is not just a formality; it's a core part of the problem-solving process.
- **It shows your architectural thinking.** A well-organized diagram reflects a well-organized mind.
- **It anchors the conversation.** Both you and the interviewer can point to components and discuss them in context.
- **It prevents you from missing key components.** When you draw the boxes for a cache, a load balancer, and a message queue, you're less likely to forget them in your explanation.
- **It makes trade-offs visual.** You can easily show where you're adding a replica for availability or a CDN for lower latency.

A good system design interview feels like you're drawing a map together—your diagram is the compass that guides the exploration.
# 2. The Layered Approach
Don't try to draw the entire, final system all at once. The best approach is to build your diagram in layers, adding complexity as the conversation evolves. This shows the interviewer you can think from a high level before diving into the details.
| Layer | Focus | Example Components |
| --- | --- | --- |
| 1. High-Level Overview | The "bird's-eye view." Show only the core components and user interaction. | Client → API Gateway → Service → Database |
| 2. Core Services | Break down the main application into its key functional parts. | Authentication Service, Feed Service, Storage Service, Cache |
| 3. Scaling & Reliability | Add components that handle load and ensure fault tolerance. | Load Balancer, Read Replicas, Message Queue, Workers |
| 4. Deep Dive (Optional) | Zoom into a specific part of the system if asked. | Data partitioning strategy, async message flow, CDN edge logic. |

Here’s an example that combines these layers:
Start simple. Then, as the conversation evolves, add layers like caching and message queues without cluttering the initial view.
# 3. Common Visual Notation and Symbols
Using standard symbols makes your diagrams instantly recognizable. You don't need to be a UML expert, but knowing these basic shapes helps.
| Symbol | Meaning | Example |
| --- | --- | --- |
| 🟦 Box / Rectangle | A compute component or a service. | API Server, Worker, Service |
| 🛢️ Cylinder | A storage system or database. | SQL DB, NoSQL DB, Redis |
| 🔹 Diamond | A routing or decision-making component. | Load Balancer, API Gateway, Router |
| ➡️ Arrow | Data flow, a request, or a relationship. | API → Database |
| ☁️ Cloud Shape | An external or third-party service. | CDN, Payment Gateway |
| 📦 Rectangle with folded corner | A message queue or message broker. | Kafka, RabbitMQ, SQS |

# 4. Use Consistent Visual Grammar
Consistency is key to a readable diagram. Think of it as the "style guide" for your architecture.
**Do:**
- Use the **same shape** for the same type of component (e.g., all databases are cylinders).
- **Align** boxes neatly, either horizontally or vertically.
- Use arrows to clearly show the **direction of data flow**.
- Keep **naming conventions** consistent (e.g., `UserService`, `AuthService`).

**Don't:**
- Mix shapes arbitrarily for similar components.
- Let arrows cross over each other unnecessarily.
- Overload the diagram with long sentences of text.

# 5. Group Related Components
Grouping components into logical blocks adds a layer of hierarchy to your design. It helps you explain your system top-down and makes each part easier to reason about.
| Group | Example Components |
| --- | --- |
| Client Tier | Web App, Mobile App, Browser |
| API / Gateway Tier | API Gateway, Authentication Service, Rate Limiter |
| Application Tier | Business logic, Feed Service, Recommendation Service |
| Data Tier | Database, Cache, Object Store, Search Index |
| Infrastructure | CDN, Load Balancer, Message Queue |

# 6. Highlight Data Flow and Interaction
A static diagram shows components, but a dynamic one shows how they interact. Use arrows and labels to narrate the flow of data.
- Use **solid arrows** for synchronous requests (e.g., an API call that waits for a response).
- Use **dashed arrows** for asynchronous events (e.g., sending a message to a queue).
- **Label arrows** for critical interactions to remove ambiguity.

A sequence diagram is excellent for detailing a specific interaction:
# 7. Tools for Drawing Diagrams
Practice with a tool before your interview so you're fast and comfortable. Speed and clarity matter more than perfect aesthetics.

#### Excalidraw
Simple, fast, and has a hand-drawn feel that looks great.
**Best for:** Live whiteboard-style sketching

#### Mermaid
Excellent for documentation and version control.
**Best for:** Text-based diagrams in Markdown

#### Draw.io (diagrams.net)
Free, powerful, and has a rich set of icons.
**Best for:** Classic drag-and-drop diagramming

#### Lucidchart / Whimsical
Clean visuals, templates, and great alignment tools.
**Best for:** Collaborative, polished designs
# Quiz

## Diagramming Tips Quiz
In a system design interview, what is the primary role of your diagram?