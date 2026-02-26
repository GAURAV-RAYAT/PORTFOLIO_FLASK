from pymongo import MongoClient
from config import Config

# Global database client
client = None
db = None

def init_db():
    """Initialize MongoDB connection"""
    global client, db
    
    try:
        if Config.MONGO_URI:
            client = MongoClient(Config.MONGO_URI)
            db = client.get_database("portfolio_db")
            print("✅ Connected to MongoDB!")
            return True
        else:
            print("⚠️ MONGO_URI not found.")
            return False
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return False

def get_db():
    """Get database instance"""
    return db

def get_client():
    """Get MongoDB client"""
    return client

def get_collection(collection_name):
    """Get a specific collection"""
    if db is not None:
        return db[collection_name]
    return None
