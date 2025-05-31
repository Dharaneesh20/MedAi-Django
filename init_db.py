#!/usr/bin/env python3
# init_db.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "medai_db")

def setup_mongodb():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        print(f"Connected to MongoDB database: {DB_NAME}")
        
        # Create collections
        db.users.create_index("username", unique=True)
        db.users.create_index("email", unique=True, sparse=True)
        db.medical_profiles.create_index("user_id", unique=True)
        db.conversations.create_index("user_id")
        
        print("Database collections and indexes created successfully.")
        
        # Optional: Add a test user (uncomment if needed)
        """
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        # Check if test user exists
        test_user = db.users.find_one({"username": "test_user"})
        
        if not test_user:
            # Create test user
            user_data = {
                "username": "test_user",
                "password": generate_password_hash("password123"),
                "email": "test@example.com",
                "created_at": datetime.now()
            }
            
            result = db.users.insert_one(user_data)
            user_id = str(result.inserted_id)
            
            # Create empty medical profile for test user
            profile_data = {
                "user_id": user_id,
                "age": 30,
                "blood_group": "O+",
                "height": 175.0,
                "weight": 70.0,
                "allergies": "None",
                "chronic_conditions": "None",
                "current_medications": "None",
                "previous_surgeries": "None",
                "last_updated": datetime.now()
            }
            
            db.medical_profiles.insert_one(profile_data)
            print("Test user created successfully.")
        else:
            print("Test user already exists.")
        """
        
        return True
    
    except Exception as e:
        print(f"Error setting up MongoDB: {e}")
        return False

if __name__ == "__main__":
    if setup_mongodb():
        print("MongoDB setup completed successfully.")
    else:
        print("MongoDB setup failed.")
