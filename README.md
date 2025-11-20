# FastAPI Advanced Concepts Lab

This lab project demonstrates several advanced FastAPI concepts, split into **independent mini-projects** (segments).  
Each segment has **its own code**, **its own `requirements.txt`**, and you are expected to create and use a **separate virtual environment (venv)** for each one.

## Segments

1. `middleware-lab/`  
   - Focus: **Middleware**, including:
     - Timing middleware (`X-Process-Time` header)
     - Rate limiting middleware (simple IP-based in-memory rate limit)
   - Endpoints:
     - `GET /test` – simple test endpoint to pass through middleware chain.

2. `versioning-lab/`  
   - Focus: **API Versioning** using routers:
     - `v1` and `v2` sub-packages
   - Endpoints:
     - `GET /` – root, returns available versions and metadata.
     - `GET /v1/items/{item_id}` – v1 behavior.
     - `GET /v2/items/{item_id}` – v2 behavior (enhanced data).

3. `database-lab/`  
   - Focus: **Database integration + Dependency Injection + Background Tasks**:
     - SQLite + SQLAlchemy ORM.
     - Pydantic schemas for validation & serialization.
     - CRUD operations for a `Todo` model.
     - Example of a background task when creating a todo.
   - Endpoints:
     - `POST /todos/` – create a todo.
     - `GET /todos/{todo_id}` – get one.
     - `GET /todos/` – list all.
     - `PUT /todos/{todo_id}` – update.
     - `DELETE /todos/{todo_id}` – delete.
     - `POST /todos/background/` – create todo and process it in background.

---

## Deployment Options

Each lab supports **two deployment options**:

### Option 1: Uvicorn Server (Development)

Traditional development setup with virtual environment:

```bash
cd <lab-name>
python3 -m venv venv
source venv/bin/activate          # On Linux/macOS
# On Windows (PowerShell): venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** For `versioning-lab`, use: `uvicorn myapp.main:app --reload --host 0.0.0.0 --port 8000`

### Option 2: Docker Deployment (Production-Ready)

Each lab includes `Dockerfile` and `docker-compose.yml` for containerized deployment:

```bash
cd <lab-name>
docker-compose up --build
```

This will:
- Build the Docker image
- Start the container on port 8000
- Enable health checks
- Persist data (for database-lab)

**Benefits:**
- Consistent environments across development and production
- Easy to scale and deploy
- Isolated dependencies
- Production-ready configuration

---

## Venv Strategy (IMPORTANT)

Each segment should be run in **its own venv**, e.g.:

```bash
cd middleware-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

For `versioning-lab` and `database-lab`, do the **same pattern** inside each folder.

This keeps dependencies isolated, makes it easier to experiment independently, and reflects how multiple FastAPI services might be managed in real-world environments.

---

## Documentation

Each segment has its own detailed `README.md` with:
- **Deployment instructions** (both Uvicorn and Docker)
- **Request flow diagrams**
- **Sequence diagrams**
- **Architecture diagrams**
- **Test cases** (Postman and Swagger)
- **Code explanations**

Additionally, see `medium.md` for a comprehensive blog post covering:
- Theoretical concepts
- Code explanations with references
- Flow sequence and module diagrams
- Deployment guides
- Best practices and patterns

---

## Quick Start

### Middleware Lab
```bash
# Development
cd middleware-lab && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Docker
cd middleware-lab && docker-compose up --build
```

### Versioning Lab
```bash
# Development
cd versioning-lab && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn myapp.main:app --reload

# Docker
cd versioning-lab && docker-compose up --build
```

### Database Lab
```bash
# Development
cd database-lab && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Docker
cd database-lab && docker-compose up --build
```

---

## Testing

All labs include:
- **Swagger UI**: Available at `http://localhost:8000/docs` when running
- **Postman Test Cases**: Detailed in each lab's README.md
- **cURL Examples**: Provided in each lab's README.md

---

## Project Structure

```
fastapi-advanced-lab/
├── README.md                    # This file
├── medium.md                    # Comprehensive blog post
├── middleware-lab/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── versioning-lab/
│   ├── myapp/
│   │   ├── main.py
│   │   ├── v1/routes.py
│   │   └── v2/routes.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
└── database-lab/
    ├── main.py
    ├── database.py
    ├── models.py
    ├── schemas.py
    ├── requirements.txt
    ├── Dockerfile
    ├── docker-compose.yml
    └── README.md
```

---

Read each segment's **own `README.md`** for detailed explanation and step‑by‑step instructions.
