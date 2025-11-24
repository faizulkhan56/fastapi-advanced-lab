from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .v1 import routes as v1_routes
from .v2 import routes as v2_routes
import sys
import os

# Add versioning-lab directory to path to import utils
versioning_lab_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if versioning_lab_dir not in sys.path:
    sys.path.insert(0, versioning_lab_dir)

from utils.logger import logger
from utils.exception import CustomException

app = FastAPI(
    title="Versioned API Demo",
    version="2.0.0",
    description="Simple FastAPI project with v1 and v2 routes."
)

logger.info("Versioning Lab application started")

# Global exception handler for CustomException
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    logger.error(f"CustomException raised: {str(exc)}")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": "CustomException"}
    )

# Include versioned routers
try:
    app.include_router(v1_routes.router, prefix="/v1")
    app.include_router(v2_routes.router, prefix="/v2")
    logger.info("Versioned routers included successfully")
except Exception as e:
    logger.error(f"Error including routers: {str(e)}")
    raise CustomException(f"Router inclusion error: {str(e)}", sys)


@app.get("/")
async def root():
    try:
        logger.info("Root endpoint called")
        return {
            "available_versions": ["v1", "v2"],
            "current_version": "v2",
            "deprecated_versions": ["v1"]
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise CustomException(f"Root endpoint error: {str(e)}", sys)
