@echo off
TITLE DISHA AI: Legal Metrology Online Verification System (Government of India)
color 0B

echo ======================================================================
echo   DISHA AI: Online Verification System for Weighing Instruments
echo   Department of Consumer Affairs, Government of India
echo   Ministry of Consumer Affairs, Food ^& Public Distribution
echo ======================================================================
echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python.
    pause
    exit /b 1
)

echo [2/3] Starting DISHA AI Server on http://127.0.0.1:8000 ...
echo [INFO] Interactive Swagger API Docs available at http://127.0.0.1:8000/docs
echo.

start http://127.0.0.1:8000

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
