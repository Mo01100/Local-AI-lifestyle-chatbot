"""
Text-to-Speech API Endpoints
Provides offline TTS synthesis via the Piper neural TTS engine.

This module provides three endpoints:
  - /synthesize: Converts text to WAV audio, streaming the result back to the browser.
                 Supports multiple languages via the LANGUAGE_VOICES mapping in TTSService.
  - /voices:     Lists all installed Piper voice models and the language→voice mapping.
  - /health:     Returns whether Piper TTS is installed and ready to synthesize.

Piper TTS runs entirely on the local machine with no internet connection needed.
The browser's tts.js calls /synthesize, receives the WAV bytes, and plays them via the Web Audio API.
"""

import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from ..services.tts_service import TTSService

# All routes in this router are mounted under /api/tts
router = APIRouter(prefix="/api/tts", tags=["tts"])

# Instantiate the TTS service singleton (loads Piper voice models on demand)
tts_service = TTSService()


class SynthesizeRequest(BaseModel):
    """Schema for the TTS synthesis request."""
    text: str                          # The text to convert to speech
    voice: Optional[str] = None        # Specific Piper voice model name (overrides language if provided)
    language: Optional[str] = None     # Language code e.g. 'ar', 'en', 'fr' — maps to the matching Piper voice


@router.post("/synthesize")
async def synthesize_text(request: SynthesizeRequest):
    """
    Convert text to speech using the Piper TTS engine.
    
    Workflow:
      1. Validate the input text is not empty
      2. Check Piper TTS is installed and a voice is available for the requested language
      3. Call TTSService.synthesize() to generate raw WAV bytes
      4. Return the WAV as a streaming HTTP response so the browser can play it
    
    Args:
        text:     Text to convert to speech (max ~4000 chars recommended)
        voice:    Specific voice model name. If omitted, the language param selects the voice.
        language: Language code (e.g. 'en', 'ar', 'fr'). Used to pick the right voice model.
    
    Returns:
        WAV audio as a streaming response (audio/wav) — suitable for the browser Web Audio API.
    """
    # ── Step 1: Validate input ───────────────────────────────────────────────────
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    # ── Step 2: Confirm Piper is available ────────────────────────────────────────
    # Return 503 (Service Unavailable) with helpful setup instructions if Piper isn't installed
    if not tts_service.is_available():
        status = tts_service.get_status()
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Piper TTS is not available.",
                "piper_installed": status["piper_package_installed"],
                "voices_found": len(status["available_voices"]) > 0,
                "message": (
                    "Run: pip install piper-tts  "
                    "then: python -m piper.download_voices en_US-lessac-medium --download-dir models/piper/voices  "
                    "Or run scripts/download_piper.bat for guided setup."
                ),
            },
        )

    # ── Step 3: Synthesize ────────────────────────────────────────────────────
    # TTSService.synthesize() returns raw WAV bytes ready to stream
    try:
        wav_bytes = tts_service.synthesize(request.text, request.voice, request.language)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ── Step 4: Stream the WAV back to the client ───────────────────────────────
    # StreamingResponse avoids buffering the entire WAV in memory before sending
    return StreamingResponse(
        io.BytesIO(wav_bytes),       # Wrap the bytes in a file-like object for streaming
        media_type="audio/wav",      # Tell the browser this is audio
        headers={
            "Content-Disposition": "inline; filename=speech.wav",  # Play inline (not download)
            "Cache-Control": "no-cache",  # Don't cache TTS output (text may vary)
        },
    )


@router.get("/voices")
def get_voices():
    """Return available Piper voice models and the language→voice mapping."""
    voices = tts_service.get_available_voices()
    return {
        "voices": voices,
        "default_voice": TTSService.DEFAULT_VOICE,
        "language_voices": TTSService.LANGUAGE_VOICES,
        "count": len(voices),
    }


@router.get("/health")
def health_check():
    """Health check — shows whether Piper TTS is ready to use."""
    status = tts_service.get_status()
    return {
        "status": "available" if status["is_available"] else "unavailable",
        "language_voices": TTSService.LANGUAGE_VOICES,
        **status,
    }
