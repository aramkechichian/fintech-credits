"""
Initialize default admin user on application startup
"""
import logging
from app.models.user import UserInDB
from app.repositories.user_repository import user_repository
from app.services.auth_service import get_password_hash
from datetime import datetime

logger = logging.getLogger(__name__)


async def initialize_admin_user():
    """Initialize default admin user if it doesn't exist"""
    logger.info("Initializing default admin user...")
    
    admin_email = "admin@admin.com"
    admin_password = "admin"
    admin_name = "Administrator"
    
    try:
        # Check if admin user already exists
        existing_user = await user_repository.get_by_email(admin_email)
        
        if existing_user:
            logger.info("Admin user already exists, skipping...")
            return
        
        # Create admin user with hashed password
        hashed_password = get_password_hash(admin_password)
        admin_user = UserInDB(
            email=admin_email,
            full_name=admin_name,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        # Save to database
        await user_repository.create(admin_user)
        logger.info("Default admin user created successfully (email: admin@admin.com, password: admin)")
        
    except Exception as e:
        logger.error(f"Error initializing admin user: {str(e)}", exc_info=True)
