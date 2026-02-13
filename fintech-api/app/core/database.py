from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        # Test connection
        await db.client.admin.command('ping')
        print(f"✓ Connected to MongoDB: {settings.mongodb_db_name} at {settings.mongodb_url}")
    except Exception as e:
        print(f"⚠ Warning: Could not connect to MongoDB at {settings.mongodb_url}")
        print(f"  Error: {str(e)}")
        print(f"  Please make sure MongoDB is running and MONGODB_URL is set correctly")
        # Don't raise - allow app to start but operations will fail
        db.client = None

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    if db.client is None:
        raise ConnectionError("MongoDB is not connected. Please check your MongoDB connection.")
    return db.client[settings.mongodb_db_name]
