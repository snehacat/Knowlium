@echo off
echo ================================================
echo    Starting Knowlium - Document Intelligence
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo.
    echo Creating .env file...
    echo GROQ_API_KEY=your_groq_api_key_here > .env
    echo.
    echo Please edit .env file and add your Groq API key
    echo Get your API key from: https://console.groq.com/keys
    echo.
    pause
    notepad .env
    echo.
    echo After saving your API key, press any key to continue...
    pause >nul
)

REM Install/update dependencies
echo Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo.

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Streamlit
    echo Try running: pip install streamlit
    pause
    exit /b 1
)

REM Run Streamlit app
echo Starting Knowlium...
echo.
echo The app will open in your browser at: http://localhost:8501
echo.
echo To stop the app: Press Ctrl+C
echo.
streamlit run app.py

pause
