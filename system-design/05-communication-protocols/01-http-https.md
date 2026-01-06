# HTTP/HTTPS

## Summary

HTTP (HyperText Transfer Protocol) is the foundation of web communication. HTTPS adds encryption via TLS/SSL, securing data in transit. Understanding HTTP/HTTPS is essential for API design and web system architecture.

## Key Concepts

### HTTP Methods
- **GET:** Retrieve data (idempotent, cacheable)
- **POST:** Create resource (not idempotent)
- **PUT:** Update/replace resource (idempotent)
- **PATCH:** Partial update (idempotent)
- **DELETE:** Remove resource (idempotent)

### HTTP Status Codes
- **2xx:** Success (200 OK, 201 Created)
- **3xx:** Redirection (301 Moved, 304 Not Modified)
- **4xx:** Client Error (400 Bad Request, 404 Not Found)
- **5xx:** Server Error (500 Internal Error, 503 Service Unavailable)

### HTTPS (HTTP Secure)
- Encrypts data using TLS/SSL
- Prevents man-in-the-middle attacks
- Required for sensitive data
- Uses port 443 (vs HTTP's port 80)

## Why It Matters

**Web Foundation:** All web applications use HTTP/HTTPS.

**Security:** HTTPS is mandatory for authentication, payments, personal data.

**API Design:** REST APIs are built on HTTP principles.

**Performance:** HTTP/2 and HTTP/3 improve performance significantly.

## Real-World Examples

**HTTP/2:** Used by major sites for multiplexing and header compression.

**HTTPS Everywhere:** Google ranks HTTPS sites higher, browsers mark HTTP as insecure.

**REST APIs:** Built on HTTP methods and status codes.

## Tradeoffs

**HTTP vs HTTPS:**
- HTTP: Faster, simpler
- HTTPS: Secure, required for modern web, slight overhead

**HTTP/1.1 vs HTTP/2:**
- HTTP/1.1: Simple, widely supported
- HTTP/2: Multiplexing, better performance, more complex

## Design Considerations

- Always use HTTPS in production
- Choose appropriate HTTP methods
- Return correct status codes
- Support HTTP/2 for better performance
- Handle redirects properly

## Interview Hints

When discussing HTTP/HTTPS:
1. Explain HTTP methods and when to use each
2. Discuss status codes and their meanings
3. Explain HTTPS encryption
4. Compare HTTP versions
5. Address security considerations
