from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/")
async def test_endpoint():
    """Test endpoint to verify the API is working"""
    return {
        "status": "success",
        "message": "Fintech API is running!",
        "app_name": settings.app_name,
        "env": settings.env
    }
