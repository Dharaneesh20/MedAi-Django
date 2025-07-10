# 🏥 Med AI Chat Application 💬

A Django-based chatbot application powered by Google's Gemini API to provide reliable medical information. It includes **user authentication**, **secure medical profile storage**, and **conversation history tracking** using **MongoDB**.

## 🚀 Features

✅ **User Authentication** 🔒 – Secure login & registration  
✅ **Medical Profile Storage** 📋 – Age, blood group, medical history, etc.  
✅ **Conversation History** 🗂️ – Tracks & stores chat interactions  
✅ **Personalized Responses** 🎯 – Tailored answers based on user profile  
✅ **Mobile-Friendly UI** 📱 – Optimized for easy access anywhere  
✅ **MongoDB Integration** 🍃 – Scalable, document-based database storage

## 🛠️ Setup Instructions

### 📝 Prerequisites

🔹 **Python 3.8+**  
🔹 **MongoDB** (installed locally or accessible via connection string)  
🔹 **Google Gemini API Key** 🔑  

### ⚙️ Installation

1️⃣ **Clone the Repository** 🔄  
   ```bash
   git clone https://github.com/yourusername/medai-chat.git
   cd medai-chat
   ```

2️⃣ **Create a Virtual Environment and Install Dependencies** 📦
   ```bash
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies in the correct order to avoid conflicts
   pip install sqlparse==0.2.4
   pip install pymongo==3.12.3
   pip install djongo==1.3.6
   pip install Django==3.2.19
   pip install -r requirements.txt
   ```

3️⃣ **Set Up MongoDB** 🍃
   
   Make sure MongoDB is running on your system. The default connection is to localhost:27017.
   
   For Ubuntu/Debian:
   ```bash
   sudo systemctl start mongodb
   ```
   
   For macOS (with Homebrew):
   ```bash
   brew services start mongodb-community
   ```
   
   For Windows, start the MongoDB service from Services.

4️⃣ **Configure Environment Variables** 🔐
   
   Copy the `.env.example` file to `.env` and update with your own values:
   ```bash
   cp .env.example .env
   # Then edit .env with your preferred text editor
   ```

5️⃣ **Initialize the Database** 🗃️
   ```bash
   python init_db.py
   python manage.py migrate
   ```

6️⃣ **Create a Superuser for Admin Access** 👑
   ```bash
   python manage.py createsuperuser
   ```

7️⃣ **Run the Application** ▶️
   ```bash
   python manage.py runserver
   ```

8️⃣ **Access the Chatbot** 🌐
   ```
   http://127.0.0.1:8000/
   ```

## 📁 Project Structure

- 📂 **manage.py** – Django management script
- 📂 **medai_project/** – Django project settings
- 📂 **medai/** – Main Django application
- 📂 **init_db.py** – MongoDB initialization script
- 📂 **.env** – Environment variables configuration
- 📂 **requirements.txt** – Python dependencies
- 📂 **templates/medai/** – HTML files for UI
  - 🔹 **index.html** – Chat interface 💬
  - 🔹 **login.html** – User login page 🔑
  - 🔹 **register.html** – User registration form 📝
  - 🔹 **profile.html** – Medical data form 📋

## 🏃‍♂️ Usage

1️⃣ **Register/Login** 🔑  
2️⃣ **Complete Medical Profile** 📋  
3️⃣ **Start Chatting** 💬  
4️⃣ **Get AI-Driven Medical Answers** 🤖  
5️⃣ **Review Saved Conversations** 📂  

## 🔐 Security Notes

⚠️ API Key should be stored securely in the .env file  
⚠️ MongoDB should be properly secured in production environments  
⚠️ Passwords are hashed using Django's authentication system  
⚠️ Add additional security layers for production use 🛡️

## 📊 MongoDB Collections

The application uses three MongoDB collections:

1. **users** – Stores user account information
   - _id: ObjectId (automatically generated)
   - username: String (unique)
   - password: String (hashed)
   - email: String (optional, unique)
   - created_at: DateTime

2. **medical_profiles** – Stores user medical information
   - _id: ObjectId (automatically generated)
   - user_id: String (links to users collection)
   - age: Integer (optional)
   - blood_group: String (optional)
   - height: Float (optional, in cm)
   - weight: Float (optional, in kg)
   - allergies: String (optional)
   - chronic_conditions: String (optional)
   - current_medications: String (optional)
   - previous_surgeries: String (optional)
   - last_updated: DateTime

3. **conversations** – Stores chat history
   - _id: ObjectId (automatically generated)
   - user_id: String (links to users collection)
   - user_message: String
   - ai_response: String
   - timestamp: DateTime
   - query_type: String (medical or non_medical)

---

Developed with ❤️ using Django, MongoDB, and Google Gemini API
