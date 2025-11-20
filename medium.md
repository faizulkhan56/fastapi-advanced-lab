# Building Advanced FastAPI Applications: A Comprehensive Guide to Middleware, Versioning, and Database Integration

## Introduction

FastAPI has rapidly become one of the most popular Python web frameworks for building modern APIs. Its combination of high performance, automatic API documentation, and type safety makes it an excellent choice for production applications. In this comprehensive guide, we'll explore three critical advanced concepts: **Middleware**, **API Versioning**, and **Database Integration with Dependency Injection**.

This article provides a complete walkthrough of three independent lab projects, each demonstrating essential FastAPI patterns. By the end, you'll understand how to implement cross-cutting concerns, manage API evolution, and build data-driven applications with proper architectural patterns.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Lab 1: Middleware - Timing and Rate Limiting](#lab-1-middleware-timing-and-rate-limiting)
3. [Lab 2: API Versioning](#lab-2-api-versioning)
4. [Lab 3: Database Integration with Dependency Injection](#lab-3-database-integration-with-dependency-injection)
5. [Deployment Strategies](#deployment-strategies)
6. [Best Practices and Patterns](#best-practices-and-patterns)
7. [Conclusion](#conclusion)

---

## Project Overview

Our FastAPI Advanced Lab consists of three independent mini-projects:

1. **Middleware Lab**: Demonstrates timing middleware and IP-based rate limiting
2. **Versioning Lab**: Shows how to structure APIs with multiple versions (v1, v2)
3. **Database Lab**: Integrates SQLAlchemy ORM with dependency injection and background tasks

Each lab is self-contained with its own dependencies, making it easy to understand concepts in isolation before combining them in larger applications.

### Project Structure

```
fastapi-advanced-lab/
├── middleware-lab/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── versioning-lab/
│   ├── myapp/
│   │   ├── main.py
│   │   ├── v1/routes.py
│   │   └── v2/routes.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── database-lab/
    ├── main.py
    ├── database.py
    ├── models.py
    ├── schemas.py
    ├── requirements.txt
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Lab 1: Middleware - Timing and Rate Limiting

### Theoretical Foundation

**Middleware** in FastAPI allows you to execute code before and after request processing. It's the perfect place to implement cross-cutting concerns that apply to all or most routes, such as:

- Authentication and authorization
- Logging and monitoring
- Rate limiting
- Request/response transformation
- Error handling

FastAPI middleware follows the ASGI (Asynchronous Server Gateway Interface) standard, which means middleware functions receive a `Request` object and a `call_next` function that represents the next middleware or route handler in the chain.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Middleware Execution Flow                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Request → Rate Limit MW → Timing MW → Route Handler    │
│                                                          │
│  Response ← Rate Limit MW ← Timing MW ← Route Handler   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Code Explanation

Let's examine the middleware implementation:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time

app = FastAPI(title="Middleware Lab - Rate Limit & Timing")

# Rate limiting configuration
requests = {}          # Stores timestamps per client IP
RATE_LIMIT = 5         # Max 5 requests
RATE_TIME = 10         # Within 10 seconds
```

**Key Concepts:**

1. **In-Memory Storage**: We use a dictionary to track requests per IP. In production, you'd use Redis or a similar distributed cache.

2. **Rate Limiting Algorithm**: The sliding window approach tracks timestamps and removes old entries outside the time window.

```python
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    if client_ip not in requests:
        requests[client_ip] = []

    # Remove timestamps older than RATE_TIME seconds
    requests[client_ip] = [
        ts for ts in requests[client_ip]
        if current_time - ts < RATE_TIME
    ]

    # Check limit
    if len(requests[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"message": "Too many requests – try again later"}
        )

    # Add the current request timestamp
    requests[client_ip].append(current_time)

    response = await call_next(request)
    return response
```

**How It Works:**

1. Extract client IP from the request
2. Clean up old timestamps outside the time window
3. Check if the limit is exceeded
4. If exceeded, return 429 immediately
5. Otherwise, add current timestamp and proceed

**Timing Middleware:**

```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request to {request.url.path} took {process_time:.6f} seconds")
    return response
```

This middleware:
- Records start time before processing
- Calls the next handler (route or next middleware)
- Calculates elapsed time
- Adds a custom header to the response
- Logs the timing information

### Sequence Diagram

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
  │                  │                 │                    │<──Response───┘
  │                  │                 │                    │
  │                  │                 │<──Response─────────│
  │                  │                 │                    │
  │                  │                 │───Add Header───────│
  │                  │                 │                    │
  │<──Response───────│<────────────────│                    │
  │  (with X-Process-Time)            │                    │
```

### Testing

**Swagger UI**: Navigate to `http://localhost:8000/docs` for interactive testing.

**Postman Test Cases:**
1. Basic request: `GET /test` - Verify `X-Process-Time` header
2. Rate limiting: Send 6 requests rapidly - 6th should return 429
3. Header verification: Check response headers for timing information

### Deployment

**Option 1: Uvicorn (Development)**
```bash
cd middleware-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Option 2: Docker (Production)**
```bash
cd middleware-lab
docker-compose up --build
```

### References

- [FastAPI Middleware Documentation](https://fastapi.tiangolo.com/advanced/middleware/)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [Rate Limiting Strategies](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

---

## Lab 2: API Versioning

### Theoretical Foundation

API versioning is crucial for maintaining backward compatibility while evolving your API. There are several versioning strategies:

1. **URL Path Versioning** (what we use): `/v1/items`, `/v2/items`
2. **Header Versioning**: `Accept: application/vnd.api.v1+json`
3. **Query Parameter**: `?version=1`
4. **Subdomain**: `v1.api.example.com`

URL path versioning is the most explicit and widely understood approach.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Versioning Architecture                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Main App (myapp/main.py)                               │
│  ├── Includes v1 router with prefix /v1                 │
│  └── Includes v2 router with prefix /v2                 │
│                                                          │
│  v1/routes.py                                            │
│  └── GET /items/{item_id} → Legacy format               │
│                                                          │
│  v2/routes.py                                            │
│  └── GET /items/{item_id} → Enhanced format             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Code Explanation

**Main Application (`myapp/main.py`):**

```python
from fastapi import FastAPI
from .v1 import routes as v1_routes
from .v2 import routes as v2_routes

app = FastAPI(
    title="Versioned API Demo",
    version="2.0.0",
    description="Simple FastAPI project with v1 and v2 routes."
)

# Include versioned routers
app.include_router(v1_routes.router, prefix="/v1")
app.include_router(v2_routes.router, prefix="/v2")

@app.get("/")
async def root():
    return {
        "available_versions": ["v1", "v2"],
        "current_version": "v2",
        "deprecated_versions": ["v1"]
    }
```

**Key Concepts:**

1. **Router Inclusion**: `include_router()` adds routes from separate modules
2. **Prefix**: Each version gets its own URL prefix
3. **Version Metadata**: Root endpoint provides version information

**Version 1 Routes (`myapp/v1/routes.py`):**

```python
from fastapi import APIRouter

router = APIRouter(tags=["v1"])

@router.get("/items/{item_id}")
async def read_item_v1(item_id: int):
    return {
        "version": "v1",
        "item_id": item_id,
        "detail": "Data from v1"
    }
```

**Version 2 Routes (`myapp/v2/routes.py`):**

```python
from fastapi import APIRouter

router = APIRouter(tags=["v2"])

@router.get("/items/{item_id}")
async def read_item_v2(item_id: int):
    return {
        "version": "v2",
        "item_id": item_id,
        "detail": "Enhanced data from v2"
    }
```

### Module Dependency Diagram

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

### Request Flow

```
Client Request: GET /v1/items/1
    │
    ▼
Main Router (myapp/main.py)
    │
    ▼
Version Router Selection
    │
    ├── /v1/* → v1.routes.router
    └── /v2/* → v2.routes.router
    │
    ▼
v1/routes.py → read_item_v1()
    │
    ▼
Response: {"version": "v1", "item_id": 1, ...}
```

### Testing

**Swagger UI**: All versions appear in `/docs` with clear tags.

**Postman Test Cases:**
1. Root endpoint: `GET /` - Verify version metadata
2. V1 endpoint: `GET /v1/items/1` - Test legacy version
3. V2 endpoint: `GET /v2/items/1` - Test current version
4. Version comparison: Compare v1 vs v2 responses
5. Invalid version: `GET /v3/items/1` - Should return 404

### Deployment

**Option 1: Uvicorn (Development)**
```bash
cd versioning-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn myapp.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 2: Docker (Production)**
```bash
cd versioning-lab
docker-compose up --build
```

### Best Practices

1. **Deprecation Strategy**: Clearly mark deprecated versions
2. **Version Lifecycle**: Define support periods for each version
3. **Breaking Changes**: Only introduce breaking changes in new versions
4. **Documentation**: Document differences between versions

### References

- [FastAPI Routers Documentation](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [API Versioning Best Practices](https://restfulapi.net/versioning/)
- [Semantic Versioning](https://semver.org/)

---

## Lab 3: Database Integration with Dependency Injection

### Theoretical Foundation

**Dependency Injection (DI)** is a design pattern where dependencies are provided to a function rather than created inside it. FastAPI's `Depends()` makes DI elegant and automatic.

**Benefits:**
- Testability: Easy to mock dependencies
- Reusability: Share database sessions across routes
- Resource management: Automatic cleanup
- Separation of concerns: Business logic separate from infrastructure

**SQLAlchemy ORM** provides:
- Object-relational mapping
- Database abstraction
- Query builder
- Relationship management

**Pydantic** provides:
- Data validation
- Serialization
- Type safety
- Automatic API documentation

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│         Database Lab Architecture                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  FastAPI Routes                                         │
│  ├── Depends(get_db) → Dependency Injection            │
│  └── Uses Pydantic schemas for validation              │
│                                                          │
│  SQLAlchemy ORM                                         │
│  ├── Todo Model (models.py)                            │
│  ├── Session Management (database.py)                  │
│  └── Query Builder                                      │
│                                                          │
│  SQLite Database                                        │
│  └── test.db (persistent storage)                       │
│                                                          │
│  Background Tasks                                       │
│  └── Async processing after response                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Code Explanation

**Database Configuration (`database.py`):**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**Key Concepts:**

1. **Engine**: Manages database connections
2. **SessionLocal**: Factory for creating database sessions
3. **Base**: Base class for ORM models
4. **check_same_thread=False**: Required for SQLite with FastAPI

**ORM Model (`models.py`):**

```python
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)
```

**Pydantic Schemas (`schemas.py`):**

```python
from pydantic import BaseModel

class TodoBase(BaseModel):
    title: str
    description: str
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int

    class Config:
        orm_mode = True  # Allows conversion from ORM objects
```

**Dependency Injection (`main.py`):**

```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provides session to route
    finally:
        db.close()  # Always closes session
```

**CRUD Operations:**

```python
@app.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
```

**How It Works:**

1. Request arrives with JSON body
2. Pydantic validates data against `TodoCreate` schema
3. `Depends(get_db)` provides database session
4. Create ORM object from validated data
5. Add to session, commit, refresh
6. Return ORM object (automatically serialized via `Todo` schema)

**Background Tasks:**

```python
@app.post("/todos/background/")
def create_todo_background(
    todo: schemas.TodoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    def process_todo(todo_data: dict):
        import time
        time.sleep(2)
        print(f"Processed todo in background: {todo_data}")

    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    background_tasks.add_task(process_todo, todo.dict())
    return {"message": "Todo created, processing in background"}
```

Background tasks run **after** the response is sent, perfect for:
- Sending emails
- Logging/analytics
- Post-processing
- Cache invalidation

### Sequence Diagram - CRUD Operation

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

### Database Schema

```
┌─────────────────┐
│     todos       │
├─────────────────┤
│ id (PK)         │  INTEGER PRIMARY KEY
│ title           │  VARCHAR
│ description     │  VARCHAR
│ completed       │  BOOLEAN DEFAULT FALSE
└─────────────────┘
```

### Testing

**Swagger UI**: Full CRUD interface at `/docs`

**Postman Test Cases:**
1. Create: `POST /todos/` with JSON body
2. Read: `GET /todos/{id}` - Verify created todo
3. List: `GET /todos/` - Get all todos
4. Update: `PUT /todos/{id}` - Modify todo
5. Delete: `DELETE /todos/{id}` - Remove todo
6. Background: `POST /todos/background/` - Test async processing
7. Validation: Send invalid data - Verify 422 error
8. Not Found: `GET /todos/999` - Verify 404

### Deployment

**Option 1: Uvicorn (Development)**
```bash
cd database-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Option 2: Docker (Production)**
```bash
cd database-lab
docker-compose up --build
```

The database file is persisted via volume mount.

### References

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

## Deployment Strategies

### Development: Uvicorn with Auto-Reload

**Advantages:**
- Fast iteration
- Automatic code reloading
- Easy debugging
- Direct access to logs

**Command:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production: Docker Deployment

**Advantages:**
- Consistent environments
- Easy scaling
- Isolation
- Production-ready configuration

**Dockerfile Structure:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose Benefits:**
- Service orchestration
- Health checks
- Volume management
- Network configuration

### Production Considerations

1. **Use Production ASGI Server**: Consider Gunicorn with Uvicorn workers
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Environment Variables**: Use `.env` files for configuration
3. **Database**: Use PostgreSQL or MySQL instead of SQLite
4. **Rate Limiting**: Use Redis for distributed rate limiting
5. **Monitoring**: Add APM tools (Sentry, DataDog, etc.)
6. **Logging**: Structured logging with proper levels
7. **Security**: HTTPS, CORS configuration, authentication

---

## Best Practices and Patterns

### 1. Middleware Best Practices

- **Order Matters**: Middleware executes in registration order
- **Error Handling**: Always handle exceptions in middleware
- **Performance**: Keep middleware lightweight
- **Logging**: Log important events but avoid excessive logging

### 2. Versioning Best Practices

- **Semantic Versioning**: Follow semver principles
- **Deprecation Policy**: Give clients time to migrate
- **Documentation**: Clearly document version differences
- **Testing**: Test all versions in CI/CD

### 3. Database Best Practices

- **Connection Pooling**: Configure appropriate pool size
- **Transactions**: Use transactions for multi-step operations
- **Migrations**: Use Alembic for schema migrations
- **Indexing**: Add indexes for frequently queried fields
- **Validation**: Validate at both Pydantic and database level

### 4. Dependency Injection Patterns

- **Single Responsibility**: Each dependency should do one thing
- **Reusability**: Share dependencies across routes
- **Testing**: Make dependencies easily mockable
- **Resource Management**: Always clean up resources (sessions, connections)

### 5. Error Handling

```python
from fastapi import HTTPException

@app.get("/todos/{todo_id}")
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
```

### 6. Code Organization

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── todos.py
│   │   └── users.py
│   └── middleware/
│       ├── __init__.py
│       └── rate_limit.py
├── tests/
├── requirements.txt
└── Dockerfile
```

---

## Testing Strategies

### Unit Testing

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_todo():
    response = client.post(
        "/todos/",
        json={"title": "Test", "description": "Test desc", "completed": False}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
```

### Integration Testing

- Test database operations
- Test middleware behavior
- Test version routing
- Test error scenarios

### Postman Collections

- Organize requests by feature
- Use environment variables
- Add test scripts
- Share collections with team

---

## Performance Optimization

### 1. Database Optimization

- Use connection pooling
- Add database indexes
- Optimize queries (avoid N+1)
- Use database-level constraints

### 2. Caching Strategies

- Response caching for read-heavy endpoints
- Query result caching
- Use Redis for distributed caching

### 3. Async Operations

- Use async/await for I/O operations
- Background tasks for non-critical work
- Database connection pooling

---

## Security Considerations

### 1. Authentication & Authorization

- JWT tokens
- OAuth2
- API keys
- Role-based access control

### 2. Input Validation

- Pydantic schemas
- SQL injection prevention (SQLAlchemy handles this)
- XSS prevention
- CSRF protection

### 3. Rate Limiting

- Per-user limits
- Per-IP limits
- Distributed rate limiting
- Different limits for different endpoints

---

## Monitoring and Observability

### 1. Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

### 2. Metrics

- Request count
- Response times
- Error rates
- Database query performance

### 3. Health Checks

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## Conclusion

This comprehensive guide has covered three essential FastAPI advanced concepts:

1. **Middleware**: Implement cross-cutting concerns like rate limiting and timing
2. **API Versioning**: Manage API evolution while maintaining backward compatibility
3. **Database Integration**: Build data-driven applications with proper patterns

Each lab demonstrates production-ready patterns that you can adapt to your own projects. The combination of FastAPI's modern features, SQLAlchemy's powerful ORM, and Pydantic's validation creates a robust foundation for building scalable APIs.

### Key Takeaways

- **Middleware** provides a clean way to implement cross-cutting concerns
- **Versioning** is essential for API evolution and backward compatibility
- **Dependency Injection** makes code testable and maintainable
- **Docker** provides consistent deployment across environments
- **Testing** is crucial at all levels (unit, integration, E2E)

### Next Steps

1. Explore authentication and authorization
2. Add more complex database relationships
3. Implement caching strategies
4. Set up CI/CD pipelines
5. Add monitoring and observability
6. Scale with multiple workers and load balancing

### Resources

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

## Appendix: Complete Deployment Commands

### Middleware Lab

**Development:**
```bash
cd middleware-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Docker:**
```bash
cd middleware-lab
docker-compose up --build
```

### Versioning Lab

**Development:**
```bash
cd versioning-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn myapp.main:app --reload --host 0.0.0.0 --port 8000
```

**Docker:**
```bash
cd versioning-lab
docker-compose up --build
```

### Database Lab

**Development:**
```bash
cd database-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Docker:**
```bash
cd database-lab
docker-compose up --build
```

---

**Happy Coding! 🚀**

