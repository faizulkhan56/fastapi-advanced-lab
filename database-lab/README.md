# Database Lab – FastAPI + SQLAlchemy + DI + Background Tasks

This mini-project demonstrates:

- Integrating FastAPI with **SQLAlchemy ORM** (using SQLite).
- Using **Dependency Injection (DI)** to provide a database session to routes.
- Implementing full **CRUD operations** for a `Todo` model.
- Adding a **background task** example when creating a todo.

---

## Project Structure

```text
database-lab/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── data/             # (created at runtime, contains test.db)
│   └── test.db       # (SQLite database file)
└── venv/             # (created by you, not included in the zip)
```

---

## Request Flow Diagram

```
┌─────────────┐
│   Client    │
│  (Browser/  │
│  Postman)   │
└──────┬──────┘
       │ HTTP Request
       │ (e.g., POST /todos/)
       ▼
┌─────────────────────────────────────┐
│      FastAPI Application            │
│  ┌───────────────────────────────┐  │
│  │  Route Handler                │  │
│  │  - Extract request data       │  │
│  │  - Validate with Pydantic     │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Dependency Injection         │  │
│  │  - get_db() dependency        │  │
│  │  - Create DB session          │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  SQLAlchemy ORM                │  │
│  │  - Query/Insert/Update/Delete │  │
│  │  - Map to Todo model          │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  SQLite Database              │  │
│  │  - Persist data               │  │
│  │  - Return results             │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Background Tasks (optional)  │  │
│  │  - Process after response     │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │ HTTP Response
               │ (with Pydantic schema)
               ▼
┌─────────────┐
│   Client    │
└─────────────┘
```

---

## Sequence Diagram - CRUD Operations

```
Client          Route Handler      get_db()        SQLAlchemy      SQLite DB
  │                  │                 │                │              │
  │───POST /todos/───>│                 │                │              │
  │                  │                 │                │              │
  │                  │───Depends──────>│                │              │
  │                  │                 │                │              │
  │                  │                 │───Session──────>│              │
  │                  │                 │                │              │
  │                  │                 │                │───INSERT─────>│
  │                  │                 │                │              │
  │                  │                 │                │<──Result─────│
  │                  │                 │                │              │
  │                  │                 │<──Session──────│              │
  │                  │                 │                │              │
  │                  │<──Todo Object───│                │              │
  │                  │                 │                │              │
  │<──JSON Response──│                 │                │              │
  │                  │                 │                │              │
  │                  │───Close Session─>│                │              │
```

---

## Sequence Diagram - Background Task

```
Client          Route Handler      Background      DB Session      SQLite DB
  │                  │              Tasks           │                │
  │───POST /todos/   │                 │            │                │
  │   /background/──>│                 │            │                │
  │                  │                 │            │                │
  │                  │───Create Todo───>│            │                │
  │                  │                 │            │                │
  │                  │                 │───INSERT───>│                │
  │                  │                 │            │                │
  │                  │                 │<──Success───│                │
  │                  │                 │            │                │
  │                  │───Add Task──────>│            │                │
  │                  │                 │            │                │
  │<──Response───────│                 │            │                │
  │  (immediate)     │                 │            │                │
  │                  │                 │            │                │
  │                  │                 │───Process───┐                │
  │                  │                 │  (async)    │                │
  │                  │                 │<────────────┘                │
```

---

## Deployment Options

### Option 1: Uvicorn Server (Development)

#### 1. Create and activate venv

From inside `database-lab`:

```bash
cd database-lab
python3 -m venv venv
source venv/bin/activate          # On Linux/macOS

# On Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

Each FastAPI segment in this lab has **its own venv**.  
Do **not** reuse the venv from `middleware-lab` or `versioning-lab`.

#### 2. Install dependencies

With the venv active:

```bash
pip install -r requirements.txt
```

This installs:

- `fastapi` – API framework
- `uvicorn` – ASGI server
- `sqlalchemy` – ORM for database access

#### 3. Run the app

From `database-lab` with venv active:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The database file (`data/test.db`) will be created automatically on first run in the `data/` directory.

---

### Option 2: Docker Deployment (Production-Ready)

#### 1. Build and run with Docker Compose

```bash
cd database-lab
docker-compose up --build
```

This will:
- Build the Docker image
- Start the container on port 8000
- Mount the database file for persistence
- Enable health checks

#### 2. Run with Docker directly

```bash
# Build the image
docker build -t database-lab .

