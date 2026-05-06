"""
Speech-to-Text API Endpoints
Handles audio upload and transcription using Vosk (100% offline)

This module provides endpoints for:
  - /transcribe: Accepts a WAV audio file and returns the transcribed text using Vosk.
                 Vosk processes audio locally with no internet connection required.
  - /models:     Lists all supported speech language models and whether they're installed.
  - /health:     Simple health check for monitoring which languages are ready to use.

Note: The browser-based Web Speech API is the primary STT mechanism in this project.
This backend route exists as a fallback for server-side or non-browser transcription use cases.
"""

import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from ..services.speech_service import SpeechService

# All routes in this router are mounted under /api/speech
router = APIRouter(prefix="/api/speech", tags=["speech"])

# Instantiate the speech service singleton; it manages Vosk model loading and caching
speech_service = SpeechService()

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),    # The uploaded WAV audio file
    language: str = Form(default='en')  # Target language code for recognition model selection
):
    """
    Transcribe audio file to text using the Vosk offline speech recognition engine.
    
    Workflow:
      1. Validate the requested language is supported
      2. Check that the Vosk model for that language is installed on disk
      3. Save the uploaded audio to a temporary WAV file
      4. Pass the temp file to SpeechService for transcription
      5. Clean up the temp file (in the finally block, always runs)
      6. Return the transcribed text
    
    Args:
        audio: Audio file (WAV format expected — mono, 16000 Hz recommended for Vosk)
        language: Language code (en, ar, es, fr, de, zh, hi)
        
    Returns:
        JSON with transcribed text and language code
    """
    temp_wav_path = None  # Track the temp file path so we can delete it in the finally block
    
    try:
        # ── Step 1: Validate the language parameter ────────────────────────────
        if language not in speech_service.LANGUAGE_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {language}. Supported: {list(speech_service.LANGUAGE_MODELS.keys())}"
            )
        
        # ── Step 2: Check the model is installed (downloaded) on disk ────────────────
        # If not, return a 503 with instructions on how to download the model
        if not speech_service.is_model_available(language):
            model_info = speech_service.get_model_download_info(language)
            raise HTTPException(
                status_code=503,
                detail={
                    "error": f"Model not available for language: {language}",
                    "model_name": model_info.get('model_name'),
                    "download_url": model_info.get('download_url'),
                    "message": "Please download the model using the setup script"
                }
            )
        
        # ── Step 3: Save the uploaded audio to a temp file on disk ────────────────
        # Vosk needs a file path, not an in-memory buffer, so we write the upload to /tmp/
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav', mode='wb') as temp_wav:
            temp_wav_path = temp_wav.name
            content = await audio.read()  # Read entire uploaded file into memory
            temp_wav.write(content)        # Write to the temp file
        
        # ── Step 4: Transcribe the audio using the Vosk speech service ─────────────
        result = speech_service.transcribe_audio(temp_wav_path, language)
        
        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Transcription failed')
            )
        
        # Return the transcribed text and the language code used
        return JSONResponse(content={
            "success": True,
            "text": result['text'],
            "language": result['language']
        })
        
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is (don't wrap them in another 500)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )
    finally:
        # ── Step 5: Always clean up the temp file, even if an error occurred ────────
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.unlink(temp_wav_path)  # Delete the temporary WAV file
            except:
                pass  # Ignore errors during cleanup (non-critical)

@router.get("/models")
def get_available_models():
    """Return a list of all speech models with availability and download information.
    Used by the frontend or setup scripts to know which languages are ready to use
    and where to download models for languages that aren't installed yet.
    """
    # Fetch which languages have models currently installed and ready
    available = speech_service.get_available_languages()
    all_models = []
    
    # Build a status entry for every supported language, not just installed ones
    for lang in speech_service.LANGUAGE_MODELS.keys():
        info = speech_service.get_model_download_info(lang)
        all_models.append({
            'language': lang,
            'model_name': info.get('model_name'),
            'is_available': lang in available,  # True if the model is installed on disk
            'download_url': info.get('download_url')  # Where to get it if not installed
        })
    
    return {
        "available_languages": available,  # Languages ready for transcription right now
        "models": all_models               # Full status for all supported languages
    }

@router.get("/health")
def health_check():
    """Health check for the speech service.
    Returns which languages are currently available and the total count.
    """
    available = speech_service.get_available_languages()
    return {
        "status": "healthy",
        "available_languages": available,
        "total_models": len(available)  # How many language models are currently installed
    }
