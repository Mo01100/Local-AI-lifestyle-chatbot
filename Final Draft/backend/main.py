"""
FastAPI Main Application
AI Lifestyle Chatbot Backend Server

This is the entry point for the FastAPI backend. It:
  - Creates the main FastAPI application instance
  - Configures CORS so the browser-based frontend can call the API
  - Registers all feature routers (chat, planning, reminders, settings, speech, TTS)
  - Serves the frontend HTML/CSS/JS files as static assets
  - Initialises the SQLite database on first startup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database.db import init_db
from .api import chat, planning, reminders, settings, speech, tts

# ─── Create the FastAPI application instance ───────────────────────────────────
# The title and description appear in the auto-generated Swagger UI at /docs
app = FastAPI(
    title="AI Lifestyle Chatbot API",
    description="Backend API for offline AI lifestyle chatbot",
    version="1.0.0"
)

# ─── CORS Middleware ─────────────────────────────────────────────────────
# Allows the browser frontend (running on a different port during development)
# to make fetch() calls to this API without being blocked by the browser's same-origin policy.
# In production, restrict 'allow_origins' to your actual frontend domain for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods: GET, POST, PUT, DELETE, PATCH, etc.
    allow_headers=["*"],  # Allows all request headers
)

# ─── Register Feature Routers ────────────────────────────────────────────────
# Each router is defined in its own module under backend/api/ and handles
# a specific feature area with its own URL prefix (e.g., /api/chat, /api/reminders, etc.)
app.include_router(chat.router)       # /api/chat   — chat messages and conversation history
app.include_router(planning.router)   # /api/planning — daily meal/exercise scheduling
app.include_router(reminders.router)  # /api/reminders — reminder CRUD
app.include_router(settings.router)   # /api/settings — user accessibility/appearance settings
app.include_router(speech.router)     # /api/speech — speech-to-text via Vosk
app.include_router(tts.router)        # /api/tts — text-to-speech via Piper

# ─── Serve Frontend Static Files ───────────────────────────────────────────────
# Mount the frontend/ folder as static files on the root path '/'.
# With html=True, navigating to '/' will automatically serve index.html.
# This means the backend serves both the API and the frontend from the same process.
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

@app.on_event("startup")
async def startup_event():
    """Runs automatically when the FastAPI server starts.
    Initialises the database tables so they exist before the first API request comes in.
    (This is idempotent — calling it multiple times won't delete existing data.)
    """
    init_db()  # Creates all SQLAlchemy table schemas in the SQLite database if they don't already exist
    print("✓ Backend server started")
    print("✓ API documentation: http://localhost:8000/docs")

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Lifestyle Chatbot API is running"
    }

@app.get("/api/info")
def get_info():
    """Get application information"""
    return {
        "name": "AI Lifestyle Chatbot",
        "version": "1.0.0",
        "description": "100% offline AI lifestyle assistant with multi-language support",
        "features": [
            "Multi-language chat (Arabic, Spanish, French, German, Chinese, Hindi, English)",
            "RAG-powered responses from nutrition and exercise knowledge base",
            "Conversation history storage",
            "Daily planning (meals, exercise, wellness)",
            "Reminder system with notifications",
            "Accessibility settings (contrast, brightness, font size)",
            "Speech-to-text input (Vosk offline recognition)",
            "Text-to-speech output (Piper neural TTS, offline)",
            "100% offline - no external API calls",
            "Complete data privacy"
        ],
        "technology": {
            "llm": "Llama 3.2 via Ollama",
            "rag": "ChromaDB with sentence-transformers",
            "translation": "Argos Translate (offline)",
            "tts": "Piper neural TTS (offline)",
            "backend": "FastAPI + SQLite",
            "frontend": "Vanilla HTML/CSS/JavaScript"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
