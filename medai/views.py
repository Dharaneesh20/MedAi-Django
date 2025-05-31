from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

from .forms import RegisterForm, LoginForm, MedicalProfileForm
from .db import get_db_connection
from .ai import get_ai_response, is_medical_query

def home(request):
    """Home page view"""
    context = {
        'logged_in': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None
    }
    return render(request, 'medai/index.html', context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data.get('email', '')

            try:
                # Connect to MongoDB
                db = get_db_connection()
                if not db:
                    messages.error(request, 'Error connecting to database. Please try again later.')
                    return render(request, 'medai/register.html', {'form': form})

                # Check if username or email already exists in MongoDB
                existing_user = None
                if email:
                    existing_user = db.users.find_one({"$or": [{"username": username}, {"email": email}]})
                else:
                    existing_user = db.users.find_one({"username": username})

                if existing_user:
                    if existing_user.get('username') == username:
                        messages.error(request, 'Username already exists')
                    elif email and existing_user.get('email') == email:
                        messages.error(request, 'Email already exists')
                    return render(request, 'medai/register.html', {'form': form})

                # Create user in Django auth system for session management
                User.objects.create_user(username=username, email=email, password=password)

                # Create user in MongoDB with hashed password for application data
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

                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')

            except Exception as e:
                print(f"Registration error: {e}")
                messages.error(request, 'An error occurred during registration. Please try again.')
    else:
        form = RegisterForm()
    
    return render(request, 'medai/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                # First, authenticate against Django's user system
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    return redirect('home')
                
                # If Django auth fails, check MongoDB for legacy users
                db = get_db_connection()
                if not db:
                    messages.error(request, 'Error connecting to database. Please try again later.')
                    return render(request, 'medai/login.html', {'form': form})

                mongo_user = db.users.find_one({"username": username})

                if not mongo_user or not check_password_hash(mongo_user['password'], password):
                    messages.error(request, 'Invalid username or password')
                    return render(request, 'medai/login.html', {'form': form})

                # If MongoDB auth succeeds but Django auth failed, create Django user
                try:
                    django_user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=mongo_user.get('email')
                    )
                    login(request, django_user)
                    return redirect('home')
                except:
                    messages.error(request, 'Error creating user session. Please try again.')

            except Exception as e:
                print(f"Login error: {e}")
                messages.error(request, 'An error occurred during login. Please try again.')
    else:
        form = LoginForm()
    
    return render(request, 'medai/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('home')

@login_required
def profile_view(request):
    """User profile view"""
    db = get_db_connection()
    if not db:
        messages.error(request, 'Error connecting to database')
        return redirect('home')

    # Find user ID in MongoDB
    mongo_user = db.users.find_one({"username": request.user.username})
    if not mongo_user:
        messages.error(request, 'User profile not found')
        return redirect('home')
    
    user_id = str(mongo_user['_id'])
    
    if request.method == 'POST':
        form = MedicalProfileForm(request.POST)
        if form.is_valid():
            try:
                # Update medical profile
                updated_profile = {
                    "age": form.cleaned_data['age'],
                    "blood_group": form.cleaned_data['blood_group'],
                    "height": form.cleaned_data['height'],
                    "weight": form.cleaned_data['weight'],
                    "allergies": form.cleaned_data['allergies'],
                    "chronic_conditions": form.cleaned_data['chronic_conditions'],
                    "current_medications": form.cleaned_data['current_medications'],
                    "previous_surgeries": form.cleaned_data['previous_surgeries'],
                    "last_updated": datetime.now()
                }
                
                db.medical_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": updated_profile}
                )
                
                messages.success(request, 'Medical profile updated successfully')
            except Exception as e:
                print(f"Profile update error: {e}")
                messages.error(request, 'An error occurred while updating your profile')
    else:
        form = MedicalProfileForm()
    
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
    
    # Pre-populate form with existing data
    form = MedicalProfileForm(initial={
        'age': profile_data.get('age'),
        'blood_group': profile_data.get('blood_group'),
        'height': profile_data.get('height'),
        'weight': profile_data.get('weight'),
        'allergies': profile_data.get('allergies'),
        'chronic_conditions': profile_data.get('chronic_conditions'),
        'current_medications': profile_data.get('current_medications'),
        'previous_surgeries': profile_data.get('previous_surgeries'),
    })
    
    # Get conversation history
    conversations = list(db.conversations.find(
        {"user_id": user_id},
        {"_id": 0, "user_message": 1, "ai_response": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(20))
    
    context = {
        'username': request.user.username,
        'profile': profile_data,
        'form': form,
        'conversations': conversations
    }
    
    return render(request, 'medai/profile.html', context)

@csrf_exempt
@require_POST
def chat_api(request):
    """API endpoint for chat"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'response': 'Please enter a message'}, status=400)
        
        # Check if this is a medical query
        is_medical = is_medical_query(message)
        
        # If not a medical query, respond with a polite refusal
        if not is_medical:
            non_medical_response = "I'm sorry, but I can only answer medical and healthcare-related questions. Please ask me something about medicine, health conditions, treatments, or other healthcare topics."
            
            # Save conversation to DB if user is logged in
            if request.user.is_authenticated:
                db = get_db_connection()
                if db:
                    mongo_user = db.users.find_one({"username": request.user.username})
                    if mongo_user:
                        user_id = str(mongo_user['_id'])
                        conversation = {
                            "user_id": user_id,
                            "user_message": message,
                            "ai_response": non_medical_response,
                            "timestamp": datetime.now(),
                            "query_type": "medical" if is_medical else "non_medical"
                        }
                        db.conversations.insert_one(conversation)
            
            return JsonResponse({'response': non_medical_response})
        
        # Determine if we have a user profile to personalize responses
        user_profile = None
        
        if request.user.is_authenticated:
            db = get_db_connection()
            if db:
                # Find user ID in MongoDB
                mongo_user = db.users.find_one({"username": request.user.username})
                if mongo_user:
                    user_id = str(mongo_user['_id'])
                    profile_data = db.medical_profiles.find_one({"user_id": user_id})
                    if profile_data:
                        # Convert MongoDB ObjectId to string
                        if '_id' in profile_data:
                            profile_data['_id'] = str(profile_data['_id'])
                        user_profile = profile_data
        
        # Prepare prompt with enhanced markdown instructions
        prompt_prefix = """
        You are MedAI, a medical assistant specialized in healthcare information.
        You can ONLY answer questions related to medicine, healthcare, medical conditions,
        treatments, and other health-related topics.
        
        FORMAT YOUR RESPONSE USING MARKDOWN:
        - Use **bold** for important terms, drug names, and key points
        - Use *italics* for emphasis
        - Use bullet points or numbered lists for steps or multiple items
        - Use headings with # or ## for sections if needed
        - Use tables for comparing options when relevant
        
        Your response should be well-structured, clear, and formatted for easy reading.
        Always include appropriate disclaimers about consulting healthcare professionals.
        """
        
        full_prompt = f"{prompt_prefix}\n\nUser: {message}\nAI:"
        
        # Get response from Gemini model
        ai_response = get_ai_response(message, user_profile)
        
        # Save conversation to DB if user is logged in
        if request.user.is_authenticated:
            db = get_db_connection()
            if db:
                mongo_user = db.users.find_one({"username": request.user.username})
                if mongo_user:
                    user_id = str(mongo_user['_id'])
                    conversation = {
                        "user_id": user_id,
                        "user_message": message,
                        "ai_response": ai_response,
                        "timestamp": datetime.now(),
                        "query_type": "medical" if is_medical else "non_medical"
                    }
                    db.conversations.insert_one(conversation)
        
        return JsonResponse({'response': ai_response})
        
    except Exception as e:
        print(f"Error processing chat: {e}")
        return JsonResponse(
            {'response': 'Sorry, there was an error processing your request. Please try again.'}, 
            status=500
        )
