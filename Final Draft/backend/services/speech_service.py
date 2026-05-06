"""
Speech Recognition Service using Vosk
Provides offline speech-to-text functionality
"""

import os
import json
import wave
from pathlib import Path
from typing import Optional, Dict
from vosk import Model, KaldiRecognizer

class SpeechService:
    """Service for offline speech recognition using Vosk"""
    
    # Language code to Vosk model mapping
    LANGUAGE_MODELS = {
        'en': 'vosk-model-small-en-us-0.15',
        'ar': 'vosk-model-ar-mgb2-0.4',
        'es': 'vosk-model-small-es-0.42',
        'fr': 'vosk-model-small-fr-0.22',
        'de': 'vosk-model-small-de-0.15',
        'zh': 'vosk-model-small-cn-0.22',
        'hi': 'vosk-model-small-hi-0.22'
    }
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize speech service
        
        Args:
            models_dir: Directory containing Vosk models (default: project_root/models/vosk)
        """
        if models_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.models_dir = project_root / "models" / "vosk"
        else:
            self.models_dir = Path(models_dir)
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models: Dict[str, Model] = {}
        
    def _get_model_path(self, language: str) -> Optional[Path]:
        """Get path to Vosk model for given language"""
        model_name = self.LANGUAGE_MODELS.get(language)
        if not model_name:
            return None
        
        model_path = self.models_dir / model_name
        return model_path if model_path.exists() else None
    
    def _load_model(self, language: str) -> Optional[Model]:
        """Load Vosk model for given language"""
        if language in self.loaded_models:
            return self.loaded_models[language]
        
        model_path = self._get_model_path(language)
        if not model_path:
            return None
        
        try:
            model = Model(str(model_path))
            self.loaded_models[language] = model
            return model
        except Exception as e:
            print(f"Error loading model for {language}: {e}")
            return None
    
    def is_model_available(self, language: str) -> bool:
        """Check if model is available for given language"""
        return self._get_model_path(language) is not None
    
    def get_available_languages(self) -> list:
        """Get list of languages with available models"""
        return [lang for lang in self.LANGUAGE_MODELS.keys() 
                if self.is_model_available(lang)]
    
    def transcribe_audio(self, audio_path: str, language: str = 'en') -> Dict[str, any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to WAV audio file
            language: Language code (en, ar, es, fr, de, zh, hi)
            
        Returns:
            Dict with 'success', 'text', 'language', and optional 'error'
        """
        # Validate language
        if language not in self.LANGUAGE_MODELS:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'text': '',
                'language': language
            }
        
        # Check if model is available
        if not self.is_model_available(language):
            return {
                'success': False,
                'error': f'Model not found for language: {language}. Please download the model first.',
                'text': '',
                'language': language,
                'model_name': self.LANGUAGE_MODELS[language]
            }
        
        # Load model
        model = self._load_model(language)
        if not model:
            return {
                'success': False,
                'error': f'Failed to load model for language: {language}',
                'text': '',
                'language': language
            }
        
        try:
            # Open audio file
            wf = wave.open(audio_path, "rb")
            
            # Validate audio format
            if wf.getnchannels() != 1:
                wf.close()
                return {
                    'success': False,
                    'error': 'Audio must be mono (1 channel)',
                    'text': '',
                    'language': language
                }
            
            # Create recognizer
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            
            # Process audio
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'text' in result and result['text']:
                        results.append(result['text'])
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if 'text' in final_result and final_result['text']:
                results.append(final_result['text'])
            
            wf.close()
            
            # Combine all results
            full_text = ' '.join(results).strip()
            
            return {
                'success': True,
                'text': full_text,
                'language': language,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing audio: {str(e)}',
                'text': '',
                'language': language
            }
    
    def get_model_download_info(self, language: str) -> Dict[str, str]:
        """Get download information for a language model"""
        model_name = self.LANGUAGE_MODELS.get(language)
        if not model_name:
            return {'error': f'Unsupported language: {language}'}
        
        base_url = 'https://alphacephei.com/vosk/models'
        return {
            'language': language,
            'model_name': model_name,
            'download_url': f'{base_url}/{model_name}.zip',
            'install_path': str(self.models_dir / model_name),
            'is_installed': self.is_model_available(language)
        }
