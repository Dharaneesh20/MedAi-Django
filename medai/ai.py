import google.generativeai as genai
from django.conf import settings
import traceback

# Initialize Google Generative AI
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Try to initialize the model
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    print(f"Error initializing default model: {str(e)}")
    try:
        model = genai.GenerativeModel('gemini-flash')
        print("Using fallback model: gemini-flash")
    except Exception as e:
        print(f"Failed to initialize any model: {str(e)}")
        model = None

def is_medical_query(query):
    """Check if a query is medical-related"""
    try:
        classifier_model = genai.GenerativeModel('gemini-2.0-flash')
        classification_prompt = f"""
        You are a strict medical query classifier. Determine if the following query is STRICTLY related to:
        - Medicine
        - Healthcare
        - Medical conditions and symptoms
        - Treatments and procedures
        - Medications and pharmaceuticals
        - Human anatomy and physiology
        - Medical devices and equipment
        - Healthcare systems and policies
        - Public health
        - Medical education and careers
        - Medical research and clinical trials
        
        Query: "{query}"
        
        Respond with ONLY "YES" if the query is definitively medical or health-related, and "NO" if it is not.
        Be very strict - if the query could be answered by a non-medical assistant, respond with "NO".
        """
        response = classifier_model.generate_content(classification_prompt)
        result = response.text.strip().upper()
        is_medical = "YES" in result
        
        print(f"Query: '{query}' - Medical classification: {is_medical}")
        return is_medical
    except Exception as e:
        print(f"Error in query classification: {str(e)}")
        # Default to non-medical in case of classification error
        return False

def get_ai_response(message, user_profile=None):
    """Get AI response for a message, with optional user profile for context"""
    try:
        # Check if this is a medical query with the enhanced classifier
        is_medical = is_medical_query(message)
        
        # If not a medical query, respond with a polite refusal
        if not is_medical:
            return "I'm sorry, but I can only answer medical and healthcare-related questions. Please ask me something about medicine, health conditions, treatments, or other healthcare topics."
        
        # Prepare prompt with medical context and user profile if available
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
        
        if user_profile:
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
                prompt_prefix += "\n\nConsider the following patient information when responding:\n"
                prompt_prefix += "\n".join(profile_details)
                prompt_prefix += "\n\nNow answer the following question with this context in mind:\n"
        
        full_prompt = prompt_prefix + message
        
        # Add a secondary check as instruction to the model
        full_prompt += "\n\nIMPORTANT: If this question is not related to medicine or healthcare, respond only with: 'I'm sorry, but I can only answer medical and healthcare-related questions. Please ask me something about medicine, health conditions, treatments, or other healthcare topics.'"
        
        # Get response from Gemini model
        response = model.generate_content(full_prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error processing AI response: {e}")
        traceback.print_exc()
        return "Sorry, there was an error processing your request. Please try again."
