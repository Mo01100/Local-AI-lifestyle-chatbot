"""
Translation Model Installation Script
Downloads and installs Argos Translate language packages.
100% OFFLINE after installation - No API calls during translation.

Argos Translate is a local, open-source machine translation library.
Language packages (translation models) must be downloaded ONCE from the
internet before they can be used offline.

This script:
  1. Updates the Argos Translate package index (fetches available packages)
  2. Downloads and installs bidirectional translation packages for 6 languages
     (Arabic, Spanish, French, German, Chinese, Hindi) all paired with English
  3. Verifies installed packages and runs a quick translation test

English is used as the pivot language because the LLM only understands English.
So for any language X: user text -> translate X->EN -> LLM -> translate EN->X

Usage:
  python scripts/translation/install_translation_models.py
  (One-time setup; requires internet for the initial download)
"""

import argostranslate.package
import argostranslate.translate
from pathlib import Path

class TranslationModelInstaller:
    """Install Argos Translate language packages (language pairs for offline translation).
    
    Each installed package enables translation in ONE direction between a language pair.
    To support full round-trip translation (user language <-> English), both directions
    must be installed (install_bidirectional handles this automatically).
    """
    
    def __init__(self):
        self.installed_packages = []  # Track which packages were successfully installed this run
    
    def update_package_index(self) -> None:
        """Fetch the latest list of available Argos Translate packages from the internet.
        
        This calls argostranslate.package.update_package_index() which downloads
        a small JSON index of all available language package versions and their URLs.
        Must be called once before install_language_pair() can find packages.
        """
        print("Updating Argos Translate package index...")
        argostranslate.package.update_package_index()  # Downloads the package manifest
        print("\u2713 Package index updated\n")
    
    def install_language_pair(self, from_code: str, to_code: str) -> bool:
        """
        Download and install a single translation direction package.
        
        Searches the available packages (fetched via update_package_index) for a
        package matching the given language codes, downloads it, and installs it.
        
        Args:
            from_code: ISO 639-1 source language code (e.g., 'ar' for Arabic)
            to_code:   ISO 639-1 target language code (e.g., 'en' for English)
        
        Returns:
            True if the package was installed successfully, False otherwise.
        """
        print(f"Installing {from_code} \u2192 {to_code}...")
        
        try:
            # Query the package index for all available packages
            available_packages = argostranslate.package.get_available_packages()
            
            # Find the package that matches our direction (from_code -> to_code)
            package_to_install = next(
                (pkg for pkg in available_packages 
                 if pkg.from_code == from_code and pkg.to_code == to_code),
                None  # Returns None if no matching package is found
            )
            
            if package_to_install:
                # download() fetches the .argosmodel file and returns its local path
                # install_from_path() extracts and registers the model for use
                argostranslate.package.install_from_path(
                    package_to_install.download()
                )
                self.installed_packages.append(f"{from_code} \u2192 {to_code}")
                print(f"  \u2713 Installed {from_code} \u2192 {to_code}\n")
                return True
            else:
                print(f"  \u26a0 Package {from_code} \u2192 {to_code} not found\n")
                return False
        
        except Exception as e:
            print(f"  \u2717 Error installing {from_code} \u2192 {to_code}: {e}\n")
            return False
    
    def install_bidirectional(self, lang1: str, lang2: str) -> None:
        """Install both translation directions for a language pair.
        
        Calls install_language_pair() twice: lang1->lang2 then lang2->lang1.
        Both directions are needed for full round-trip translation:
          - lang1->lang2 to translate user input to English
          - lang2->lang1 to translate LLM response back to the user's language
        """
        print(f"Installing bidirectional translation: {lang1} \u2194 {lang2}")
        print("-" * 60)
        self.install_language_pair(lang1, lang2)  # First direction
        self.install_language_pair(lang2, lang1)  # Reverse direction
    
    def install_common_languages(self) -> None:
        """Install commonly used language pairs."""
        print("Installing common language packages...")
        print("="*60 + "\n")
        
        # English is the pivot language for the LLM
        languages = [
            ('ar', 'en', 'Arabic'),
            ('es', 'en', 'Spanish'),
            ('fr', 'en', 'French'),
            ('de', 'en', 'German'),
            ('zh', 'en', 'Chinese'),
            ('hi', 'en', 'Hindi'),
        ]
        
        for from_code, to_code, name in languages:
            print(f"\n--- {name} ↔ English ---")
            self.install_bidirectional(from_code, to_code)
    
    def verify_installation(self) -> None:
        """Verify installed packages."""
        print("\n" + "="*60)
        print("Verifying installed translation packages...")
        print("="*60 + "\n")
        
        installed = argostranslate.package.get_installed_packages()
        
        if installed:
            print(f"Total installed packages: {len(installed)}\n")
            for pkg in installed:
                print(f"  ✓ {pkg.from_name} ({pkg.from_code}) → {pkg.to_name} ({pkg.to_code})")
        else:
            print("  ⚠ No packages installed")
        
        print()
    
    def test_translation(self) -> None:
        """Test translation with sample text."""
        print("\n" + "="*60)
        print("Testing translation...")
        print("="*60 + "\n")
        
        test_cases = [
            ('ar', 'en', 'مرحبا'),
            ('es', 'en', 'Hola'),
            ('fr', 'en', 'Bonjour'),
        ]
        
        for from_code, to_code, text in test_cases:
            try:
                translated = argostranslate.translate.translate(text, from_code, to_code)
                print(f"{from_code} → {to_code}: '{text}' → '{translated}'")
            except Exception as e:
                print(f"{from_code} → {to_code}: Error - {e}")
        
        print()
    
    def run(self) -> None:
        """Execute complete installation."""
        print("\n" + "="*60)
        print("Argos Translate Model Installation (Offline Translation)")
        print("="*60 + "\n")
        
        print("⚠ NOTE: This will download language models from the internet.")
        print("After installation, all translation will be 100% offline.\n")
        
        self.update_package_index()
        self.install_common_languages()
        self.verify_installation()
        self.test_translation()
        
        print("="*60)
        print("✓ Translation model installation complete!")
        print("="*60)
        print("\nAll future translations will be 100% offline.")
        print("\nNext step: Test translation service")
        print("  python scripts/translation/translation_service.py\n")

if __name__ == "__main__":
    installer = TranslationModelInstaller()
    installer.run()
