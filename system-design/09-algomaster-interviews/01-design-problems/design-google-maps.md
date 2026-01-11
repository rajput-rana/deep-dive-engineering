# Design Google Maps

## What is Google Maps?

Google Maps is a navigation and mapping service that helps users find locations, get directions, and explore geographic areas through interactive maps.
The core functionality includes rendering maps at various zoom levels, searching for places, calculating routes between locations, and providing real-time traffic updates.
Users can view maps in different modes (road, satellite, terrain), get turn-by-turn navigation, and discover points of interest like restaurants, gas stations, and landmarks.
**Popular Examples:** Google Maps, Apple Maps, Waze, MapQuest, HERE WeGo
What makes Google Maps fascinating from a system design perspective is the sheer diversity of challenges it presents. These challenges are very different from each other, yet they all need to work together seamlessly.
Serving map tiles requires handling millions of requests per second with sub-second latency. Location search demands sophisticated text matching and geospatial indexing. Route calculation involves running graph algorithms on a network with billions of edges. And real-time traffic requires ingesting and processing data from millions of devices simultaneously.
This system design problem tests multiple fundamental concepts: geospatial data structures, caching at scale, graph algorithms, real-time data processing, and geographic distribution. The interviewer can steer the conversation in many directions depending on your experience and the role.
In this chapter, we will explore the **high-level design of a mapping and navigation service like Google Maps**.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
A mapping service can mean many things. Are we building a simple static map viewer, or do we need turn-by-turn navigation with voice guidance? Should we support public transit, or just driving? Do we need to handle offline scenarios? 
These questions significantly impact our architecture, so we need to get clarity upfront.
Here is how a requirements discussion might unfold in an interview:
**Candidate:** "What are the core features we need to support? Should we focus on map viewing, navigation, or both?"
**Interviewer:** "Focus on map rendering, location search, and navigation with routing. Real-time traffic would be a good addition if time permits."
**Candidate:** "What is the expected scale? How many users and how many navigation requests per day?"
**Interviewer:** "Assume 1 billion daily active users globally, with 100 million navigation requests per day."
**Candidate:** "Should we support multiple transportation modes like driving, walking, cycling, and public transit?"
**Interviewer:** "Start with driving. You can mention how the design would extend to other modes."
**Candidate:** "How accurate do the ETAs need to be? Should we incorporate real-time traffic data?"
**Interviewer:** "Yes, real-time traffic is important. ETAs should be within 10-15% accuracy."
**Candidate:** "Do we need to support offline maps for areas without connectivity?"
**Interviewer:** "That's a nice-to-have. Focus on the online experience first."
**Candidate:** "What about the map data itself? Should we assume we have access to road network and POI data?"
**Interviewer:** "Yes, assume map data is available from providers like OpenStreetMap or licensed sources."
This conversation reveals several important constraints. We are building a read-heavy system with massive scale, we need real-time data integration, and we have three distinct subsystems (maps, search, navigation) that must work together. 
Let's formalize these requirements.

## 1.1 Functional Requirements
- **Map Rendering:** Display interactive maps at various zoom levels with smooth panning and zooming.
- **Location Search:** Allow users to search for addresses, places, and points of interest (POI).
- **Navigation:** Calculate optimal routes between origin and destination with turn-by-turn directions.
- **ETA Calculation:** Provide accurate estimated time of arrival based on current traffic conditions.
- **Real-time Traffic:** (Optional) Display traffic conditions and adjust routes dynamically.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider what makes the system production-ready at global scale:
- **Low Latency:** Map tiles should load within 200ms. Route calculations should complete within 1-2 seconds.
- **High Availability:** The system must be highly available (99.99%) since users depend on it for navigation.
- **Scalability:** Support billions of map tile requests and millions of navigation requests daily.
- **Global Coverage:** Serve users worldwide with consistent performance across regions.

# 2. Back-of-the-Envelope Estimation
Before diving into the architecture, let's run some calculations to understand the scale we are dealing with. These numbers will guide our decisions about storage, caching, and infrastructure.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:

