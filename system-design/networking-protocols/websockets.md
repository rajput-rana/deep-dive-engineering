# WebSockets

**Reference:** [AlgoMaster - WebSockets](https://algomaster.io/learn/system-design/websockets)

## Summary

WebSocket is a communication protocol that provides full-duplex communication over a single TCP connection. Unlike HTTP's request-response model, WebSockets enable persistent, bidirectional communication between client and server.

## Key Concepts

### WebSocket vs HTTP

**HTTP:**
- Request-response model
- Client initiates, server responds
- Stateless
- One-way communication

**WebSocket:**
- Full-duplex communication
- Both sides can send anytime
- Stateful connection
- Bidirectional communication

### WebSocket Handshake

```
1. Client sends HTTP upgrade request
   GET /chat HTTP/1.1
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==

2. Server responds with upgrade
   HTTP/1.1 101 Switching Protocols
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=

3. Connection upgraded to WebSocket
```

## Why It Matters

**Real-Time Communication:** Enables chat, gaming, live updates without polling.

**Efficiency:** Single connection vs multiple HTTP requests.

**Low Latency:** No HTTP overhead for each message.

**Bidirectional:** Server can push data to client.

## Real-World Examples

**Chat Applications:** Slack, Discord use WebSockets for real-time messaging.

**Gaming:** Multiplayer games for real-time updates.

**Trading Platforms:** Real-time stock prices and trades.

**Collaboration Tools:** Google Docs for real-time editing.

**Notifications:** Push notifications to web clients.

## Architecture Pattern

```
┌─────────┐
│ Client  │
└────┬────┘
     │ WebSocket Connection
     ▼
┌──────────────┐
│ WebSocket    │
│   Server     │
└──────┬───────┘
       │
   ┌───┴───┬────────┐
   │       │        │
   ▼       ▼        ▼
┌────┐ ┌────┐  ┌────┐
│Msg │ │Pub │  │DB  │
│Q   │ │Sub │  │    │
└────┘ └────┘ └────┘
```

## Tradeoffs

### Advantages
- ✅ Low latency
- ✅ Efficient (single connection)
- ✅ Real-time bidirectional
- ✅ Reduced server load (vs polling)

### Disadvantages
- ❌ More complex than HTTP
- ❌ Connection management overhead
- ❌ Firewall/proxy issues
- ❌ No built-in reconnection

## Design Considerations

### When to Use WebSockets

**Good for:**
- Real-time chat
- Live updates (sports scores, stock prices)
- Collaborative editing
- Gaming
- Notifications

**Not ideal for:**
- Simple request-response
- One-time data fetch
- Stateless APIs
- RESTful services

### Connection Management

**Challenges:**
- Handle disconnections
- Reconnection logic
- Heartbeat/ping-pong
- Connection limits

**Solutions:**
- Automatic reconnection
- Heartbeat to detect dead connections
- Connection pooling
- Load balancing (sticky sessions)

### Scaling WebSockets

**Challenges:**
- Stateful connections
- Load balancer must support WebSocket
- Cross-server communication

**Solutions:**
- Sticky sessions (same server)
- Message queue for cross-server
- Redis pub/sub for broadcasting
- Horizontal scaling with session affinity

## Alternatives

### Server-Sent Events (SSE)
- One-way (server → client)
- Simpler than WebSocket
- Good for notifications

### Long Polling
- HTTP-based
- Simpler but less efficient
- Good fallback

### HTTP/2 Server Push
- HTTP/2 feature
- Limited browser support
- Not bidirectional

## Interview Hints

When discussing WebSockets:
1. Explain difference from HTTP
2. Describe handshake process
3. Discuss use cases
4. Address scaling challenges
5. Compare with alternatives (SSE, polling)

## Reference

[AlgoMaster - WebSockets](https://algomaster.io/learn/system-design/websockets)

