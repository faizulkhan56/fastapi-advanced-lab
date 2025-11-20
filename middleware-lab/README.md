# Middleware Lab – Timing & Rate Limiting

This mini-project demonstrates two key FastAPI middleware concepts:

1. **Timing middleware** – measures how long each request takes and adds an `X-Process-Time` header.
2. **Rate limiting middleware** – simple in-memory rate limiting per client IP.

You can use this lab to understand how **global cross-cutting concerns** are implemented in FastAPI using `@app.middleware("http")`.

---

## Project Structure

```text
middleware-lab/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
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
       ▼
┌─────────────────────────────────────┐
│      FastAPI Application            │
│  ┌───────────────────────────────┐  │
│  │  Rate Limiting Middleware     │  │
│  │  - Check IP request count     │  │
│  │  - Allow/Block (429 if limit) │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Timing Middleware            │  │
│  │  - Record start time          │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Route Handler: GET /test     │  │
│  │  - Process request            │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Timing Middleware (return)   │  │
│  │  - Calculate process time     │  │
│  │  - Add X-Process-Time header  │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │ HTTP Response
               ▼
┌─────────────┐
│   Client    │
│  (with      │
│  headers)   │
└─────────────┘
```

---

## Sequence Diagram

```
Client          Rate Limit MW      Timing MW         Route Handler
  │                  │                 │                    │
  │───Request───────>│                 │                    │
  │                  │───Check IP─────>│                    │
  │                  │<──Allow─────────│                    │
  │                  │                 │                    │
  │                  │                 │───Request──────────>│
  │                  │                 │                    │
  │                  │                 │                    │───Process───┐
  │                  │                 │                    │<──Response──┘
  │                  │                 │                    │
  │                  │                 │<──Response─────────│
  │                  │                 │                    │
  │                  │                 │───Add Header───────│
  │                  │                 │                    │
  │<──Response───────│<────────────────│                    │
  │  (with X-Process-Time)            │                    │
```

---

## Deployment Options

### Option 1: Uvicorn Server (Development)

#### 1. Create and activate venv

From inside `middleware-lab`:

```bash
cd middleware-lab
python3 -m venv venv
source venv/bin/activate          # On Linux/macOS

# On Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

#### 2. Install dependencies

With the venv active:

```bash
pip install -r requirements.txt
```

This installs:

- `fastapi` – the framework
- `uvicorn` – ASGI server to run the app

#### 3. Run the app

From inside `middleware-lab` with the venv active:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- `main:app` means:
  - `main` = `main.py` module.
  - `app` = FastAPI instance defined as `app = FastAPI()`.

You should see something like:

```text
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### Option 2: Docker Deployment (Production-Ready)

#### 1. Build and run with Docker Compose

```bash
cd middleware-lab
docker-compose up --build
```

This will:
- Build the Docker image
- Start the container on port 8000
- Enable health checks

#### 2. Run with Docker directly

```bash
# Build the image
docker build -t middleware-lab .

# Run the container
docker run -d -p 8000:8000 --name middleware-lab middleware-lab
```

#### 3. Stop the container

```bash
# With docker-compose
docker-compose down

# With docker directly
docker stop middleware-lab
docker rm middleware-lab
```

---

## Code Overview (`main.py`)

Key concepts:

- A **rate limiting middleware** that:
  - Tracks timestamps of each request per `client_ip`.
  - Allows at most `RATE_LIMIT` requests within `RATE_TIME` seconds.
  - Returns HTTP `429 Too Many Requests` when exceeded.

- A **timing middleware** that:
  - Records start time before calling the next handler.
  - Calculates total processing time.
  - Adds `X-Process-Time` to the response headers.
  - Logs the path and time to the console.

- A test route:
  - `GET /test` – returns a simple JSON response.

---

## Testing

### Swagger UI Testing

1. Start the application (using either deployment option)
2. Navigate to: `http://localhost:8000/docs`
3. You'll see the interactive Swagger UI with:
   - `GET /test` endpoint
   - Try it out button to test directly
   - Response schema and examples

### Postman Collection

#### Test Case 1: Basic Request Test

**Request:**
```
GET http://localhost:8000/test
```

**Expected Response:**
- Status: `200 OK`
- Headers: `X-Process-Time: <float>`
- Body:
```json
{
  "message": "Request successful"
}
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/test`
3. Send request
4. Check response headers for `X-Process-Time`
5. Verify response body

#### Test Case 2: Rate Limiting Test

The rate limit is configured as:

```python
RATE_LIMIT = 5   # requests
RATE_TIME = 10   # seconds
```

**Request:**
```
GET http://localhost:8000/test
```

**Test Steps:**
1. Create a new GET request in Postman
2. URL: `http://localhost:8000/test`
3. Use Postman's Collection Runner or send 6 requests rapidly (within 10 seconds)
4. First 5 requests should return `200 OK`
5. 6th request should return `429 Too Many Requests`

**Expected Response (After Limit):**
- Status: `429 Too Many Requests`
- Body:
```json
{
  "message": "Too many requests – try again later"
}
```

**Postman Collection Runner:**
1. Create a collection with the GET /test request
2. Go to Collection → Run
3. Set iterations to 6
4. Set delay to 0ms
5. Run and observe rate limiting

#### Test Case 3: Timing Header Verification

**Request:**
```
GET http://localhost:8000/test
```

**Verification:**
1. Send request
2. In Postman, go to Headers tab in response
3. Verify `X-Process-Time` header exists
4. Value should be a positive float (e.g., `0.001234`)

### cURL Commands

#### Basic test

```bash
curl http://localhost:8000/test
```

Expected JSON:

```json
{"message": "Request successful"}
```

Check response headers:

```bash
curl -i http://localhost:8000/test
```

You should see `X-Process-Time` in the headers.

#### Rate limiting test

```bash
# Send 10 requests rapidly
for i in {1..10}; do curl -i http://localhost:8000/test; echo; done
```

You should start to see responses with:

- Status: `HTTP/1.1 429 Too Many Requests`
- Body:

```json
{"message": "Too many requests – try again later"}
```

---

## Concepts to Remember

- Middleware runs **before and after** your route handlers.
- The order of `@app.middleware("http")` functions in the file is the order they execute in.
- Rate limiting here is **in-memory and per-process** (good for learning, not for real production with multiple instances).
- Timing middleware is a great place to integrate logging, metrics, or APM tools.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         Middleware Lab Architecture         │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │      FastAPI Application Layer        │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Rate Limiting Middleware        │ │ │
│  │  │  - In-memory request tracking    │ │ │
│  │  │  - IP-based rate limiting        │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Timing Middleware              │ │ │
│  │  │  - Request timing               │ │ │
│  │  │  - Header injection             │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Route Handlers                 │ │ │
│  │  │  - GET /test                    │ │ │
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

Once you understand this lab, you're ready to move on to:

- `versioning-lab/` – for API versioning.
- `database-lab/` – for database integration, DI, and background tasks.
