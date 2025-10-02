@echo off
echo ========================================
echo Headhunter AI Chatbot
echo ========================================
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Starting chatbot...
echo.

python run.py

pause
