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

   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **Install Dependencies (All OS):**
   ```bash
   # Install dependencies in the correct order to avoid conflicts
   pip install sqlparse==0.2.4
   pip install pymongo==3.12.3
   pip install djongo==1.3.6
   pip install Django==3.2.19
   pip install -r requirements.txt
   ```

3️⃣ **Set Up MongoDB** 🍃
   
   Make sure MongoDB is running on your system. The default connection is to localhost:27017.
   
   **Windows:**
   ```
   1. Download MongoDB Community Server from the official website
   2. Run the installer and follow the instructions
   3. Start MongoDB service:
      - Go to Services (services.msc)
      - Find "MongoDB" and start the service
      - OR from Command Prompt (Admin): net start MongoDB
   ```
   
   **macOS (with Homebrew):**
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install -y mongodb
   sudo systemctl start mongodb
   sudo systemctl enable mongodb
   ```

   **Fedora:**
   ```bash
   sudo dnf install -y mongodb mongodb-server
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

   **openSUSE:**
   ```bash
   sudo zypper install mongodb
   sudo systemctl start mongodb
   sudo systemctl enable mongodb
   ```

4️⃣ **Configure Environment Variables** 🔐
   
   Copy the `.env.example` file to `.env` and update with your own values:
   
   **Windows:**
   ```bash
   copy .env.example .env
   ```
   
   **macOS/Linux:**
   ```bash
   cp .env.example .env
   ```
   
   Then edit .env with your preferred text editor and add your Google Gemini API key.

5️⃣ **Initialize the Database** 🗃️
   
   **All Operating Systems:**
   ```bash
   python init_db.py
   python manage.py migrate
   ```

6️⃣ **Create a Superuser for Admin Access** 👑
   
   **All Operating Systems:**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin username, email, and password.

7️⃣ **Run the Application** ▶️
   
   **All Operating Systems:**
   ```bash
   python manage.py runserver
   ```

8️⃣ **Access the Chatbot** 🌐
   Open your browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```
   Admin panel is available at:
   ```
   http://127.0.0.1:8000/admin/
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

## ❓ Troubleshooting

- **MongoDB Connection Issues:** Ensure MongoDB is running and accessible at the configured address/port
- **API Key Errors:** Verify your Google Gemini API key is correctly set in the .env file
- **Dependencies Issues:** Try installing dependencies one by one as listed in the installation instructions
- **Virtual Environment Problems:** If using Python 3.10+, you may need to install the virtualenv package first

