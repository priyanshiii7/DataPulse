from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio

from app.config import get_settings
from app.database import init_db
from app.api import pipelines, health_checks, metrics
from app.services.health_checker import HealthCheckWorker
from app.services.cache import cache_service

settings = get_settings()

# Background task reference
health_check_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting DataPulse...")
    
    # Initialize database
    await init_db()
    
    # Connect to Redis (gracefully fails if unavailable)
    await cache_service.connect()
    
    # Start background health checker
    global health_check_task
    worker = HealthCheckWorker()
    health_check_task = asyncio.create_task(worker.run())
    
    print("DataPulse started successfully!")
    print(f"Visit: http://localhost:8000")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if health_check_task:
        health_check_task.cancel()
        try:
            await health_check_task
        except asyncio.CancelledError:
            pass

app = FastAPI(
    title=settings.APP_NAME,
    description="Real-Time Pipeline Health Monitor",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(pipelines.router, prefix="/api/pipelines", tags=["Pipelines"])
app.include_router(health_checks.router, prefix="/api/health-checks", tags=["Health Checks"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])

# Web routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/pipeline/{pipeline_id}", response_class=HTMLResponse)
async def pipeline_detail(request: Request, pipeline_id: int):
    return templates.TemplateResponse(
        "pipeline_detail.html",
        {"request": request, "pipeline_id": pipeline_id}
    )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "redis": cache_service.redis_available
    }
