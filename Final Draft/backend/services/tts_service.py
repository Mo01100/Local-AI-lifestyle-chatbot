"""
Text-to-Speech Service using piper-tts (pip install piper-tts)
Provides offline neural TTS via the PiperVoice Python API.

Install the package:
    pip install piper-tts

Download voices (example):
    python -m piper.download_voices en_US-lessac-medium
    python -m piper.download_voices ar_JO-kareem-medium
    # etc. — see models/piper/voices/
"""

import io
import wave
from pathlib import Path
from typing import Optional, Dict

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False


class TTSService:
    """Service for offline text-to-speech using the piper-tts Python package."""

    DEFAULT_VOICE = "en_US-lessac-medium"

    # Maps app language codes → Piper voice model names.
    LANGUAGE_VOICES: Dict[str, str] = {
        'en': 'en_US-lessac-medium',
        'ar': 'ar_JO-kareem-medium',
        'es': 'es_ES-davefx-medium',
        'fr': 'fr_FR-mls-medium',
        'de': 'de_DE-thorsten-medium',
        'zh': 'zh_CN-huayan-x_low',
        'hi': 'hi_IN-pratham-medium',
    }

    def __init__(self, voices_dir: Optional[str] = None):
        """
        Initialize the TTS service.

        Args:
            voices_dir: Directory containing .onnx voice model files.
                        Defaults to project_root/models/piper/voices
        """
        if voices_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.voices_dir = project_root / "models" / "piper" / "voices"
        else:
            self.voices_dir = Path(voices_dir)

        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self._loaded: Dict[str, "PiperVoice"] = {}  # cache loaded voice objects

    # ------------------------------------------------------------------
    # Availability checks
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if piper-tts is installed and at least one voice exists."""
        return PIPER_AVAILABLE and len(self.get_available_voices()) > 0

    def get_available_voices(self) -> list:
        """List voice model names (stems of .onnx files present in voices_dir)."""
        if not self.voices_dir.exists():
            return []
        return [p.stem for p in self.voices_dir.glob("*.onnx")]

    def get_voice_path(self, voice: str) -> Optional[Path]:
        """Return path to a .onnx file, or None if not present."""
        candidate = self.voices_dir / f"{voice}.onnx"
        return candidate if candidate.exists() else None

    # ------------------------------------------------------------------
    # Voice loading (with in-process cache)
    # ------------------------------------------------------------------

    def _load_voice(self, voice: str) -> "PiperVoice":
        """Load (and cache) a PiperVoice object for the given model name."""
        if voice not in self._loaded:
            path = self.get_voice_path(voice)
            if path is None:
                raise RuntimeError(
                    f"Voice model '{voice}.onnx' not found in {self.voices_dir}. "
                    "Download it with: python -m piper.download_voices " + voice
                )
            self._loaded[voice] = PiperVoice.load(str(path))
        return self._loaded[voice]

    # ------------------------------------------------------------------
    # Synthesis
    # ------------------------------------------------------------------

    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        language: Optional[str] = None,
    ) -> bytes:
        """
        Convert text to WAV audio and return the raw bytes.

        Priority for choosing a voice:
            explicit voice name  >  language code mapping  >  DEFAULT_VOICE  >  first available

        Args:
            text:     Text to synthesize.
            voice:    Explicit voice model name, e.g. 'en_US-lessac-medium'.
            language: Two-letter language code, e.g. 'ar'.  Used if voice is not provided.

        Returns:
            WAV audio as bytes.

        Raises:
            RuntimeError: if piper-tts is not installed or no voice is found.
        """
        if not PIPER_AVAILABLE:
            raise RuntimeError(
                "piper-tts is not installed. Run: pip install piper-tts"
            )

        # Resolve voice name
        if not voice and language:
            voice = self.LANGUAGE_VOICES.get(language)
        resolved = voice or self.DEFAULT_VOICE

        if self.get_voice_path(resolved) is None:
            available = self.get_available_voices()
            if not available:
                raise RuntimeError(
                    f"No voice models found in {self.voices_dir}. "
                    "Download one with: python -m piper.download_voices en_US-lessac-medium"
                )
            resolved = available[0]

        # Truncate excessively long text
        max_len = 4000
        clean_text = text.strip()
        if len(clean_text) > max_len:
            clean_text = clean_text[:max_len]

        # Load (cached) voice and synthesize into an in-memory WAV
        piper_voice = self._load_voice(resolved)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            piper_voice.synthesize_wav(clean_text, wav_file)

        return buffer.getvalue()

    # ------------------------------------------------------------------
    # Status / info
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return status info for the health endpoint."""
        voices = self.get_available_voices()
        return {
            "piper_package_installed": PIPER_AVAILABLE,
            "voices_dir": str(self.voices_dir),
            "available_voices": voices,
            "default_voice": self.DEFAULT_VOICE,
            "is_available": self.is_available(),
        }