#### Map Tile Requests
Map tiles are the foundation of the visual experience. Every time a user pans or zooms, the app requests new tiles. Let's estimate the volume:
This is an enormous number. To put it in perspective, 1.4 million requests per second means we need a highly distributed system with aggressive caching. There is no way a centralized architecture can handle this.

#### Navigation Requests
Navigation requests are more compute-intensive but less frequent:
While 3,500 QPS might seem modest compared to tile requests, each navigation request requires complex graph computation. This is CPU-bound work that cannot be infinitely cached, since routes depend on real-time traffic.

### 2.2 Storage Estimates
Map storage is where things get interesting. We need to store pre-rendered tiles for the entire world at multiple zoom levels.

#### Map Tile Storage
But we do not just store one zoom level. We need tiles from zoom level 0 (entire world in one tile) to level 18 or higher (individual buildings visible). Fortunately, lower zoom levels have far fewer tiles:

#### Road Network Graph
The road network is a graph where nodes are intersections and edges are road segments:
This is actually quite manageable. The road graph can fit in memory on a single large server, though we will want to distribute it for availability and to reduce latency.

### 2.3 Key Insights
These estimates reveal several important design implications:
1. **Tile serving is the bottleneck:** With 1.4 million QPS at peak, we need a massively distributed caching layer. CDNs are essential, not optional.
2. **Navigation is compute-intensive:** While QPS is lower, each request requires graph traversal on a billion-edge graph. We need algorithmic optimizations, not just more servers.
3. **Storage is substantial but manageable:** Petabytes of tiles can be handled with object storage. The road graph fits in memory, which is good for performance.
4. **Geographic distribution is critical:** Users are distributed globally, and latency matters. We need data centers and CDN edge nodes worldwide.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Our mapping service needs three main APIs: one for map tiles, one for location search, and one for directions.

### 3.1 Get Map Tiles

#### Endpoint: GET /tiles/{zoom}/{x}/{y}
This is our highest-volume endpoint. It returns a single map tile image for the specified coordinates and zoom level.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| zoom | integer | Zoom level (0-22). Level 0 shows the entire world, level 18+ shows street details |
| x | integer | Tile column number (0 to 2^zoom - 1) |
| y | integer | Tile row number (0 to 2^zoom - 1) |

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| style | string | No | Map style: "roadmap", "satellite", "terrain", or "hybrid". Defaults to "roadmap" |

#### Response:
Returns a 256×256 pixel PNG or WebP image. Response headers include aggressive cache-control directives since tiles rarely change:

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid parameters | Zoom level out of range or invalid x/y coordinates |
| 404 Not Found | Tile does not exist | Coordinates are valid but tile is not generated (ocean, etc.) |

The key design decision here is making tiles infinitely cacheable. Map geometry changes infrequently, so we can cache for a year and use ETags for revalidation.

### 3.2 Search Places

#### Endpoint: GET /places/search
Searches for places matching a query string, with optional location biasing.

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| query | string | Yes | Search string (e.g., "coffee shops", "123 Main St", "SFO airport") |
| location | string | No | Latitude,longitude to bias results toward (e.g., "37.7749,-122.4194") |
| radius | integer | No | Search radius in meters. Only applies if location is provided |
| limit | integer | No | Maximum number of results (default: 10, max: 50) |

#### Success Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Missing query or malformed location |
| 404 Not Found | No results | Query returned zero matches |

### 3.3 Get Directions

#### Endpoint: GET /directions
Calculates a route between origin and destination with turn-by-turn directions.

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| origin | string | Yes | Starting point (lat,lng or place_id or address) |
| destination | string | Yes | End point (lat,lng or place_id or address) |
| mode | string | No | Transportation mode: "driving", "walking", "cycling". Defaults to "driving" |
| departure_time | integer | No | Unix timestamp for traffic-aware routing. Defaults to now |
| alternatives | boolean | No | If true, return up to 3 alternative routes |

#### Success Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Cannot parse origin or destination |
| 404 Not Found | No route found | No possible route between points (e.g., across oceans) |

