from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.database import init_db, close_db
from backend.core.logging import CorrelationIdMiddleware, get_logger
from backend.schemas.common import ErrorResponse

# API Routers
from backend.api.auth import router as auth_router
from backend.api.profile import router as profile_router
from backend.api.resumes import router as resumes_router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Middlewares
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error="Internal Server Error",
            detail=str(exc) if settings.DEBUG else None
        ).model_dump()
    )

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])
app.include_router(resumes_router, prefix="/api/resumes", tags=["Resumes"])

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
