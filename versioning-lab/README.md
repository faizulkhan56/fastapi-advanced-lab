# Versioning Lab – v1 & v2 API Structure

This mini-project demonstrates **API versioning** in FastAPI using:

- Separate `v1` and `v2` packages
- Routers included into a central `main.py` with URL prefixes

The directory structure simulates how a real production API might evolve over time.

---

## Project Structure

```text
versioning-lab/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── myapp/
│   ├── __init__.py
│   ├── main.py
│   ├── v1/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── v2/
│       ├── __init__.py
│       └── routes.py
└── venv/          # (created by you, not included in the zip)
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
       │ (e.g., /v1/items/1)
       ▼
┌─────────────────────────────────────┐
│      FastAPI Application            │
│  ┌───────────────────────────────┐  │
│  │  Main Router                  │  │
│  │  - Route: /                   │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Version Router Selection     │  │
│  │  - /v1/* → v1.routes          │  │
│  │  - /v2/* → v2.routes          │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Versioned Route Handler      │  │
│  │  - v1/items/{item_id}         │  │
│  │  - v2/items/{item_id}         │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │ HTTP Response
               │ (versioned data)
               ▼
┌─────────────┐
│   Client    │
└─────────────┘
```

---

## Sequence Diagram

```
Client          Main Router      v1 Router      v2 Router      Route Handler
  │                  │                │              │                │
  │───GET /v1/items/1──>│                │              │                │
  │                  │                │              │                │
  │                  │───Route───────>│              │                │
  │                  │                │              │                │
  │                  │                │───GET───────>│                │
  │                  │                │              │                │
  │                  │                │              │───Process──────>│
  │                  │                │              │                │
  │                  │                │              │<──Response──────│
  │                  │                │              │                │
  │                  │                │<──Response───│                │
  │                  │                │              │                │
  │<──Response───────│<───────────────│              │                │
  │  (v1 format)     │                │              │                │
```

---

## Deployment Options

### Option 1: Uvicorn Server (Development)

#### 1. Create and activate venv

From inside `versioning-lab`:

```bash
cd versioning-lab
python3 -m venv venv
source venv/bin/activate          # On Linux/macOS

# On Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

#### 2. Install dependencies

With venv active:

```bash
pip install -r requirements.txt
```

This installs:

- `fastapi` – API framework
- `uvicorn` – ASGI server

#### 3. Run the app

From **inside `versioning-lab`** with venv active:

```bash
cd versioning-lab
source venv/bin/activate        # if not already
uvicorn myapp.main:app --reload --host 0.0.0.0 --port 8000
```

Explanation:

- `myapp.main:app`:
  - `myapp.main` – module path (`myapp/main.py`).
  - `app` – FastAPI instance defined as `app = FastAPI()`.

You should see:

```text
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### Option 2: Docker Deployment (Production-Ready)

#### 1. Build and run with Docker Compose

```bash
cd versioning-lab
docker-compose up --build
```

This will:
- Build the Docker image
- Start the container on port 8000
- Enable health checks

#### 2. Run with Docker directly

```bash
# Build the image
docker build -t versioning-lab .

# Run the container
docker run -d -p 8000:8000 --name versioning-lab versioning-lab
```

#### 3. Stop the container

```bash
# With docker-compose
docker-compose down

# With docker directly
docker stop versioning-lab
docker rm versioning-lab
```

---

## Code Overview

### 3.1 `myapp/main.py`

- Creates the main FastAPI app.
- Imports `v1` and `v2` routes.
- Includes them with prefixes `/v1` and `/v2`.
- Serves a root (`/`) endpoint that returns:
  - `available_versions`
  - `current_version`
  - `deprecated_versions`

### 3.2 `myapp/v1/routes.py`

- Defines an `APIRouter`.
- Exposes:

```http
GET /v1/items/{item_id}
```

- Returns data that marks it as **v1**.

### 3.3 `myapp/v2/routes.py`

- Similar to v1 but returns "enhanced" data.
- Exposes:

```http
GET /v2/items/{item_id}
```

---

## Testing

### Swagger UI Testing