Notice that we return both `duration_seconds` (without traffic) and `duration_in_traffic_seconds` (with current traffic). This helps users understand how much delay traffic is adding.
# 4. High-Level Design
Now we get to the heart of the design. Rather than presenting a complex diagram upfront, we will build the architecture incrementally, addressing one requirement at a time. This mirrors how you would approach the problem in an interview and makes the reasoning easier to follow.
Our system needs to handle three distinct operations:
1. **Map Rendering:** Serve pre-rendered map tiles with extremely low latency
2. **Location Search:** Find places based on text queries with geographic awareness
3. **Navigation:** Calculate optimal routes considering real-time traffic

Each of these has very different characteristics. Map tiles are static and highly cacheable. Location search requires text indexing and geospatial queries. Navigation involves complex graph algorithms with real-time data. Let's tackle them one by one.

## 4.1 Requirement 1: Map Rendering
When you open a mapping app and see a detailed street map, you are actually looking at dozens of small images stitched together seamlessly. These images, called tiles, are the fundamental building block of web-based mapping.

### Why Tiles?
Rendering the entire world as a single image would be absurd. At street-level detail, such an image would be trillions of pixels across. Instead, we divide the world into a grid of small squares, each 256×256 pixels. The client only requests and renders the tiles that are currently visible in the viewport.
This approach has several advantages:
- **Parallel loading:** The browser can fetch multiple tiles simultaneously
- **Aggressive caching:** Tiles can be cached at CDN edges worldwide
- **Progressive rendering:** Users see something immediately, even if not all tiles have loaded
- **Efficient updates:** When map data changes, we only re-render affected tiles

### The Tile Pyramid
Tiles are organized in a hierarchical structure called a tile pyramid. At zoom level 0, the entire world fits in a single tile. At zoom level 1, the world is divided into a 2×2 grid (4 tiles). At zoom level 2, it is a 4×4 grid (16 tiles), and so on.
Each tile is identified by three numbers: **(z, x, y)** where z is the zoom level, x is the column, and y is the row. Given a geographic coordinate (latitude, longitude), we can calculate exactly which tile contains that point at any zoom level.

### Components for Map Rendering
To serve tiles at the scale we calculated (1.4 million QPS at peak), we need a distributed architecture with multiple caching layers.

#### CDN (Content Delivery Network)
The CDN is our first and most important layer of defense against the traffic tsunami. With edge nodes in hundreds of locations worldwide, the CDN serves cached tiles from a location geographically close to the user.
For map tiles, we set extremely aggressive cache headers: `Cache-Control: public, max-age=31536000` (1 year). Since map geometry rarely changes, we can cache indefinitely and rely on cache invalidation when updates occur. This results in a 95%+ cache hit rate at the edge, meaning only 5% of requests ever reach our origin servers.

#### Tile Service
The Tile Service handles the small percentage of requests that miss the CDN cache. It retrieves tiles from object storage and can perform on-the-fly transformations if needed (different styles, overlays, etc.).
The service is stateless and horizontally scalable. Each instance independently handles requests without coordination, making it easy to add capacity during traffic spikes.

#### Object Storage
Pre-rendered tiles are stored in object storage like Amazon S3 or Google Cloud Storage. The storage is organized by zoom level and coordinates for efficient retrieval:
Object storage is the right choice here because tiles are static binary files with simple key-based access. We do not need database features like transactions or complex queries.

### The Tile Request Flow
Let's trace what happens when a user pans to a new area of the map:
The key insight is that most users see most tiles from cache. When you view San Francisco, millions of other users have already viewed those same tiles, so they are warm in the CDN cache. Only truly obscure areas or fresh data require a trip to origin.

