@echo off
cd /d "%~dp0"

REM Start backend API on port 8000
start "STRIX API" cmd /k "python -m uvicorn app.api.server:app  --port 8000 --reload"

REM Start Streamlit dashboard on port 8000
start "STRIX Dashboard" cmd /k "python -m streamlit run app/dashboard/dashboard.py --server.port 8000 && start chrome http://localhost:8000"


REM Start camera / detection loop
start "STRIX Camera" cmd /k "python app\main.py"

echo.
echo STRIX services started.
echo Backend: http://127.0.0.1:8000
echo Dashboard: http://127.0.0.1:8000
pause
