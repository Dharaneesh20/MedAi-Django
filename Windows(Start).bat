@echo off
title MedAI Startup

echo =======================================
echo        MedAI Application Setup
echo =======================================

:: Change to the directory where the batch file is located
cd /d "%~dp0"

:: Set execution policy
echo Setting execution policy...
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    py -3.11 -m venv venv
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

:: Install requirements if requirements.txt exists
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Installing core dependencies...
    pip install google-generativeai
    pip install sqlparse==0.2.4
    pip install pymongo==3.12.3
    pip install djongo==1.3.6
    pip install Django==3.2.19
    pip install python-dotenv
    pip install werkzeug==2.3.7
)

:: Run migrations
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

:: Ask if user wants to create a superuser
echo.
set /p create_superuser=Do you want to create a superuser? (y/n): 
if /i "%create_superuser%"=="y" (
    echo Creating superuser...
    python manage.py createsuperuser
)

:: Start the server
echo.
echo Starting MedAI server...
python manage.py runserver

pause