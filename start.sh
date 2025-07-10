#!/bin/bash

# Display title and header
echo "======================================="
echo "        MedAI Application Setup"
echo "======================================="

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Create virtual environment first (emphasized as first main operation)
echo "Checking for Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Trying with python3.11..."
        python3.11 -m venv venv
    fi
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Installing core dependencies..."
    pip install google-generativeai
    pip install sqlparse==0.2.4
    pip install pymongo==3.12.3
    pip install djongo==1.3.6
    pip install Django==3.2.19
    pip install python-dotenv
    pip install werkzeug==2.3.7
fi

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Ask if user wants to create a superuser
echo
read -p "Do you want to create a superuser? (y/n): " create_superuser
if [[ "$create_superuser" == "y" || "$create_superuser" == "Y" ]]; then
    echo "Creating superuser..."
    python manage.py createsuperuser
fi

# Start the server
echo
echo "Starting MedAI server..."
python manage.py runserver

# Keep terminal open
read -p "Press Enter to exit..."
