"""UrbanLens FastAPI application entry point."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_v1_router, root_router
from app.core.config import settings
from app.core.exceptions import (
    UrbanLensException,
    unhandled_exception_handler,
    urbanlens_exception_handler,
)
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.db.client import MongoClientManager
from slowapi.errors import RateLimitExceeded

configure_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for graceful startup and shutdown."""
    logger.info("Starting %s v%s in %s mode...", settings.PROJECT_NAME, settings.VERSION, settings.ENVIRONMENT)
    yield
    logger.info("Shutting down %s, closing database connection...", settings.PROJECT_NAME)
    MongoClientManager.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Source-grounded urban intelligence API providing validated city datasets, multi-provider observations, and multi-agent synthesis.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register rate limiter on app state
app.state.limiter = limiter

# Enable CORS for frontend applications (Vite dev server, localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_and_request_id(request: Request, call_next):
    """Middleware assigning unique trace request ID and recording response latency."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
    return response


# Register exception handlers
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(UrbanLensException, urbanlens_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Include endpoint routers
app.include_router(root_router)
app.include_router(api_v1_router)
