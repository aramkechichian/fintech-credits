from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import connect_to_mongo, close_mongo_connection
from app.controllers.test_controller import router as test_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.credit_request_controller import router as credit_request_router
from app.controllers.country_rule_controller import router as country_rule_router
import logging
import time

# Configure logging FIRST, before anything else
configure_logging()

logger = logging.getLogger(__name__)
logger.info("Starting fintech-api application...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    # Initialize default country rules
    from app.core.init_country_rules import initialize_default_country_rules
    try:
        await initialize_default_country_rules()
    except Exception as e:
        logger.error(f"Error initializing country rules: {str(e)}", exc_info=True)
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

# Add CORS middleware - MUST be added before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8001",
    ],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    logger.debug(f"  Headers: {dict(request.headers)}")
    logger.debug(f"  Query params: {dict(request.query_params)}")
    
    # Log body for POST/PUT/PATCH requests (read once and store)
    body_bytes = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body_bytes = await request.body()
            if body_bytes:
                import json
                try:
                    body_json = json.loads(body_bytes.decode())
                    # Don't log passwords
                    if isinstance(body_json, dict) and "password" in body_json:
                        body_json = {**body_json, "password": "***"}
                    logger.debug(f"  Body: {body_json}")
                except:
                    logger.debug(f"  Body (raw): {body_bytes.decode()[:200]}")
        except Exception as e:
            logger.debug(f"  Could not read body: {str(e)}")
    
    # Process request
    try:
        # Recreate request with body if we read it
        if body_bytes is not None:
            async def receive():
                return {"type": "http.request", "body": body_bytes}
            request._receive = receive
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"← {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        # Log validation errors
        if response.status_code == 422:
            try:
                # Read response body to see validation errors
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                import json
                error_detail = json.loads(response_body.decode())
                logger.warning(f"  Validation error details: {json.dumps(error_detail, indent=2)}")
                # Recreate response since we consumed the iterator
                from fastapi.responses import Response
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            except Exception as e:
                logger.debug(f"  Could not read validation error body: {str(e)}")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"✗ {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.3f}s", exc_info=True)
        raise

# Include routers
app.include_router(test_router)
app.include_router(auth_router)
app.include_router(credit_request_router)
app.include_router(country_rule_router)

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "app": settings.app_name, 
        "env": settings.env,
        "mongodb_url": settings.mongodb_url.split("@")[-1] if "@" in settings.mongodb_url else settings.mongodb_url
    }
