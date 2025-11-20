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
