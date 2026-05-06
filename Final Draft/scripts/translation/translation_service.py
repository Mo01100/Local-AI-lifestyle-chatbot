"""
Translation Service
Provides translation layer for multi-language support.
100% OFFLINE - Uses Argos Translate (no API calls).

This module acts as the language bridge in the chatbot pipeline:
  1. User writes in any supported language (Arabic, French, Spanish, etc.)
  2. translate_to_english() converts it to English for the LLM
  3. The LLM answers in English
  4. translate_from_english() converts the answer back to the user's language

Language detection uses Unicode character-range heuristics.
All translations are cached in data/translation_cache.json to speed up repeated queries.
"""

import argostranslate.translate
from typing import Optional, Tuple
import json
from pathlib import Path

class TranslationService:
    """Offline translation service using Argos Translate.
    
    Wraps Argos Translate calls with language detection, a disk-backed cache,
    and helper methods for the standard input/output translation pattern.
    """
    
    def __init__(self, cache_translations: bool = True):
        self.cache_enabled = cache_translations  # When False, skip cache (useful for testing)
        self.cache = {}                          # In-memory translation cache
        self.cache_file = Path('data') / 'translation_cache.json'  # Persistent disk cache
        
        # Restore in-memory cache from disk so repeated phrases are translated instantly
        if self.cache_enabled and self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
    
    def detect_language(self, text: str) -> str:
        """
        Detect language using Unicode character-range heuristics.
        
        - Arabic chars: U+0600–U+06FF
        - Chinese chars: U+4E00–U+9FFF
        - Anything else defaults to English
        
        Limitation: cannot distinguish between Latin-script languages (en/fr/es).
        Swap in `langdetect` library for production-quality detection.
        """
        # Arabic Unicode block
        if any('\u0600' <= char <= '\u06FF' for char in text):
            return 'ar'
        
        # CJK Unified Ideographs block (Chinese)
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return 'zh'
        
        # Default: treat as English
        return 'en'
    
    def translate(self, text: str, from_lang: str, to_lang: str) -> str:
        """
        Translate text using Argos Translate. Results are cached on disk.
        Returns the original text unchanged on any error (fail-safe).
        """
        # Avoid Argos call if source and target language are identical
        if from_lang == to_lang:
            return text
        
        # Cache key encodes the language pair + source text
        cache_key = f"{from_lang}_{to_lang}_{text}"
        if self.cache_enabled and cache_key in self.cache:
            return self.cache[cache_key]  # Return cached result immediately
        
        try:
            # Argos Translate runs a local neural MT model (no internet needed)
            translated = argostranslate.translate.translate(text, from_lang, to_lang)
            
            # Store result in cache and persist to disk
            if self.cache_enabled:
                self.cache[cache_key] = translated
                self._save_cache()
            
            return translated
        
        except Exception as e:
            print(f"Translation error ({from_lang} -> {to_lang}): {e}")
            return text  # Return original on failure so the app doesn't crash
    
    def translate_to_english(self, text: str, source_lang: Optional[str] = None) -> Tuple[str, str]:
        """
        Translate text to English (for LLM processing).
        
        Args:
            text: Text to translate
            source_lang: Source language code (auto-detected if None)
        
        Returns:
            Tuple of (translated_text, detected_language)
        """
        # Detect language if not provided
        if source_lang is None:
            source_lang = self.detect_language(text)
        
        # Translate to English
        if source_lang == 'en':
            return text, 'en'
        
        translated = self.translate(text, source_lang, 'en')
        return translated, source_lang
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate text from English to target language (for user response).
        
        Args:
            text: English text from LLM
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        if target_lang == 'en':
            return text
        
        return self.translate(text, 'en', target_lang)
    
    def process_user_input(self, user_input: str) -> Tuple[str, str]:
        """
        Process user input: detect language and translate to English.
        
        Args:
            user_input: User's input in any language
        
        Returns:
            Tuple of (english_text, user_language)
        """
        english_text, user_lang = self.translate_to_english(user_input)
        return english_text, user_lang
    
    def process_llm_output(self, llm_output: str, user_language: str) -> str:
        """
        Process LLM output: translate from English to user's language.
        
        Args:
            llm_output: LLM response in English
            user_language: User's language code
        
        Returns:
            Translated response
        """
        return self.translate_from_english(llm_output, user_language)
    
    def _save_cache(self) -> None:
        """Write the in-memory cache to disk after each new translation.
        ensure_ascii=False preserves Arabic/Chinese characters correctly.
        """
        if not self.cache_enabled:
            return
        
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear both the in-memory cache and the on-disk JSON file.
        Use when translation models are updated and cached results may be stale.
        """
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()  # Delete the cache file from disk

if __name__ == "__main__":
    # Test translation service
    print("\n" + "="*60)
    print("Translation Service Test (100% Offline)")
    print("="*60 + "\n")
    
    service = TranslationService()
    
    # Test cases
    test_inputs = [
        ("Hello, how are you?", "en"),
        ("مرحبا، كيف حالك؟", "ar"),
        ("Hola, ¿cómo estás?", "es"),
        ("Bonjour, comment allez-vous?", "fr"),
    ]
    
    print("Testing user input processing (any language → English):")
    print("-" * 60)
    for text, expected_lang in test_inputs:
        english_text, detected_lang = service.process_user_input(text)
        print(f"\nInput ({expected_lang}): {text}")
        print(f"Detected: {detected_lang}")
        print(f"English: {english_text}")
    
    print("\n\n" + "="*60)
    print("Testing LLM output processing (English → user language):")
    print("-" * 60)
    
    llm_response = "Here are some healthy breakfast options for you."
    
    for target_lang in ['en', 'ar', 'es', 'fr']:
        translated = service.process_llm_output(llm_response, target_lang)
        print(f"\n{target_lang}: {translated}")
    
    print("\n" + "="*60)
    print("✓ Translation service test complete")
    print("="*60)
    print(f"\nCache size: {len(service.cache)} translations")
    print("\nNext step: Setup LLM integration")
    print("  python scripts/llm/llm_interface.py\n")
