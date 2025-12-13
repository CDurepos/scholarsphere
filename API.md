# ScholarSphere API Documentation

This document provides a comprehensive overview of all API endpoints available in the ScholarSphere backend.

**Base URL:** `/api`

---

## Table of Contents

- [Authentication](#authentication)
  - [POST /auth/register](#post-authregister)
  - [POST /auth/login](#post-authlogin)
  - [POST /auth/logout](#post-authlogout)
  - [POST /auth/refresh](#post-authrefresh)
  - [GET /auth/lookup-faculty](#get-authlookup-faculty)
  - [GET /auth/check-username](#get-authcheck-username)
  - [GET /auth/check-credentials/:faculty_id](#get-authcheck-credentialsfaculty_id)
- [Faculty](#faculty)
  - [GET /faculty](#get-faculty)
  - [POST /faculty](#post-faculty)
  - [GET /faculty/:faculty_id](#get-facultyfaculty_id)
  - [PUT /faculty/:faculty_id](#put-facultyfaculty_id)
  - [DELETE /faculty/:faculty_id](#delete-facultyfaculty_id)
  - [GET /faculty/:faculty_id/rec](#get-facultyfaculty_idrec)
  - [GET /faculty/:faculty_id/keyword](#get-facultyfaculty_idkeyword)
  - [PUT /faculty/:faculty_id/keyword](#put-facultyfaculty_idkeyword)
- [Search](#search)
  - [GET /search/faculty](#get-searchfaculty)
  - [GET /search/keyword](#get-searchkeyword)
- [Recommendations](#recommendations)
  - [GET /recommend/:faculty_id](#get-recommendfaculty_id)
  - [POST /recommend/generate](#post-recommendgenerate)
- [Institution](#institution)
  - [GET /institution/list](#get-institutionlist)
- [Rate Limited](#rate-limited)
  - [GET /rate-limit/:faculty_id/generate-keyword](#get-rate-limitfaculty_idgenerate-keyword)

---

## Authentication

Authentication endpoints handle user registration, login, session management, and token refresh. The system uses JWT access tokens (short-lived) and refresh tokens (stored in HttpOnly cookies).

### POST /auth/register

Register credentials for an existing faculty member.

**Authentication:** None required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `faculty_id` | string (UUID) | Yes | UUID of the existing faculty member |
| `username` | string | Yes | Unique username for login |
| `password` | string | Yes | Plain text password (hashed server-side via SHA-256) |

**Response:**

```json
{
  "message": "Credentials registered successfully"
}
```

**Status Codes:**
- `201` - Created successfully
- `400` - Missing required fields
- `404` - Invalid faculty_id
- `409` - Username already exists or credentials already registered

**Service Behavior:** Creates a credentials record with hashed password. After successful registration, automatically generates personalized recommendations for the new user.

---

### POST /auth/login

Authenticate with username and password.

**Authentication:** None required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | Username |
| `password` | string | Yes | Plain text password |
| `remember_me` | boolean | No | If `true`, extends session to 30 days (default: 7 days) |

**Response:**

```json
{
  "access_token": "eyJ...",
  "faculty_id": "uuid-string",
  "faculty": {
    "faculty_id": "uuid-string",
    "first_name": "John",
    "last_name": "Doe",
    "biography": "...",
    "orcid": "...",
    "google_scholar_url": "...",
    "research_gate_url": "...",
    "emails": ["john.doe@example.com"],
    "phones": ["207-555-1234"],
    "departments": ["Computer Science"],
    "titles": ["Professor"]
  }
}
```

**Cookies Set:**
- `refresh_token` (HttpOnly, Lax SameSite) - Used for token refresh

**Status Codes:**
- `200` - Login successful
- `400` - Missing required fields
- `401` - Invalid credentials
- `500` - Server error

**Service Behavior:** Validates credentials using stored procedure, fetches complete faculty data including emails, phones, departments, titles, generates JWT access token and creates a session with refresh token.

---

### POST /auth/logout

Logout by revoking the current session.

**Authentication:** None required (uses refresh token cookie)

**Request Body:** None

**Response:**

```json
{
  "message": "Logged out successfully"
}
```

**Cookies Cleared:**
- `refresh_token` - Expired immediately

**Status Codes:**
- `200` - Logout successful
- `500` - Server error

**Service Behavior:** Hashes the refresh token from the cookie, marks the session as revoked in the database, and clears the refresh token cookie.

---

### POST /auth/refresh

Refresh the access token using the refresh token cookie.

**Authentication:** Refresh token cookie required

**Request Body:** None

**Response:**

```json
{
  "access_token": "eyJ..."
}
```

**Status Codes:**
- `200` - Token refreshed successfully
- `401` - Refresh token not found or invalid/expired
- `500` - Server error

**Service Behavior:** Retrieves the refresh token from cookies, hashes it, looks up the session in the database, and generates a new JWT access token if the session is valid.

---

### GET /auth/lookup-faculty

Public endpoint for looking up faculty during signup. Allows new users to search for their existing faculty record before creating an account.

**Authentication:** None required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `first_name` | string | No | Filter by first name |
| `last_name` | string | No | Filter by last name |
| `institution` | string | No | Filter by institution |

**Response:**

```json
[
  {
    "faculty_id": "uuid-string",
    "first_name": "John",
    "last_name": "Doe",
    "department_name": "Computer Science",
    "institution_name": "University of Southern Maine",
    "signup_token": "eyJ..."
  }
]
```

Each result includes a `signup_token` (JWT) that can be used to update the faculty profile during signup before credentials are registered.

**Status Codes:**
- `200` - Success (returns array, may be empty)
- `500` - Server error

**Service Behavior:** Uses the search existing faculty service to find matching faculty members. Unlike the general search, this uses AND logic - all provided parameters must match (partial match). Generates a signup token for each result, allowing the user to claim and update their profile during registration.

---

### GET /auth/check-username

Check if a username is available for registration.

**Authentication:** None required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Username to check |

**Response:**

```json
{
  "username": "johndoe",
  "available": true
}
```

**Status Codes:**
- `200` - Success
- `400` - Username parameter missing
- `500` - Server error

**Service Behavior:** Queries the credentials table to check if the username already exists.

---

### GET /auth/check-credentials/:faculty_id

Check if credentials already exist for a faculty member.

**Authentication:** None required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `faculty_id` | string (UUID) | Faculty member's UUID |

**Response:**

```json
{
  "faculty_id": "uuid-string",
  "has_credentials": false
}
```

**Status Codes:**
- `200` - Success
- `400` - faculty_id missing
- `500` - Server error

**Service Behavior:** Queries the credentials table to check if a record exists for the given faculty_id.

---

## Faculty

Faculty endpoints handle CRUD operations for faculty member profiles and their research keywords.

### GET /faculty

List faculty members with optional filters.

**Authentication:** None required

**Status:** `501 Not Implemented`

**Response:**

```json
{
  "message": "Not implemented"
}
```

---

### POST /faculty

Create a new faculty member.

**Authentication:** None required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | Yes | Faculty member's first name |
| `last_name` | string | No | Faculty member's last name |
| `institution_name` | string | No | Name of affiliated institution |
| `emails` | string[] | No | List of email addresses |
| `phones` | string[] | No | List of phone numbers |
| `departments` | string[] | No | List of department names |
| `titles` | string[] | No | List of titles (e.g., "Professor") |
| `biography` | string | No | Faculty member's biography |
| `orcid` | string | No | ORCID identifier |
| `google_scholar_url` | string | No | Google Scholar profile URL |
| `research_gate_url` | string | No | ResearchGate profile URL |

**Response:**

```json
{
  "faculty_id": "uuid-string",
  "message": "Faculty member created successfully"
}
```

**Status Codes:**
- `201` - Created successfully
- `400` - Missing required fields
- `500` - Server error

**Service Behavior:** Generates a UUID v4 for the faculty_id, creates the faculty record, creates all associated multi-valued attributes (emails, phones, departments, titles), and handles institution relationship creation if institution_name is provided.

---

### GET /faculty/:faculty_id

Get complete faculty data by ID.

**Authentication:** None required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `faculty_id` | string (UUID) | Faculty member's UUID |

**Response:**

```json
{
  "faculty_id": "uuid-string",
  "first_name": "John",
  "last_name": "Doe",
  "biography": "...",
  "orcid": "...",
  "google_scholar_url": "...",
  "research_gate_url": "...",
  "emails": ["john.doe@example.com"],
  "phones": ["207-555-1234"],
  "departments": ["Computer Science"],
  "titles": ["Professor"],
  "institution_name": "University of Southern Maine"
}
```

**Status Codes:**
- `200` - Success
- `400` - faculty_id missing
- `404` - Faculty member not found
- `500` - Server error

**Service Behavior:** Fetches faculty base record and all related data (emails, phones, departments, titles, institution) from their respective tables.

---

### PUT /faculty/:faculty_id

Update faculty profile.

**Authentication:** Required (JWT access token OR signup token) - Can only update own profile

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `faculty_id` | string (UUID) | Faculty member's UUID |

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | No | Updated first name |
| `last_name` | string | No | Updated last name |
| `institution_name` | string | No | Updated institution name |
| `emails` | string[] | No | Replaces all existing emails |
| `phones` | string[] | No | Replaces all existing phones |
| `departments` | string[] | No | Replaces all existing departments |
| `titles` | string[] | No | Replaces all existing titles |
| `biography` | string | No | Updated biography |
| `orcid` | string | No | Updated ORCID |
| `google_scholar_url` | string | No | Updated Google Scholar URL |
| `research_gate_url` | string | No | Updated ResearchGate URL |

**Response:**

```json
{
  "faculty_id": "uuid-string",
  "message": "Faculty member updated successfully"
}
```

**Notes:**
- Accepts either a standard JWT access token (for logged-in users) or a signup token (for users during registration)
- Signup tokens are obtained from the `/auth/lookup-faculty` endpoint

**Status Codes:**
- `200` - Updated successfully
- `400` - Missing request body
- `403` - Unauthorized (trying to update another user's profile, or using signup token when credentials already exist)
- `404` - Faculty member not found
- `500` - Server error

**Service Behavior:** Updates faculty base info and uses a "replace all" strategy for multi-valued attributes (deletes all existing entries, creates new ones). After update, automatically generates new recommendations for the user. When using a signup token, verifies that no credentials exist yet for the faculty member.

---

### DELETE /faculty/:faculty_id

Delete a faculty member.

**Authentication:** TBD

**Status:** `Not Implemented` (returns null)

---

### GET /faculty/:faculty_id/rec

Get recommendations for a faculty member (alternative endpoint).

**Authentication:** TBD

**Status:** `Not Implemented` (returns null)

---

### GET /faculty/:faculty_id/keyword

Get all research keywords for a faculty member.

**Authentication:** None required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `faculty_id` | string (UUID) | Faculty member's UUID |

**Response:**

```json
["machine learning", "artificial intelligence", "data science"]
```

**Status Codes:**
- `200` - Success
- `400` - faculty_id missing
- `500` - Server error

**Service Behavior:** Queries the `faculty_researches_keyword` table to get all keywords associated with the faculty member.

---

### PUT /faculty/:faculty_id/keyword

Replace all keywords for a faculty member.

**Authentication:** Required (JWT) - Can only update own profile

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `faculty_id` | string (UUID) | Faculty member's UUID |

**Request Body:**

```json
{
  "keywords": ["machine learning", "AI", "data science"]
}
```

**Response:**

```json
{
  "message": "Keywords updated successfully"
}
```

**Status Codes:**
- `200` - Updated successfully
- `400` - Missing or invalid keywords array
- `403` - Unauthorized (trying to update another user's profile)
- `500` - Server error

**Service Behavior:** Validates and normalizes keywords (lowercase, 2-64 characters, deduped), deletes all existing keywords for the faculty member, creates new keyword associations. After update, automatically generates new recommendations.

---

## Search

Search endpoints provide faculty and keyword search functionality.

### GET /search/faculty

Search for faculty members based on various filters.

**Authentication:** Required (JWT)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | No | General search (comma-separated terms, searches across all fields) |
| `keywords` | string | No | Comma-separated keywords to filter by research interests |
| `first_name` | string | No | Filter by first name |
| `last_name` | string | No | Filter by last name |
| `department` | string | No | Filter by department |
| `institution` | string | No | Filter by institution |

**Response:**

```json
[
  {
    "faculty_id": "uuid-string",
    "first_name": "John",
    "last_name": "Doe",
    "department_name": "Computer Science",
    "institution_name": "University of Southern Maine",
    "keyword_score": 3
  }
]
```

**Status Codes:**
- `200` - Success (returns array, may be empty)
- `500` - Server error

**Service Behavior:** 
- If `query` is provided: Parses into comma-separated terms, searches across all fields for each term, returns intersection (faculty matching ALL terms).
- If specific filters provided: Uses filters directly in search query.
- If `keywords` provided: Reranks results by keyword match score (faculty with more matching keywords appear first).
- Results are limited to 50 items.

---

### GET /search/keyword

Search keywords by prefix for autocomplete.

**Authentication:** None required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search term (minimum 2 characters) |
| `limit` | integer | No | Max results (default: 10, max: 50) |

**Response:**

```json
["machine learning", "macroeconomics", "macrobiology"]
```

**Status Codes:**
- `200` - Success (returns array, may be empty)
- `500` - Server error

**Service Behavior:** Performs a prefix search on the keywords table, returns matching keyword names ordered by relevance.

---

## Recommendations

Recommendation endpoints provide personalized faculty collaboration suggestions.

### GET /recommend/:faculty_id

Get personalized recommendations for a faculty member.

**Authentication:** None required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `faculty_id` | string (UUID) | Faculty member's UUID |

**Response:**

```json
[
  {
    "faculty_id": "uuid-string",
    "first_name": "Jane",
    "last_name": "Smith",
    "biography": "...",
    "institution_name": "University of Maine",
    "department_name": "Computer Science",
    "recommendation_type": "shared_keyword",
    "recommendation_text": "Similar research interests"
  }
]
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Service Behavior:** Fetches pre-computed recommendations from the `faculty_recommended_to_faculty` table. Recommendations are generated based on:
- Similar research interests (shared keywords)
- Published in your research area
- Same department
- Works at the same institution

---

### POST /recommend/generate

Manually trigger recommendation generation for all users.

**Authentication:** None required

**Request Body:** None

**Response:**

```json
{
  "message": "Recommendations generated successfully"
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Service Behavior:** Calls the `generate_all_recommendations` stored procedure which creates/refreshes recommendations for all registered users. This is typically run by a scheduled event every 12 hours but can be triggered manually.

---

## Institution

Institution endpoints provide access to institution data.

### GET /institution/list

Get a list of all available institutions.

**Authentication:** None required

**Query Parameters:** None

**Response:**

```json
[
  {
    "name": "University of Maine",
    "street_addr": "168 College Ave",
    "city": "Orono",
    "state": "ME",
    "country": "USA",
    "zip": "04469",
    "website_url": "https://umaine.edu",
    "type": "university"
  }
]
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Service Behavior:** Loads institutions from a JSON file (`data/institutions.json`), caches the result, and returns the list sorted alphabetically by name.

---

## Rate Limited

Rate-limited endpoints that have usage restrictions to prevent abuse.

### GET /rate-limit/:faculty_id/generate-keyword

Generate research keywords for a faculty member using AI based on their biography.

**Authentication:** Required (JWT)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `faculty_id` | string (UUID) | Faculty member's UUID |

**Rate Limit:** 3 requests per hour per faculty member

**Response (Success):**

```json
{
  "keywords": ["machine learning", "neural networks", "data mining"]
}
```

**Response (Rate Limited):**

```json
{
  "error": "Rate limit exceeded. Maximum of 3 requests per hour."
}
```

**Status Codes:**
- `200` - Success
- `400` - User has no biography
- `429` - Rate limit exceeded
- `500` - Server error (includes LLM failures)

**Service Behavior:** 
1. Checks rate limit by counting recent keyword generation requests in the last hour
2. Fetches the faculty member's biography
3. Records the generation attempt in the database
4. Calls the Qwen LLM model to generate keywords from the biography
5. Returns generated keywords or rolls back the generation record on failure

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common error codes:
- `400` - Bad Request (missing or invalid parameters)
- `401` - Unauthorized (missing or invalid authentication)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (duplicate resource)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `501` - Not Implemented

---

## Authentication Flow

1. **Registration:**
   - User searches for their faculty record via `/auth/lookup-faculty`
   - User checks if credentials exist via `/auth/check-credentials/:faculty_id`
   - User checks username availability via `/auth/check-username`
   - User registers via `/auth/register`

2. **Login:**
   - User authenticates via `/auth/login`
   - Receives `access_token` in response body and `refresh_token` in HttpOnly cookie

3. **Authenticated Requests:**
   - Include `Authorization: Bearer <access_token>` header
   - Access tokens expire after a short period (configured in JWT settings)

4. **Token Refresh:**
   - When access token expires, call `/auth/refresh`
   - Uses refresh token from cookie to generate new access token

5. **Logout:**
   - Call `/auth/logout` to revoke session and clear cookies
