@echo off
REM ========================================
REM AI Lifestyle Chatbot - Quick Start
REM ========================================
REM This script starts all required services
REM and opens the web application
REM ========================================

echo.
echo ========================================
echo   AI Lifestyle Chatbot - Starting...
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

echo [1/3] Starting Ollama Server...
echo.
start "Ollama Server" cmd /k "ollama serve"

REM Wait for Ollama to start
timeout /t 3 /nobreak >nul

echo [2/3] Starting Backend Server...
echo.
start "Backend Server" cmd /k "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

echo [3/3] Opening Web Browser...
echo.
start http://localhost:8000

echo.
echo ========================================
echo   SUCCESS! All services started!
echo ========================================
echo.
echo Two terminal windows have been opened:
echo   1. Ollama Server (Port 11434)
echo   2. Backend Server (Port 8000)
echo.
echo Your browser should open automatically.
echo If not, navigate to: http://localhost:8000
echo.
echo To STOP the servers:
echo   - Close both terminal windows
echo   - Or press Ctrl+C in each window
echo.
echo ========================================
echo.
pause