# Run the container with volume for database persistence
docker run -d -p 8000:8000 -v $(pwd)/test.db:/app/test.db --name database-lab database-lab
```

#### 3. Stop the container

```bash
# With docker-compose
docker-compose down

# With docker directly
docker stop database-lab
docker rm database-lab
```

**Note:** The database directory (`data/`) is persisted via volume mount, so data survives container restarts. The database file will be created at `data/test.db`.

---

## Files Overview

### 3.1 `database.py`

- Configures SQLite database URL:

  ```python
  SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
  ```

- Creates:

  - `engine` – SQLAlchemy engine.
  - `SessionLocal` – session factory.
  - `Base` – declarative base for ORM models.

### 3.2 `models.py`

- Defines a `Todo` ORM model:

  - `id`: primary key.
  - `title`: short text.
  - `description`: longer text.
  - `completed`: boolean flag.

- Mapped to table `todos`.

### 3.3 `schemas.py`

- Pydantic models for:

  - `TodoBase` – shared fields.
  - `TodoCreate` – fields needed to create a Todo.
  - `Todo` – includes `id` and enables `orm_mode` so that SQLAlchemy models can be returned directly.

### 3.4 `main.py`

- Creates FastAPI app.
- Calls `Base.metadata.create_all(bind=engine)` to create tables.
- Defines a `get_db()` dependency that:
  - Opens a DB session.
  - Yields it.
  - Closes it after use.
- Defines CRUD endpoints:
  - `POST /todos/` – create todo.
  - `GET /todos/{todo_id}` – read one.
  - `GET /todos/` – list all.
  - `PUT /todos/{todo_id}` – update.
  - `DELETE /todos/{todo_id}` – delete.
- Also defines a **background task endpoint**:
  - `POST /todos/background/` – create todo and process it asynchronously.

---

## Testing

### Swagger UI Testing

1. Start the application (using either deployment option)
2. Navigate to: `http://localhost:8000/docs`
3. You'll see the interactive Swagger UI with all CRUD endpoints:
   - `POST /todos/` – Create a new todo
   - `GET /todos/` – List all todos
   - `GET /todos/{todo_id}` – Get a specific todo
   - `PUT /todos/{todo_id}` – Update a todo
   - `DELETE /todos/{todo_id}` – Delete a todo
   - `POST /todos/background/` – Create todo with background processing
4. Use "Try it out" to test each endpoint
5. View request/response schemas

### Postman Collection

#### Test Case 1: Create a Todo

**Request:**
```
POST http://localhost:8000/todos/
Content-Type: application/json

{
  "title": "Learn FastAPI",
  "description": "Go through the advanced concepts lab",
  "completed": false
}
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "title": "Learn FastAPI",
  "description": "Go through the advanced concepts lab",
  "completed": false,
  "id": 1
}
```

**Postman Steps:**
1. Create a new POST request
2. URL: `http://localhost:8000/todos/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "title": "Learn FastAPI",
  "description": "Go through the advanced concepts lab",
  "completed": false
}
```
5. Send request
6. Save the `id` from response for next tests

#### Test Case 2: Read a Single Todo

**Request:**
```
GET http://localhost:8000/todos/1
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Go through the advanced concepts lab",
  "completed": false
}
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/todos/1` (use the id from Test Case 1)
3. Send request
4. Verify all fields match

#### Test Case 3: List All Todos

**Request:**
```
GET http://localhost:8000/todos/
```

**Expected Response:**
- Status: `200 OK`
- Body: Array of todos
```json
[
  {
    "id": 1,
    "title": "Learn FastAPI",
    "description": "Go through the advanced concepts lab",
    "completed": false
  }
]
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/todos/`
3. Send request
4. Verify array response

#### Test Case 4: Update a Todo

**Request:**
```
PUT http://localhost:8000/todos/1
Content-Type: application/json

{
  "title": "Learn FastAPI Deeply",
  "description": "Include DB, middleware, versioning, background tasks",
  "completed": true
}
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "id": 1,
  "title": "Learn FastAPI Deeply",
  "description": "Include DB, middleware, versioning, background tasks",
  "completed": true
}
```

**Postman Steps:**
1. Create a new PUT request
2. URL: `http://localhost:8000/todos/1`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON) with updated values
5. Send request
6. Verify updated fields

#### Test Case 5: Delete a Todo

**Request:**
```
DELETE http://localhost:8000/todos/1
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "detail": "Todo deleted"
}
```

