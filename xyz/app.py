# app.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import google.generativeai as genai
import os
import traceback
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API key from environment or use the hardcoded one as fallback
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBphDHOScFVnG-6rOIgkXqJe3KVDYBdejs")

genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))  # Generate a random secret key for session security

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "medai_db")

def get_db_connection():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        return db
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    try:
        # Create collections if they don't exist
        db = get_db_connection()
        if db:
            # MongoDB creates collections automatically when documents are inserted
            # This is just to ensure the database exists
            collections = db.list_collection_names()
            required_collections = ["users", "medical_profiles", "conversations"]
            
            print(f"Connected to MongoDB database: {DB_NAME}")
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
        else:
            print("Failed to initialize database: couldn't establish connection")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize Gemini model
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    print(f"Error initializing default model: {str(e)}")
    try:
        model = genai.GenerativeModel('gemini-flash')
        print("Using fallback model: gemini-flash")
    except:
        print("Failed to initialize any model. Please check your API key and available models.")

# Function to check if a query is medical-related
def is_medical_query(query):
    try:
        classifier_model = genai.GenerativeModel('gemini-2.0-flash')
        classification_prompt = f"""
        Determine if the following query is related to medicine, health, medical conditions, 
        treatments, medications, health advice, or any health-related topics.

        Query: "{query}"

        Respond with only "YES" if the query is medical or health-related, and "NO" if it is not.
        """
        response = classifier_model.generate_content(classification_prompt)
        result = response.text.strip().upper()
        return "YES" in result
    except Exception as e:
        print(f"Error in query classification: {str(e)}")
        return True

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html', logged_in=True, username=session.get('username'))
    return render_template('index.html', logged_in=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Simple validation
        if not username or not password:
            flash('Username and password are required')
            return render_template('register.html')

        try:
            db = get_db_connection()
            if not db:
                flash('Error connecting to database. Please try again later.')
                return render_template('register.html')

            # Check if username or email already exists
            existing_user = None
            if email:
                existing_user = db.users.find_one({"$or": [{"username": username}, {"email": email}]})
            else:
                existing_user = db.users.find_one({"username": username})

            if existing_user:
                if existing_user.get('username') == username:
                    flash('Username already exists')
                elif email and existing_user.get('email') == email:
                    flash('Email already exists')
                return render_template('register.html')

            # Create new user
            hashed_password = generate_password_hash(password)
            new_user = {
                "username": username,
                "password": hashed_password,
                "email": email if email else None,
                "created_at": datetime.now()
            }
            
            result = db.users.insert_one(new_user)
            user_id = str(result.inserted_id)
            
            # Create empty medical profile for the user
            medical_profile = {
                "user_id": user_id,
                "age": None,
                "blood_group": None,
                "height": None,
                "weight": None,
                "allergies": None,
                "chronic_conditions": None,
                "current_medications": None,
                "previous_surgeries": None,
                "last_updated": datetime.now()
            }
            db.medical_profiles.insert_one(medical_profile)

            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required')
            return render_template('login.html')

        try:
            db = get_db_connection()
            if not db:
                flash('Error connecting to database. Please try again later.')
                return render_template('login.html')

            user = db.users.find_one({"username": username})

            if not user or not check_password_hash(user['password'], password):
                flash('Invalid username or password')
                return render_template('login.html')

            # Set session variables
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']

            return redirect(url_for('home'))

        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login. Please try again.')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db_connection()
    if not db:
        flash('Error connecting to database')
        return redirect(url_for('home'))

    user_id = session.get('user_id')
    
    if request.method == 'POST':
        try:
            # Update medical profile
            updated_profile = {
                "age": int(request.form['age']) if request.form['age'] else None,
                "blood_group": request.form['blood_group'] if request.form['blood_group'] else None,
                "height": float(request.form['height']) if request.form['height'] else None,
                "weight": float(request.form['weight']) if request.form['weight'] else None,
                "allergies": request.form['allergies'] if request.form['allergies'] else None,
                "chronic_conditions": request.form['chronic_conditions'] if request.form['chronic_conditions'] else None,
                "current_medications": request.form['current_medications'] if request.form['current_medications'] else None,
                "previous_surgeries": request.form['previous_surgeries'] if request.form['previous_surgeries'] else None,
                "last_updated": datetime.now()
            }
            
            db.medical_profiles.update_one(
                {"user_id": user_id},
                {"$set": updated_profile}
            )
            
            flash('Medical profile updated successfully')
        except Exception as e:
            print(f"Profile update error: {e}")
            flash('An error occurred while updating your profile')
    
    # Get user medical profile
    profile_data = db.medical_profiles.find_one({"user_id": user_id})
    if not profile_data:
        # Create a default profile if none exists
        profile_data = {
            "user_id": user_id,
            "age": None,
            "blood_group": None,
            "height": None,
            "weight": None,
            "allergies": None,
            "chronic_conditions": None,
            "current_medications": None,
            "previous_surgeries": None,
            "last_updated": datetime.now()
        }
        db.medical_profiles.insert_one(profile_data)
    
    # Get conversation history
    conversations = list(db.conversations.find(
        {"user_id": user_id},
        {"_id": 0, "user_message": 1, "ai_response": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(20))
    
    return render_template(
        'profile.html', 
        username=session.get('username'),
        profile=profile_data,
        conversations=conversations
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': 'Please enter a message'}), 400
    
    try:
        # Check if this is a medical query
        is_medical = is_medical_query(message)
        
        # Determine if we have a user profile to personalize responses
        user_profile = {}
        user_id = session.get('user_id')
        
        if user_id:
            db = get_db_connection()
            if db:
                profile_data = db.medical_profiles.find_one({"user_id": user_id})
                if profile_data:
                    # Convert MongoDB ObjectId to string
                    if '_id' in profile_data:
                        profile_data['_id'] = str(profile_data['_id'])
                    user_profile = profile_data
        
        # Prepare prompt with medical context and user profile if available
        prompt_prefix = ""
        
        if is_medical and user_profile:
            profile_details = []
            if user_profile.get('age'):
                profile_details.append(f"Age: {user_profile['age']}")
            if user_profile.get('blood_group'):
                profile_details.append(f"Blood Group: {user_profile['blood_group']}")
            if user_profile.get('height'):
                profile_details.append(f"Height: {user_profile['height']} cm")
            if user_profile.get('weight'):
                profile_details.append(f"Weight: {user_profile['weight']} kg")
            if user_profile.get('allergies'):
                profile_details.append(f"Allergies: {user_profile['allergies']}")
            if user_profile.get('chronic_conditions'):
                profile_details.append(f"Chronic Conditions: {user_profile['chronic_conditions']}")
            if user_profile.get('current_medications'):
                profile_details.append(f"Current Medications: {user_profile['current_medications']}")
            if user_profile.get('previous_surgeries'):
                profile_details.append(f"Previous Surgeries: {user_profile['previous_surgeries']}")
            
            if profile_details:
                prompt_prefix = "Consider the following patient information when responding:\n"
                prompt_prefix += "\n".join(profile_details)
                prompt_prefix += "\n\nNow answer the following question with this context in mind:\n"
        
        full_prompt = prompt_prefix + message
        
        # Get response from Gemini model
        response = model.generate_content(full_prompt)
        ai_response = response.text.strip()
        
        # Save conversation to DB if user is logged in
        if user_id:
            db = get_db_connection()
            if db:
                conversation = {
                    "user_id": user_id,
                    "user_message": message,
                    "ai_response": ai_response,
                    "timestamp": datetime.now()
                }
                db.conversations.insert_one(conversation)
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        print(f"Error processing chat: {e}")
        traceback.print_exc()
        return jsonify({'response': 'Sorry, there was an error processing your request. Please try again.'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
