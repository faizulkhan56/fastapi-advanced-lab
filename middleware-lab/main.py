from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import sys
from utils.logger import logger
from utils.exception import CustomException

app = FastAPI(title="Middleware Lab - Rate Limit & Timing")

logger.info("Middleware Lab application started")

# Global exception handler for CustomException
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    logger.error(f"CustomException raised: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": "CustomException"}
    )

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
    try:
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
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"message": "Too many requests – try again later"}
            )

        # Add the current request timestamp
        requests[client_ip].append(current_time)
        logger.info(f"Request from IP: {client_ip}, Remaining requests: {RATE_LIMIT - len(requests[client_ip])}")

        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error in rate_limit middleware: {str(e)}")
        raise CustomException(f"Rate limit middleware error: {str(e)}", sys)


# ============================
# Timing Middleware
# ============================
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request to {request.url.path} took {process_time:.6f} seconds")
        return response
    except Exception as e:
        logger.error(f"Error in timing middleware: {str(e)}")
        raise CustomException(f"Timing middleware error: {str(e)}", sys)


# ============================
# Test Route
# ============================
@app.get("/test")
async def test():
    try:
        logger.info("Test endpoint called")
        return {"message": "Request successful"}
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise CustomException(f"Test endpoint error: {str(e)}", sys)
