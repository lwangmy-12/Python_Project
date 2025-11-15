from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import bridge, stats

app = FastAPI(title="PA Bridge Analysis API", version="0.1.0")

# CORS SETTINGS (for frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROOT ROUTE

@app.get("/")
def root():
    """Welcome endpoint that redirects to API documentation."""
    return {
        "message": "PA Bridge Analysis API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "redoc": "/redoc"
    }

# ROUTERS

app.include_router(
    bridge.router,
    prefix="/api/bridges",
    tags=["bridges"]
)

app.include_router(
    stats.router,
    prefix="/api/stats",
    tags=["stats"]
)

@app.get("/api/bridge/{id}")
def get_bridge_legacy(id: str, year: int = None):
    """Legacy endpoint: same as /api/bridges/{id}"""
    return bridge.get_bridge(id, year)
