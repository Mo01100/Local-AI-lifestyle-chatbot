@echo off
REM ========================================
REM AI Lifestyle Chatbot - Stop All Services
REM ========================================

echo.
echo ========================================
echo   Stopping AI Lifestyle Chatbot...
echo ========================================
echo.

echo Stopping Backend Server...
taskkill /FI "WINDOWTITLE eq Backend Server*" /T /F 2>nul

echo Stopping Ollama Server...
taskkill /FI "WINDOWTITLE eq Ollama Server*" /T /F 2>nul

REM Also kill any Python processes running uvicorn
taskkill /IM python.exe /FI "MEMUSAGE gt 50000" /F 2>nul

echo.
echo ========================================
echo   All services stopped!
echo ========================================
echo.
pause
