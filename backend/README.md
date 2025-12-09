# ScholarSphere Backend

Written by Clayton Durepos

Flask-based REST API backend for the ScholarSphere application.

## Architecture Overview

The backend follows a **3-layer architecture** pattern to ensure separation of concerns, maintainability, and testability:

```
┌─────────────────────────────────────────┐
│         Route Layer (routes/)           │  ← HTTP requests/responses
│  - Request validation                   │
│  - Authentication/authorization         │
│  - Response formatting                  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        Service Layer (services/)        │  ← Business logic
│  - Data transformation                  │
│  - Transaction management               │
│  - Cross-entity operations              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      Database Layer (db/procedures.py)  │  ← SQL stored procedures
│  - Database operations                  │
│  - Stored procedure calls               │
│  - Result formatting                    │
└─────────────────────────────────────────┘
```

## 3-Layer Architecture

### 1. Route Layer (`app/routes/`)

**Purpose:** Handle HTTP requests and responses, request validation, and authentication.

**Responsibilities:**
- Parse and validate incoming HTTP requests
- Apply authentication/authorization decorators
- Call service layer functions
- Format and return HTTP responses
- Handle errors and return appropriate status codes

**Example:**

```python
# app/routes/faculty.py
from backend.app.services.faculty import get_faculty as get_faculty_service
from backend.app.utils.jwt import require_auth
from flask import Blueprint, request, jsonify

faculty_bp = Blueprint("faculty", __name__)

@faculty_bp.route("/<string:faculty_id>", methods=["GET"])
@require_auth()  # Authentication decorator
def get_faculty(faculty_id):
    """Get faculty by ID."""
    try:
        result = get_faculty_service(faculty_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Key Points:**
- Routes should be **thin** - minimal logic, mostly delegation
- All business logic belongs in the service layer
- Use decorators for cross-cutting concerns (auth, rate limiting)
- Always return proper HTTP status codes

### 2. Service Layer (`app/services/`)

**Purpose:** Implement business logic, manage transactions, and coordinate database operations.

**Responsibilities:**
- Implement business rules and validation
- Manage database transactions
- Coordinate multiple database operations
- Transform data between route and database layers
- Handle complex operations that span multiple entities

**Example:**

```python
# app/services/faculty.py
from backend.app.db.transaction_context import start_transaction
from backend.app.db.procedures import (
    sql_update_faculty,
    sql_create_faculty_email,
    sql_delete_faculty_email_by_faculty,
)

def update_faculty(faculty_id: str, data: dict):
    """
    Update faculty profile with transaction management.
    
    Handles updating basic fields and multi-valued attributes
    (emails, phones, departments, titles) using a "delete all, then add new" strategy.
    """
    with start_transaction() as transaction_context:
        # Update basic faculty fields
        sql_update_faculty(transaction_context, faculty_id, ...)
        
        # Handle emails: delete all, then add new
        sql_delete_faculty_email_by_faculty(transaction_context, faculty_id)
        for email in data.get("emails", []):
            sql_create_faculty_email(transaction_context, faculty_id, email)
        
        # Transaction commits automatically on success
        return {"faculty_id": faculty_id, "message": "Faculty updated successfully"}
```

**Key Points:**
- Services manage **transactions** using `start_transaction()` context manager
- Services can call multiple database functions within a single transaction
- Services handle data transformation (e.g., converting lists to individual inserts)
- Services implement business rules (e.g., validation, authorization checks)

### 3. Database Layer (`app/db/procedures.py`)

**Purpose:** Execute database operations by calling MySQL stored procedures.

**Responsibilities:**
- Call MySQL stored procedures
- Handle database connections via transaction context
- Format results from stored procedures
- Provide a Python interface to SQL stored procedures

**Example:**

```python
# app/db/procedures.py
from backend.app.db.transaction_context import TransactionContext

def sql_read_faculty(
    transaction_context: TransactionContext,
    faculty_id: str
) -> dict:
    """
    Read faculty data from the database.
    
    Args:
        transaction_context: Database transaction context
        faculty_id: UUID of the faculty member
    
    Returns:
        dict: Faculty data
    """
    cursor = transaction_context.cursor
    cursor.callproc("read_faculty", (faculty_id,))
    results = [r.fetchall() for r in cursor.stored_results()]
    return results[0][0] if results and results[0] else None
```

**Key Points:**
- Database layer functions **only** interact with the database
- All SQL logic is in MySQL stored procedures (not in Python)
- Functions use `TransactionContext` to access database connections
- Functions are **stateless** - no business logic

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration management
│   ├── routes/               # Route layer (HTTP endpoints)
│   │   ├── auth.py
│   │   ├── faculty.py
│   │   ├── search.py
│   │   └── ...
│   ├── services/             # Service layer (business logic)
│   │   ├── auth.py
│   │   ├── faculty.py
│   │   ├── search.py
│   │   └── ...
│   ├── db/                   # Database layer
│   │   ├── connection.py     # Database connection management
│   │   ├── procedures.py      # Stored procedure wrappers
│   │   └── transaction_context.py  # Transaction management
│   └── utils/                # Utility functions
│       ├── jwt.py            # JWT token management
│       └── ...
├── models/                   # ML models (optional)
├── run.py                    # Application entry point
└── requirements.txt          # Python dependencies
```

### Adding a New Endpoint

To add a new endpoint following the 3-layer architecture:

1. **Add database function** in `app/db/procedures.py`:
   ```python
   def sql_your_operation(transaction_context: TransactionContext, ...):
       cursor = transaction_context.cursor
       cursor.callproc("your_stored_procedure", (...))
       # Process results
       return results
   ```

2. **Add service function** in `app/services/your_module.py`:
   ```python
   def your_service_function(...):
       with start_transaction() as transaction_context:
           result = sql_your_operation(transaction_context, ...)
           # Add business logic
           return result
   ```

3. **Add route** in `app/routes/your_module.py`:
   ```python
   @your_bp.route("/your-endpoint", methods=["GET"])
   @require_auth()  # If authentication needed
   def your_endpoint():
       result = your_service_function(...)
       return jsonify(result), 200
   ```

### Transaction Management

All database operations should use the `start_transaction()` context manager:

```python
from backend.app.db.transaction_context import start_transaction

def your_service_function():
    with start_transaction() as transaction_context:
        # All database operations here
        sql_operation_1(transaction_context, ...)
        sql_operation_2(transaction_context, ...)
        # Transaction commits automatically on success
        # Rolls back automatically on exception
```

### Authentication

Use the `@require_auth()` decorator to protect routes:

```python
from backend.app.utils.jwt import require_auth

@faculty_bp.route("/<string:faculty_id>", methods=["PUT"])
@require_auth(allow_signup=True)  # Optional: allow signup tokens
def update_faculty(faculty_id):
    # Access authenticated user via Flask's g object
    if g.faculty_id != faculty_id:
        return jsonify({"error": "Unauthorized"}), 403
    # ...
```

## Notes

- **Stored Procedures:** All database operations use MySQL stored procedures. SQL logic is not in Python code.
- **Transactions:** Always use `start_transaction()` context manager in service layer functions.
- **Error Handling:** Routes should catch exceptions and return appropriate HTTP status codes.
- **Authentication:** Most endpoints require authentication via JWT access tokens stored in the `Authorization` header.