1. Start the application (using either deployment option)
2. Navigate to: `http://localhost:8000/docs`
3. You'll see the interactive Swagger UI with:
   - `GET /` - Root endpoint (version info)
   - `GET /v1/items/{item_id}` - Version 1 endpoint
   - `GET /v2/items/{item_id}` - Version 2 endpoint
   - Try it out buttons to test directly
   - Response schemas and examples

### Postman Collection

#### Test Case 1: Root Endpoint - Version Information

**Request:**
```
GET http://localhost:8000/
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "available_versions": ["v1", "v2"],
  "current_version": "v2",
  "deprecated_versions": ["v1"]
}
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/`
3. Send request
4. Verify response contains version metadata

#### Test Case 2: Version 1 Endpoint

**Request:**
```
GET http://localhost:8000/v1/items/1
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "version": "v1",
  "item_id": 1,
  "detail": "Data from v1"
}
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/v1/items/1`
3. Try different item_id values (1, 2, 100)
4. Verify response format matches v1 schema

#### Test Case 3: Version 2 Endpoint

**Request:**
```
GET http://localhost:8000/v2/items/1
```

**Expected Response:**
- Status: `200 OK`
- Body:
```json
{
  "version": "v2",
  "item_id": 1,
  "detail": "Enhanced data from v2"
}
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/v2/items/1`
3. Try different item_id values
4. Compare response with v1 to see differences

#### Test Case 4: Version Comparison

**Test Steps:**
1. Create two requests:
   - `GET /v1/items/1`
   - `GET /v2/items/1`
2. Send both requests
3. Compare responses:
   - Both should have same `item_id`
   - `detail` field should differ
   - `version` field should match URL prefix

#### Test Case 5: Invalid Version Path

**Request:**
```
GET http://localhost:8000/v3/items/1
```

**Expected Response:**
- Status: `404 Not Found`
- Body:
```json
{
  "detail": "Not Found"
}
```

**Postman Steps:**
1. Create a GET request with invalid version
2. Verify 404 response

### cURL Commands

#### Root summary

```bash
curl http://localhost:8000/
```

Example response:

```json
{
  "available_versions": ["v1", "v2"],
  "current_version": "v2",
  "deprecated_versions": ["v1"]
}
```

#### Version 1 route

```bash
curl http://localhost:8000/v1/items/1
```

Response:

```json
{
  "version": "v1",
  "item_id": 1,
  "detail": "Data from v1"
}
```

#### Version 2 route

```bash
curl http://localhost:8000/v2/items/1
```

Response:

```json
{
  "version": "v2",
  "item_id": 1,
  "detail": "Enhanced data from v2"
}
```

---

## Concepts to Remember

- Versioning through URL prefix (e.g., `/v1`, `/v2`) is simple and explicit.
- Each version can have:
  - Its own routes.
  - Its own schemas and models.
  - Its own behavior.
- You can **deprecate** older versions while keeping them alive for legacy clients.
- Larger systems often add:
  - `v1/users.py`, `v1/orders.py`, etc.
  - `v2/users.py` with changed fields, behavior, auth, etc.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│      Versioning Lab Architecture            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │      FastAPI Application Layer        │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Main Router (myapp/main.py)    │ │ │
│  │  │  - GET /                         │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Version 1 Router              │ │ │
│  │  │  - GET /v1/items/{item_id}     │ │ │
│  │  │  - Legacy format               │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Version 2 Router              │ │ │
│  │  │  - GET /v2/items/{item_id}     │ │ │
│  │  │  - Enhanced format             │ │ │
│  │  └─────────────────────────────────┘ │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │      Uvicorn ASGI Server              │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Module Dependency Diagram

```
myapp/
├── main.py
│   ├── imports v1.routes
│   ├── imports v2.routes
│   └── includes routers with prefixes
│
├── v1/
│   └── routes.py
│       └── defines APIRouter for v1
│
└── v2/
    └── routes.py
        └── defines APIRouter for v2
```

---

Once you understand this lab, you can easily imagine adding:

- `v3` in the future.
- Different authentication rules per version.
- Different payload shapes for mobile vs web clients.
