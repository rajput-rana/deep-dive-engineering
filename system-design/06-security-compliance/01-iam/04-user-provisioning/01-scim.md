# 🔄 SCIM (System for Cross-domain Identity Management)

<div align="center">

**Master SCIM: automated user provisioning and identity synchronization**

[![SCIM](https://img.shields.io/badge/SCIM-Provisioning-blue?style=for-the-badge)](./)
[![Identity](https://img.shields.io/badge/Identity-Sync-green?style=for-the-badge)](./)
[![REST](https://img.shields.io/badge/REST-API-orange?style=for-the-badge)](./)

*Comprehensive guide to SCIM: protocol, implementation, and user lifecycle management*

</div>

---

## 🎯 SCIM Fundamentals

<div align="center">

### What is SCIM?

**SCIM (System for Cross-domain Identity Management) is a REST API protocol for automating user provisioning and identity synchronization between systems.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🔄 Automated Provisioning** | Create, update, delete users automatically |
| **🌐 REST API** | Standard HTTP/REST interface |
| **📊 JSON Format** | JSON-based data exchange |
| **🔄 Bidirectional Sync** | Sync users between systems |
| **🔐 Secure** | OAuth 2.0 authentication |

**Mental Model:** Think of SCIM like a universal translator for user accounts - when a user is created in one system (like Okta), SCIM automatically creates the same user in connected systems (like Slack, GitHub) without manual intervention.

</div>

---

## 📚 Core Concepts

<div align="center">

### Q1: What is SCIM and why is it used?

**A:** SCIM is a standardized protocol for automating user provisioning, deprovisioning, and synchronization between identity providers and applications.

**Why Use SCIM:**

1. **Automation:** Eliminates manual user management
2. **Consistency:** Ensures users are synchronized across systems
3. **Security:** Automatic deprovisioning when users leave
4. **Efficiency:** Reduces IT overhead
5. **Compliance:** Maintains accurate user records

**Key Benefits:**
- ✅ Automated user lifecycle management
- ✅ Reduced manual errors
- ✅ Faster onboarding/offboarding
- ✅ Consistent user data
- ✅ Security through automatic deprovisioning

---

### Q2: What is the difference between SCIM and SSO?

**A:**

| Aspect | SCIM | SSO |
|:---:|:---:|:---:|
| **Purpose** | User provisioning | Authentication |
| **When Used** | User lifecycle events | User login |
| **Operations** | Create, update, delete users | Authenticate users |
| **Protocol** | REST API | SAML, OIDC |
| **Frequency** | On-demand (user changes) | Every login |

**SCIM:**
- Manages user accounts
- Creates/updates/deletes users
- Synchronizes user attributes
- Runs when user data changes

**SSO:**
- Authenticates users
- Single sign-on experience
- Token-based authentication
- Runs when user logs in

**They Work Together:**
```
SCIM: Creates user account in application
SSO: Authenticates user to access application
```

---

### Q3: How does SCIM work?

**A:**

**SCIM Architecture:**

1. **SCIM Client (IdP):**
   - Identity Provider (Okta, Azure AD)
   - Initiates SCIM requests
   - Manages user lifecycle

2. **SCIM Server (Application):**
   - Application receiving users
   - Implements SCIM endpoints
   - Stores user data

**Flow:**
```
IdP (SCIM Client)
  ↓ (User created in IdP)
SCIM API Request
  ↓
Application (SCIM Server)
  ↓ (User created in application)
User can now SSO into application
```

**Example:**
```
1. Admin creates user in Okta
2. Okta sends SCIM POST /Users request
3. Slack receives request
4. Slack creates user account
5. User can now SSO into Slack
```

---

### Q4: What are SCIM endpoints?

**A:**

**Core SCIM Endpoints:**

| Endpoint | Method | Purpose |
|:---:|:---:|:---:|
| `/Users` | GET | List users |
| `/Users` | POST | Create user |
| `/Users/{id}` | GET | Get user |
| `/Users/{id}` | PUT | Update user (full) |
| `/Users/{id}` | PATCH | Update user (partial) |
| `/Users/{id}` | DELETE | Delete user |
| `/Groups` | GET | List groups |
| `/Groups` | POST | Create group |
| `/Groups/{id}` | PUT | Update group |
| `/Groups/{id}` | DELETE | Delete group |

**Example - Create User:**
```http
POST /scim/v2/Users HTTP/1.1
Host: api.example.com
Authorization: Bearer {token}
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "john.doe@example.com",
  "name": {
    "givenName": "John",
    "familyName": "Doe"
  },
  "emails": [{
    "value": "john.doe@example.com",
    "primary": true
  }],
  "active": true
}
```

---

### Q5: What is SCIM schema?

**A:** SCIM uses schemas to define user and group attributes.

**Core Schema:**
- `urn:ietf:params:scim:schemas:core:2.0:User` - User attributes
- `urn:ietf:params:scim:schemas:core:2.0:Group` - Group attributes

**User Schema Attributes:**

| Attribute | Type | Description |
|:---:|:---:|:---:|
| **id** | String | Unique identifier |
| **userName** | String | Username (required) |
| **name** | Object | Name object |
| **emails** | Array | Email addresses |
| **active** | Boolean | Account status |
| **meta** | Object | Metadata |

**Example:**
```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "id": "2819c223-7f76-453a-919d-413861904646",
  "userName": "john.doe@example.com",
  "name": {
    "givenName": "John",
    "familyName": "Doe",
    "formatted": "John Doe"
  },
  "emails": [{
    "value": "john.doe@example.com",
    "type": "work",
    "primary": true
  }],
  "active": true,
  "meta": {
    "resourceType": "User",
    "created": "2024-01-01T10:00:00Z",
    "lastModified": "2024-01-01T10:00:00Z"
  }
}
```

---

### Q6: What is the difference between SCIM 1.1 and SCIM 2.0?

**A:**

| Aspect | SCIM 1.1 | SCIM 2.0 |
|:---:|:---:|:---:|
| **Standard** | Draft | RFC 7642, 7643, 7644 |
| **Schema** | Different format | Standardized |
| **PATCH** | Not standard | Standard PATCH support |
| **Bulk Operations** | Limited | Full bulk support |
| **Adoption** | Less common | Widely adopted |

**SCIM 2.0 Improvements:**
- ✅ Standard PATCH operations
- ✅ Better bulk operations
- ✅ Standardized schemas
- ✅ More flexible filtering
- ✅ Better error handling

**Recommendation:** Use SCIM 2.0 for new implementations.

---

### Q7: How does SCIM handle user updates?

**A:**

**Update Methods:**

1. **PUT (Full Update):**
   - Replace entire user object
   - Must include all attributes
   - Idempotent

2. **PATCH (Partial Update):**
   - Update specific attributes
   - More efficient
   - Uses JSON Patch format

**PUT Example:**
```http
PUT /scim/v2/Users/2819c223-7f76-453a-919d-413861904646
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "id": "2819c223-7f76-453a-919d-413861904646",
  "userName": "john.doe@example.com",
  "name": {
    "givenName": "John",
    "familyName": "Smith"  // Updated
  },
  "active": false  // Updated
}
```

**PATCH Example:**
```http
PATCH /scim/v2/Users/2819c223-7f76-453a-919d-413861904646
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [{
    "op": "replace",
    "path": "name.familyName",
    "value": "Smith"
  }, {
    "op": "replace",
    "path": "active",
    "value": false
  }]
}
```

---

### Q8: How does SCIM handle user deprovisioning?

**A:**

**Deprovisioning Methods:**

1. **DELETE Request:**
   - Permanently delete user
   - Removes user account

2. **Deactivate (PATCH):**
   - Set `active: false`
   - Disable account (soft delete)

**DELETE Example:**
```http
DELETE /scim/v2/Users/2819c223-7f76-453a-919d-413861904646
Authorization: Bearer {token}
```

**Deactivate Example:**
```http
PATCH /scim/v2/Users/2819c223-7f76-453a-919d-413861904646
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [{
    "op": "replace",
    "path": "active",
    "value": false
  }]
}
```

**Best Practice:** Use soft delete (deactivate) first, then hard delete after retention period.

---

### Q9: How does SCIM handle groups?

**A:**

**Group Management:**

**Create Group:**
```http
POST /scim/v2/Groups
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
  "displayName": "Developers",
  "members": [{
    "value": "2819c223-7f76-453a-919d-413861904646",
    "$ref": "/Users/2819c223-7f76-453a-919d-413861904646"
  }]
}
```

**Update Group Membership:**
```http
PATCH /scim/v2/Groups/{groupId}
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [{
    "op": "add",
    "path": "members",
    "value": [{
      "value": "new-user-id"
    }]
  }]
}
```

---

### Q10: How is SCIM authenticated?

**A:**

**Authentication Methods:**

1. **OAuth 2.0 Bearer Token:**
   - Most common
   - Token in Authorization header
   - Short-lived tokens

2. **Basic Authentication:**
   - Username/password
   - Less secure
   - Not recommended

**OAuth 2.0 Example:**
```http
GET /scim/v2/Users
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Requirements:**
- Must be valid OAuth 2.0 token
- Issued by IdP
- Includes necessary scopes
- Short expiration time

---

### Q11: What are SCIM use cases?

**A:**

**Common Use Cases:**

1. **SaaS Applications:**
   - Automate user provisioning
   - Sync users from IdP
   - Automatic deprovisioning

2. **Enterprise SSO:**
   - Connect IdP to applications
   - Manage user lifecycle
   - Group synchronization

3. **Multi-Tenant Applications:**
   - Provision users per tenant
   - Sync tenant users
   - Manage access

4. **Directory Integration:**
   - Sync with Active Directory
   - LDAP integration
   - HR system integration

**Example Flow:**
```
HR System → IdP (Okta) → SCIM → Applications (Slack, GitHub, Salesforce)
```

---

### Q12: What are SCIM best practices?

**A:**

**Best Practices:**

1. **Idempotency:**
   - Handle duplicate requests
   - Use `id` or `userName` as unique identifier
   - Return existing user if already exists

2. **Error Handling:**
   - Return proper HTTP status codes
   - Include error details
   - Handle partial failures

3. **Security:**
   - Use OAuth 2.0 authentication
   - Validate tokens
   - Rate limiting

4. **Performance:**
   - Support pagination
   - Use PATCH for updates
   - Bulk operations for efficiency

5. **Compliance:**
   - Audit all SCIM operations
   - Log user changes
   - Maintain audit trail

**Example - Idempotent Create:**
```python
def create_user(user_data):
    # Check if user exists
    existing = get_user_by_username(user_data['userName'])
    if existing:
        return existing  # Return existing user
    
    # Create new user
    return create_new_user(user_data)
```

---

### Q13: What are common SCIM implementation challenges?

**A:**

**Challenges:**

1. **Schema Mapping:**
   - Map SCIM attributes to application fields
   - Handle custom attributes
   - Support extensions

2. **Conflict Resolution:**
   - Handle concurrent updates
   - Resolve conflicts
   - Maintain consistency

3. **Performance:**
   - Handle bulk operations
   - Optimize queries
   - Support pagination

4. **Error Handling:**
   - Partial failures
   - Retry logic
   - Error reporting

**Solutions:**
- Use standard SCIM schemas
- Implement proper error handling
- Support bulk operations
- Use async processing for large operations

---

### Q14: How to implement SCIM server?

**A:**

**Implementation Steps:**

1. **Define Endpoints:**
   - `/Users` (GET, POST)
   - `/Users/{id}` (GET, PUT, PATCH, DELETE)
   - `/Groups` (GET, POST)
   - `/Groups/{id}` (GET, PUT, PATCH, DELETE)

2. **Implement Authentication:**
   - OAuth 2.0 token validation
   - Scope checking
   - Rate limiting

3. **Handle Operations:**
   - Create user
   - Update user
   - Delete user
   - List users

4. **Schema Validation:**
   - Validate SCIM schema
   - Required fields
   - Data types

**Example - Python Flask:**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/scim/v2/Users', methods=['POST'])
def create_user():
    # Validate token
    token = request.headers.get('Authorization')
    if not validate_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Parse SCIM user
    user_data = request.json
    user = create_user_in_db(user_data)
    
    # Return SCIM response
    return jsonify({
        'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
        'id': user.id,
        'userName': user.username,
        'name': {
            'givenName': user.first_name,
            'familyName': user.last_name
        },
        'active': user.active
    }), 201
```

---

### Q15: What is the difference between SCIM and LDAP?

**A:**

| Aspect | SCIM | LDAP |
|:---:|:---:|:---:|
| **Protocol** | REST/HTTP | LDAP protocol |
| **Format** | JSON | LDAP entries |
| **Use Case** | Cloud/SaaS provisioning | Directory services |
| **Authentication** | OAuth 2.0 | LDAP bind |
| **Operations** | CRUD via REST | LDAP operations |
| **Modern** | Yes | Legacy |

**SCIM:**
- Modern REST API
- JSON format
- Cloud-native
- SaaS applications

**LDAP:**
- Directory protocol
- Enterprise directories
- On-premises
- Legacy systems

**When to Use:**

**SCIM:** Cloud applications, SaaS provisioning, modern IdPs

**LDAP:** Enterprise directories, on-premises systems, legacy integration

---

## 🎯 Advanced Topics

<div align="center">

### SCIM Patterns

**Provisioning Patterns:**
- Just-in-time provisioning
- Bulk provisioning
- Incremental sync

**Sync Patterns:**
- Push sync (IdP → App)
- Pull sync (App → IdP)
- Bidirectional sync

**Error Handling:**
- Retry logic
- Partial failures
- Conflict resolution

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **SCIM Purpose** | Automated user provisioning |
| **Protocol** | REST API with JSON |
| **Operations** | Create, Read, Update, Delete |
| **Authentication** | OAuth 2.0 Bearer tokens |
| **Use Case** | SaaS user lifecycle management |

**💡 Remember:** SCIM automates user provisioning between systems. Use SCIM 2.0, implement idempotency, handle errors gracefully, and maintain audit logs for compliance.

</div>

---

<div align="center">

**Master SCIM for automated user provisioning! 🚀**

*From protocol to implementation - comprehensive guide to SCIM.*

</div>

