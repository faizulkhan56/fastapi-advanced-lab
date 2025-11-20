from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time

app = FastAPI(title="Middleware Lab - Rate Limit & Timing")

# ============================
# Rate Limiting Configuration
# ============================
requests = {}          # Stores timestamps per client IP
RATE_LIMIT = 5         # Max 5 requests
RATE_TIME = 10         # Within 10 seconds


# ============================
# Rate Limiting Middleware
# ============================
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


# ============================
# Timing Middleware
# ============================
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request to {request.url.path} took {process_time:.6f} seconds")
    return response


# ============================
# Test Route
# ============================
@app.get("/test")
async def test():
    return {"message": "Request successful"}
