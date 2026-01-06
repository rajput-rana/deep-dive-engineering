# Service Identity

Service-to-service authentication and identity management: mTLS, SPIFFE/SPIRE, and service accounts.

## Table of Contents

- **[01. mTLS (Mutual TLS)](./01-mtls.md)** - Mutual authentication for services
- **[02. SPIFFE / SPIRE](./02-spiffe-spire.md)** - Secure Production Identity Framework
- **[03. Service Accounts](./03-service-accounts.md)** - Service-to-service authentication

## Service Identity Concepts

### Why Service Identity?
- Services need to authenticate to each other
- Prevent service impersonation
- Enable secure service-to-service communication
- **Principle:** Every service has a unique identity

### mTLS (Mutual TLS)
- Both client and server authenticate
- Certificate-based authentication
- **Use Cases:** Service mesh, microservices
- **Benefits:** Strong authentication, encrypted communication

### SPIFFE / SPIRE
- **SPIFFE:** Secure Production Identity Framework for Everyone
- **SPIRE:** SPIFFE Runtime Environment
- Dynamic service identity
- Short-lived certificates
- **Use Cases:** Kubernetes, microservices

### Service Accounts
- Identity for services (not users)
- Credentials for service-to-service auth
- **Best Practice:** One service account per service
- **Rotation:** Regular credential rotation

## Best Practices

- ✅ Use mTLS for service-to-service communication
- ✅ Rotate service credentials regularly
- ✅ Use SPIFFE/SPIRE for dynamic identity
- ✅ Never share service accounts
- ✅ Monitor service identity usage

## Related Topics

- **[Authentication](../01-authentication/)** - User authentication
- **[Authorization](../02-authorization/)** - Service authorization
- **[Secrets Management](../../02-secrets-management/)** - Service credential management

