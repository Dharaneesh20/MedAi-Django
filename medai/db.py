from pymongo import MongoClient
from django.conf import settings
from datetime import datetime


def get_db_connection():
    """Get or create MongoDB connection"""
    global _mongo_client, _mongo_db
    
    if _mongo_db is None:
        try:
            _mongo_client = MongoClient(settings.MONGO_URI)
            _mongo_db = _mongo_client[settings.MONGO_DB_NAME]
            return _mongo_db
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    return _mongo_db

def init_db():
    """Initialize MongoDB collections and indexes"""
    try:
        db = get_db_connection()
        if db:
            # MongoDB creates collections automatically when documents are inserted
            collections = db.list_collection_names()
            required_collections = ["users", "medical_profiles", "conversations"]
            
            print(f"Connected to MongoDB database: {settings.MONGO_DB_NAME}")
            print(f"Available collections: {collections}")
            
            for collection in required_collections:
                if collection not in collections:
                    print(f"Collection '{collection}' will be created automatically when needed")
            
            # Create initial indexes for faster queries
            db.users.create_index("username", unique=True)
            db.users.create_index("email", unique=True, sparse=True)
            db.medical_profiles.create_index("user_id", unique=True)
            db.conversations.create_index("user_id")
            
            print("Database initialized successfully")
            return True
        else:
            print("Failed to initialize database: couldn't establish connection")
            return False
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