## 4.2 Requirement 2: Location Search
Users need to find places by name, address, or category. A good search experience handles typos, understands context ("coffee" means coffee shops, not coffee beans), and ranks results by relevance and proximity.
This is fundamentally different from tile serving. Tiles are static and cacheable; search is dynamic and personalized (results depend on the user's location). We need different infrastructure.

### Components for Location Search

#### Geocoding Service
The Geocoding Service is responsible for converting human-readable queries into geographic coordinates. This is called geocoding. The reverse operation, converting coordinates to an address, is called reverse geocoding.
The service handles several types of queries:
- **Addresses:** "123 Main Street, San Francisco" → (37.7749, -122.4194)
- **Place names:** "Golden Gate Bridge" → (37.8199, -122.4783)
- **Categories:** "coffee shops near me" → [list of nearby coffee shops]

#### Search Index
We use a search engine like Elasticsearch to power fast text search. The index contains:
- Place names and aliases ("SF" → "San Francisco")
- Addresses and address components
- Categories and keywords
- Geographic coordinates for location-based filtering

The index supports fuzzy matching (finding "Starbuks" when the user meant "Starbucks"), prefix search for autocomplete, and geospatial queries.

#### Places Database
The Places Database (PostgreSQL with PostGIS extension) stores the complete record for each place: name, address, coordinates, business hours, phone number, ratings, photos, and more. The search index returns place IDs; we then hydrate full records from this database.
Why separate the search index from the database? Because they are optimized for different things. Elasticsearch excels at text search and fuzzy matching. PostgreSQL excels at storing structured data with referential integrity. Using both gives us the best of both worlds.

### The Search Flow
Let's trace a search request from the user's perspective:
Notice the caching layer. Common searches like "Starbucks" or "gas station" near popular locations are cached to avoid hitting the search index repeatedly. The cache is keyed on (query, location_bucket) where location_bucket is a coarse grid cell.

## 4.3 Requirement 3: Navigation and Routing
Navigation is the crown jewel of a mapping service. It is also the most computationally challenging. Finding the optimal route between two points requires traversing a graph with billions of edges, incorporating real-time traffic data, and doing it all in under 2 seconds.

### The Road Network Graph
We model the road network as a weighted directed graph:
- **Nodes:** Intersections, road endpoints, and significant waypoints
- **Edges:** Road segments connecting nodes
- **Weights:** Travel time (which varies based on traffic)

The graph is directed because some roads are one-way, and weights differ by direction (uphill is slower than downhill). Edges also carry metadata like road name, road type, and restrictions.

### Components for Navigation

#### Routing Service
The Routing Service is the brain of navigation. It receives an origin and destination, queries the Traffic Service for current road conditions, and runs graph algorithms on the Road Graph to find the optimal path.
The service handles various complexities:
- Converting addresses to coordinates (using the Geocoding Service)
- Snapping coordinates to the nearest road
- Respecting turn restrictions and one-way streets
- Finding alternative routes for user choice
- Handling edge cases like routing across ferry connections

#### Traffic Service
The Traffic Service collects and processes real-time traffic data from multiple sources:
- GPS probe data from millions of mobile devices
- Historical traffic patterns by time of day
- Incident reports (accidents, construction)
- Road sensors on major highways

It provides current travel times for road segments, which the Routing Service uses as edge weights in the graph.

#### Directions Service
Once the Routing Service finds the optimal path (a sequence of nodes/edges), the Directions Service converts it into human-readable instructions:
- "Head north on Market Street toward 5th Street"
- "Turn right onto 5th Street"
- "Merge onto US-101 South"
- "Take exit 429 toward SFO Airport"

It also encodes the route as a polyline for rendering on the map.

### The Navigation Flow

## 4.4 Putting It All Together
Now let's combine all the components into a complete architecture. Each layer has a specific responsibility, and the components work together to deliver the mapping experience.

### Component Responsibilities Summary
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| CDN | Global tile caching, DDoS protection | Managed service (auto-scales) |
| Load Balancer | Traffic distribution, health checks | Managed service |
| API Gateway | Auth, rate limiting, request routing | Horizontal (stateless) |
| Tile Service | Serve tiles on cache miss | Horizontal (stateless) |
| Geocoding Service | Address/place search | Horizontal (stateless) |
| Routing Service | Calculate optimal routes | Horizontal (graph is read-only) |
| Traffic Service | Aggregate and serve traffic data | Horizontal with sharding by region |
| Directions Service | Generate turn-by-turn instructions | Horizontal (stateless) |
| Redis Cache | Cache search results, routes, traffic | Redis Cluster |
| Object Storage | Store map tiles | Managed (infinite scale) |
| PostgreSQL + PostGIS | Store places with geospatial queries | Read replicas by region |
| Elasticsearch | Power text search | Cluster with sharding |
| Road Graph | Store network for routing | Replicated by region |
| TimescaleDB | Store traffic time-series | Sharded by time and region |

# 5. Database Design
With the high-level architecture in place, let's dive into the data layer. Different types of data have different access patterns, and we will use different storage solutions accordingly.

## 5.1 Choosing the Right Databases
Our system handles four main types of data, each with unique requirements:

#### Map Tiles
- Billions of static binary files (images)
- Simple key-based access: given (z, x, y), return the tile
- Extremely read-heavy with aggressive caching
- **Choice:** Object storage (S3, GCS) with CDN

#### Places Data
- Structured data with multiple fields
- Complex queries: full-text search, geospatial filtering, sorting
- Need to support "near me" queries efficiently
- **Choice:** PostgreSQL with PostGIS extension + Elasticsearch for search

#### Road Network
- Graph structure with nodes (intersections) and edges (road segments)
- Access pattern is graph traversal: given a node, find neighbors
- Need to support shortest-path algorithms efficiently
- **Choice:** Custom in-memory graph structure or Neo4j

#### Traffic Data
- Time-series data with high write throughput
- Queries by road segment and time range
- Need current data (last 5 minutes) with very low latency
- **Choice:** Redis for current state, TimescaleDB for history

## 5.2 Database Schema

### Places Table
This is the core table for location search. Each row represents a searchable location.
| Field | Type | Description |
| --- | --- | --- |
| place_id | VARCHAR(64) PK | Unique identifier (e.g., "ChIJN1t_...") |
| name | VARCHAR(255) | Display name of the place |
| address | VARCHAR(500) | Formatted address |
| latitude | DOUBLE | Geographic latitude |
| longitude | DOUBLE | Geographic longitude |
| location | GEOMETRY(POINT) | PostGIS point for spatial queries |
| geohash | VARCHAR(12) | Geohash for grid-based queries |
| rating | FLOAT | Average user rating (1-5) |
| review_count | INTEGER | Number of reviews |
| phone | VARCHAR(20) | Contact phone number |
| website | VARCHAR(255) | Business website |
| hours | JSONB | Operating hours by day |
| updated_at | TIMESTAMP | Last update time |

**Indexes:**

### Road Nodes and Edges Tables
The road network is stored as a graph with separate tables for nodes and edges.
**Road Nodes:**
| Field | Type | Description |
| --- | --- | --- |
| node_id | BIGINT PK | Unique node identifier |
| latitude | DOUBLE | Geographic latitude |
| longitude | DOUBLE | Geographic longitude |
| geohash | VARCHAR(12) | For geographic partitioning |

**Road Edges:**
| Field | Type | Description |
| --- | --- | --- |
| edge_id | BIGINT PK | Unique edge identifier |
| from_node | BIGINT FK | Starting node |
| to_node | BIGINT FK | Ending node |
| distance_meters | INTEGER | Length of road segment |
| road_type | VARCHAR(20) | Highway, primary, secondary, residential, etc. |
| speed_limit_kmh | INTEGER | Posted speed limit |
| is_oneway | BOOLEAN | One-way restriction |
| road_name | VARCHAR(255) | Name of the road |
| linestring | GEOMETRY | Actual road shape for rendering |

**Indexes:**
In practice, for routing algorithms, the graph is loaded into memory for faster traversal. The database serves as persistent storage and is used to rebuild the in-memory graph after updates.

### Traffic Segments Table
Stores real-time traffic information. This is time-series data with high write volume.
| Field | Type | Description |
| --- | --- | --- |
| edge_id | BIGINT | Reference to road edge |
| recorded_at | TIMESTAMP | When this data was recorded |
| current_speed_kmh | INTEGER | Current average speed |
| free_flow_speed_kmh | INTEGER | Speed under ideal conditions |
| congestion_level | VARCHAR(20) | free, light, moderate, heavy, severe |
| incidents | JSONB | Active incidents (accidents, construction) |

This table uses TimescaleDB's hypertable partitioning by time, allowing efficient queries for recent data and automatic expiration of old data.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. In this section, we will explore the key technical challenges: efficient tile systems, geospatial indexing, routing algorithms, and real-time traffic processing.

## 6.1 Map Tile System Deep Dive
The tile system seems simple on the surface, but there are important design decisions that affect storage, performance, and flexibility.

### Vector Tiles vs. Raster Tiles
There are two fundamentally different approaches to tile rendering:
**Raster Tiles (Traditional)**
Pre-rendered PNG or JPEG images. The server does all the rendering work upfront, and clients simply display the images.
**Vector Tiles (Modern)**
Tiles contain raw geographic data (roads, buildings, labels) in a compact binary format. Rendering happens on the client's GPU.
**Recommendation:** Use vector tiles for road maps (smaller, flexible, smooth zooming) and raster tiles for satellite imagery (cannot be vectorized).

### Storage Optimization
Not all zoom levels need full global coverage. We can save petabytes by being selective:
| Zoom Range | Coverage | Size | Notes |
| --- | --- | --- | --- |
| 0-10 | Full global | ~20 GB | Country to city level |
| 11-14 | Urban + suburban | ~5 TB | Skip empty ocean/desert |
| 15-18 | Dense urban only | ~500 TB | Skip rural areas |
| 19+ | On-demand | N/A | Generated when requested |

This selective coverage reduces storage from 10 PB to under 1 PB while still providing excellent coverage for where users actually look.

### CDN Caching Strategy
Map tiles are perfect for CDN caching because they are immutable once generated. Our caching strategy:
- **Cache-Control:** `public, max-age=31536000, immutable` (1 year, immutable flag tells browsers this will never change)
- **ETags:** Include content hash for conditional requests
- **Cache invalidation:** When map data updates, generate new tile versions with new ETags

With this strategy, we achieve 95%+ CDN hit rates. The remaining 5% are either cold tiles (obscure locations) or the first request after a map update.

## 6.2 Geospatial Indexing
"Near me" queries are fundamental to location search. We need to efficiently answer: "What places are within 1km of my current location?" Several data structures help with this.

### Geohash
Geohash encodes latitude/longitude into a string where nearby locations share common prefixes.
**How we use it:** Store geohash as a column, index it, and query with prefix matching. To find places near `9q8yyk`, we query for all places where `geohash LIKE '9q8yyk%'`. This is much faster than calculating distances for every place in the database.
**Limitation:** Geohash cells are rectangular and do not perfectly match circular distance queries. We typically query a slightly larger area (neighboring cells) and filter by exact distance.

### R-Tree / PostGIS
For precise geospatial queries, PostgreSQL with PostGIS provides R-tree indexes that support:
PostGIS uses spatial indexes (GiST) that efficiently handle these queries without scanning all rows.

### Search Ranking
Finding nearby places is just the first step. We also need to rank them by relevance. Our ranking considers:

## 6.3 Routing Algorithms
Finding the optimal route in a graph with billions of edges is computationally expensive. Standard algorithms like Dijkstra's would take minutes. We need smarter approaches.

### Why Dijkstra Is Not Enough
Dijkstra's algorithm explores nodes in order of distance from the source. For a cross-country route, it might explore millions of nodes before finding the destination. At 1,150 navigation QPS, this is far too slow.

### Contraction Hierarchies
This is the industry-standard algorithm for long-distance routing. The key insight is that highway networks are hierarchical: you take local roads to reach a highway, highways to cross the country, and local roads again at the destination.

#### Preprocessing Phase (runs offline):
1. Order nodes by "importance" (highways > main roads > local streets)
2. Contract less important nodes by adding shortcuts
3. Store the hierarchy

#### Query Phase (runs online):
1. Run bidirectional search: from origin AND from destination
2. Only traverse "upward" in the hierarchy
3. Searches meet at high-importance nodes (highways)

This reduces query time from minutes to milliseconds, roughly 1000x improvement.

### Handling Real-Time Traffic
Contraction Hierarchies assume static edge weights, but traffic is dynamic. We use a hybrid approach:
1. **Highway network:** Use Contraction Hierarchies (traffic on highways is more predictable)
2. **Local roads:** Use A* algorithm with real-time traffic weights
3. **Dynamic shortcuts:** Periodically rebuild hierarchy shortcuts for different traffic conditions (rush hour vs. night)

### Algorithm Comparison
| Algorithm | Preprocess Time | Query Time | Handles Traffic | Best For |
| --- | --- | --- | --- | --- |
| Dijkstra | None | O(E log V), slow | Yes | Small graphs |
| A* | None | 2-10x faster | Yes | Short routes, rerouting |
| Contraction Hierarchies | Hours | Milliseconds | Hard | Long-distance |
| Hybrid (CH + A*) | Hours | Fast | Yes | Production systems |

## 6.4 Real-Time Traffic Processing
Accurate ETAs require real-time traffic data. This is one of the most complex parts of the system.

### Data Sources
Traffic data comes from multiple sources:
**GPS Probe Data** is the most valuable source. Millions of smartphones running mapping apps share their location and speed (anonymized). We aggregate this data per road segment to calculate average speeds.

### ETA Calculation
ETA is the sum of travel times across all edges in the route:
For each edge, we determine the speed using:
1. **Real-time data:** If we have fresh probe data (< 5 minutes old), use it
2. **Historical average:** If no real-time data, use historical pattern for this day/time
3. **Free-flow speed:** If no data at all, use speed limit

### Predictive Traffic
For longer trips, traffic will change during the journey. We predict future conditions using:
- Current trends (is traffic getting better or worse?)
- Historical patterns (it is 5pm on a Friday, expect heavy traffic)
- Known events (concert at 7pm will cause congestion)

Machine learning models (LSTMs, transformers) trained on years of traffic data can predict conditions 30-60 minutes ahead with reasonable accuracy.

## 6.5 Scaling and Geographic Distribution
Serving users globally requires careful attention to data placement and request routing.

### Regional Architecture
We deploy the system in multiple regions (US, Europe, Asia) with data replicated appropriately:
**Data placement strategy:**
- **Map tiles:** Replicated to all regions (read-only, easy to replicate)
- **Places data:** Regional copies with eventual consistency
- **Road graph:** Partitioned by continent, replicated within regions
- **Traffic data:** Local to each region (US traffic stays in US)

### Multi-Layer Caching
We use multiple cache layers to minimize latency:
| Layer | Location | TTL | Purpose |
| --- | --- | --- | --- |
| Browser | User device | 1 year (tiles) | Avoid repeat requests |
| CDN Edge | 200+ global POPs | 1 year (tiles), 5 min (API) | Serve from nearby |
| Redis | Each region | 1 hour (search), 5 min (routes) | Reduce DB load |
| DB Cache | PostgreSQL | Automatic | Recent query results |

With this strategy:
- 95% of tile requests served from CDN
- 70% of search requests served from Redis
- 40% of route requests served from Redis (limited by traffic freshness)

# References
- [How Google Maps Works](https://www.justinobeirne.com/google-maps-moat) - Deep analysis of Google Maps' competitive advantages
- [Web Mercator Projection](https://en.wikipedia.org/wiki/Web_Mercator_projection) - Standard projection used by web mapping services
- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/) - Comprehensive documentation on map data structures
- [S2 Geometry Library](https://s2geometry.io/) - Google's spherical geometry library for geospatial indexing
- [Vector Tiles Specification](https://github.com/mapbox/vector-tile-spec) - Mapbox Vector Tile specification

# Quiz

## Design Google Maps Quiz
For global map tile delivery at very high QPS, which approach most directly reduces origin load while keeping latency low?