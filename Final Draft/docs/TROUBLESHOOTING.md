#  Troubleshooting Guide - Connection Refused Error

## Problem: ERR_CONNECTION_REFUSED

If you see "localhost refused to connect" or "ERR_CONNECTION_REFUSED", the backend server failed to start.

---

## ✅ Step-by-Step Fix

### Step 1: Check if Ollama is Running

```powershell
# Check if Ollama is running
netstat -ano | findstr :11434
```

**If nothing appears:**
```powershell
# Start Ollama manually
ollama serve
```

Keep this terminal window open!

---

### Step 2: Start Backend Server Manually

Open a **NEW** terminal in your project folder and run:

```powershell
# Method 1: Using uvicorn directly (RECOMMENDED)
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**OR if that doesn't work:**

```powershell
# Method 2: Using Python directly
python backend/main.py
```

---

### Step 3: Check for Errors

Look for these common errors:

#### Error: "ModuleNotFoundError"
**Solution:** Install dependencies
```powershell
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

#### Error: "Port 8000 is already in use"
**Solution:** Kill the process using port 8000
```powershell
# Find the process
netstat -ano | findstr :8000

# Kill it (replace PID with the number from above)
taskkill /PID <PID> /F
```

#### Error: "Ollama connection failed"
**Solution:** Make sure Ollama is running
```powershell
ollama serve
```

---

### Step 4: Verify Backend is Running

Once the backend starts, you should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Database initialized at: data\app.db
✓ Backend server started
✓ API documentation: http://localhost:8000/docs
INFO:     Application startup complete.
```

---

### Step 5: Test the Connection

Open your browser and go to:
- **Main App:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## Quick Manual Start (Always Works)

If the batch file isn't working, use this manual method:

### Terminal 1: Start Ollama
```powershell
ollama serve
```

### Terminal 2: Start Backend
```powershell
cd "c:\Users\Mohamed Metwaly\Downloads\Final Draft"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Browser: Open App
Navigate to: http://localhost:8000

---

##  Diagnostic Commands

Run these to diagnose issues:

```powershell
# Check Python version (need 3.8+)
python --version

# Check if Ollama is installed
ollama --version

# Check if Llama model is downloaded
ollama list

# Check if required packages are installed
pip list | findstr fastapi
pip list | findstr uvicorn
pip list | findstr sqlalchemy

# Check what's using port 8000
netstat -ano | findstr :8000

# Check what's using port 11434 (Ollama)
netstat -ano | findstr :11434
```

---

##  Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Python not found" | Install Python 3.8+ and add to PATH |
| "Ollama not found" | Install Ollama from https://ollama.ai |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Port already in use" | Kill the process or use a different port |
| "Database error" | Delete `data/app.db` and restart |
| "Llama model not found" | Run `ollama pull llama3.2` |

---

##  Updated Batch File

I've fixed the batch file. The issue was with the backend startup command.

**Old (broken):**
```batch
cd backend && python -m uvicorn main:app ...
```

**New (fixed):**
```batch
python -m uvicorn backend.main:app ...
```

Try running `start_chatbot.bat` again!

---

## ✅ Verification Checklist

Before running the batch file, make sure:

- [ ] Python 3.8+ is installed
- [ ] Ollama is installed
- [ ] Llama 3.2 model is downloaded (`ollama pull llama3.2`)
- [ ] Dependencies are installed (`pip install -r requirements.txt`)
- [ ] Backend dependencies are installed (`pip install -r backend/requirements.txt`)
- [ ] Port 8000 is not in use
- [ ] Port 11434 is not in use

---

##  Still Not Working?

If you're still having issues, run this diagnostic script:

```powershell
# Save this as diagnose.ps1 and run it
Write-Host "=== System Diagnostic ===" -ForegroundColor Cyan

Write-Host "`nPython Version:" -ForegroundColor Yellow
python --version

Write-Host "`nOllama Version:" -ForegroundColor Yellow
ollama --version

Write-Host "`nOllama Models:" -ForegroundColor Yellow
ollama list

Write-Host "`nPort 8000 Status:" -ForegroundColor Yellow
netstat -ano | findstr :8000

Write-Host "`nPort 11434 Status:" -ForegroundColor Yellow
netstat -ano | findstr :11434

Write-Host "`nInstalled Packages:" -ForegroundColor Yellow
pip list | findstr -i "fastapi uvicorn sqlalchemy"

Write-Host "`n=== End Diagnostic ===" -ForegroundColor Cyan
```

---

**Need more help?** Check the full guide in `ALL_IN_ONE_STARTUP_GUIDE.md`