**Postman Steps:**
1. Create a new DELETE request
2. URL: `http://localhost:8000/todos/1`
3. Send request
4. Verify deletion message
5. Try GET /todos/1 to verify 404

#### Test Case 6: Get Non-Existent Todo

**Request:**
```
GET http://localhost:8000/todos/999
```

**Expected Response:**
- Status: `404 Not Found`
- Body:
```json
{
  "detail": "Todo not found"
}
```

#### Test Case 7: Background Task Endpoint

**Request:**
```
POST http://localhost:8000/todos/background/
Content-Type: application/json

{
  "title": "Background Task Test",
  "description": "This will be processed in background",
  "completed": false
}
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "message": "Todo created, processing in background"
}
```

**Postman Steps:**
1. Create a new POST request
2. URL: `http://localhost:8000/todos/background/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON)
5. Send request
6. Note immediate response (background task continues)
7. Check server logs for background processing message

#### Test Case 8: Validation Error

**Request:**
```
POST http://localhost:8000/todos/
Content-Type: application/json

{
  "title": "Missing description"
}
```

**Expected Response:**
- Status: `422 Unprocessable Entity`
- Body: Validation error details

**Postman Steps:**
1. Send request with missing required fields
2. Verify validation error response

### cURL Commands

#### Create a todo

```bash
curl -X POST "http://localhost:8000/todos/" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Learn FastAPI",
        "description": "Go through the advanced concepts lab",
        "completed": false
      }'
```

Example response:

```json
{
  "title": "Learn FastAPI",
  "description": "Go through the advanced concepts lab",
  "completed": false,
  "id": 1
}
```

#### Read a todo

```bash
curl http://localhost:8000/todos/1
```

#### List todos

```bash
curl http://localhost:8000/todos/
```

#### Update a todo

```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Learn FastAPI Deeply",
        "description": "Include DB, middleware, versioning, background tasks",
        "completed": true
      }'
```

#### Delete a todo

```bash
curl -X DELETE "http://localhost:8000/todos/1"
```

---

## Background Task Endpoint

The extra endpoint:

```http
POST /todos/background/
```

- Creates a todo in the DB (just like `POST /todos/`).
- Schedules a background task that simulates a long-running process (2 seconds).
- Returns immediately with:

```json
{"message": "Todo created, processing in background"}
```

This demonstrates how to use `BackgroundTasks` in FastAPI.

---

## Concepts to Remember

- **Dependency Injection** (`Depends(get_db)`):
  - Keeps your routes clean and testable.
  - Ensures proper session cleanup.

- **SQLAlchemy ORM**:
  - Maps Python classes (`Todo`) to DB tables.
  - `Session` handles queries, inserts, updates, deletes.

- **Pydantic models**:
  - Validate incoming data.
  - Shape outgoing responses.
  - `orm_mode = True` allows returning ORM instances directly.

- **Background tasks**:
  - Good for:
    - Sending emails.
    - Logging / analytics.
    - Post-processing.
  - Run after the response is sent.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│      Database Lab Architecture              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │      FastAPI Application Layer        │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Route Handlers                 │ │ │
│  │  │  - POST /todos/                 │ │ │
│  │  │  - GET /todos/{id}              │ │ │
│  │  │  - GET /todos/                  │ │ │
│  │  │  - PUT /todos/{id}              │ │ │
│  │  │  - DELETE /todos/{id}           │ │ │
│  │  │  - POST /todos/background/      │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Dependency Injection           │ │ │
│  │  │  - get_db()                     │ │ │
│  │  │  - Session management           │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Pydantic Schemas               │ │ │
│  │  │  - TodoCreate                   │ │ │
│  │  │  - Todo                         │ │ │
│  │  │  - Validation                   │ │ │
│  │  └─────────────────────────────────┘ │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │      SQLAlchemy ORM Layer             │ │
│  │  - Todo Model                         │ │
│  │  - Session Management                 │ │
│  │  - Query Builder                      │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │      SQLite Database                  │ │
│  │  - test.db file                       │ │
│  │  - Persistent storage                  │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │      Background Tasks                  │ │
│  │  - Async processing                    │ │
│  │  - Post-response tasks                 │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Database Schema

```
┌─────────────────┐
│     todos       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ description     │
│ completed       │
└─────────────────┘
```

---

This lab gives you a realistic pattern for building data-driven FastAPI services.
