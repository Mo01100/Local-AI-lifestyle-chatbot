"""
Vosk Model Download Utility
Downloads and extracts Vosk language models for speech recognition.

Vosk is an offline speech recognition library. Before it can transcribe audio
in a specific language, the corresponding model must be downloaded and extracted
under models/vosk/ in the project root.

Usage:
  # Download all supported languages:
  python scripts/speech/download_vosk_models.py

  # Download specific languages only:
  python scripts/speech/download_vosk_models.py en ar fr

After downloading, Vosk models are used by:
  - backend/services/speech_service.py (server-side transcription)
  - backend/api/speech.py (REST endpoint)
"""

import os
import sys
import zipfile
import urllib.request
from pathlib import Path
from tqdm import tqdm

# ─── Language Model Registry ────────────────────────────────────────────────────────
# Mapping from ISO 639-1 language code to the corresponding Vosk model info.
# 'name'  = the folder name after extraction (also the zip file's base name)
# 'url'   = the direct download link from alphacephei.com
# 'size'  = approximate download size shown to the user before downloading
MODELS = {
    'en': {
        'name': 'vosk-model-small-en-us-0.15',
        'url':  'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        'size': '40 MB'
    },
    'ar': {
        'name': 'vosk-model-ar-mgb2-0.4',
        'url':  'https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip',
        'size': '320 MB'  # Arabic model is larger due to richer phoneme set
    },
    'es': {
        'name': 'vosk-model-small-es-0.42',
        'url':  'https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip',
        'size': '39 MB'
    },
    'fr': {
        'name': 'vosk-model-small-fr-0.22',
        'url':  'https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip',
        'size': '41 MB'
    },
    'de': {
        'name': 'vosk-model-small-de-0.15',
        'url':  'https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip',
        'size': '45 MB'
    },
    'zh': {
        'name': 'vosk-model-small-cn-0.22',
        'url':  'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip',
        'size': '42 MB'
    },
    'hi': {
        'name': 'vosk-model-small-hi-0.22',
        'url':  'https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip',
        'size': '42 MB'
    }
}

class DownloadProgressBar(tqdm):
    """Custom tqdm progress bar for urllib.request.urlretrieve download callbacks.
    
    urlretrieve calls reporthook(block_count, block_size, total_size) periodically.
    This class bridges that callback into tqdm's update() method so the download
    progress is displayed in the terminal in real time.
    """
    def update_to(self, b=1, bsize=1, tsize=None):
        # tsize is the total file size (may be None until first call)
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # Compute bytes downloaded so far

def download_model(language: str, models_dir: Path):
    """Download and extract a single Vosk model for the given language code.
    
    Steps:
      1. Look up the model info from the MODELS registry
      2. Skip download if the model directory already exists on disk
      3. Download the ZIP file to a temporary directory with a progress bar
      4. Extract the ZIP into models_dir/
      5. Delete the ZIP file and clean up the temp directory
      6. Return True on success, False on any error
    """
    if language not in MODELS:
        print(f"\u274c Unsupported language: {language}")
        print(f"   Supported languages: {', '.join(MODELS.keys())}")
        return False
    
    model_info = MODELS[language]
    model_name = model_info['name']
    model_url  = model_info['url']
    model_size = model_info['size']
    
    model_path = models_dir / model_name  # Expected extraction path
    
    # Skip download if model directory already exists
    if model_path.exists():
        print(f"\u2713 Model already exists: {model_name}")
        return True
    
    print(f"\n\U0001f4e5 Downloading {language.upper()} model ({model_size})...")
    print(f"   URL: {model_url}")
    
    # Use a temp subfolder so partial downloads don't corrupt the models directory
    temp_dir = models_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = temp_dir / f"{model_name}.zip"  # Temporary download destination
    
    try:
        # ── Download with real-time progress bar ───────────────────────────────────
        # DownloadProgressBar.update_to is passed to urlretrieve as the progress callback
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=model_name) as t:
            urllib.request.urlretrieve(
                model_url,
                zip_path,
                reporthook=t.update_to  # Called by urlretrieve after each block
            )
        
        print(f"\U0001f4e6 Extracting {model_name}...")
        
        # ── Extract the ZIP directly into models_dir ───────────────────────────────
        # extractall creates model_name/ subfolder inside models_dir automatically
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)
        
        zip_path.unlink()  # Delete the ZIP after extraction to free disk space
        
        print(f"\u2713 Successfully installed {model_name}")
        return True
        
    except Exception as e:
        print(f"\u274c Error downloading {model_name}: {e}")
        if zip_path.exists():
            zip_path.unlink()  # Clean up partial download file
        return False

def main():
    """Entry point: resolve the models directory, parse CLI args, and download.
    
    Command-line usage:
      python download_vosk_models.py          # Download all languages
      python download_vosk_models.py en ar fr  # Download specific languages only
    """
    # Resolve paths relative to this script's location so the script works
    # regardless of the working directory it is run from
    script_dir   = Path(__file__).parent
    project_root = script_dir.parent.parent
    models_dir   = project_root / "models" / "vosk"  # Target: <project>/models/vosk/
    
    models_dir.mkdir(parents=True, exist_ok=True)  # Create directory tree if absent
    
    print("=" * 60)
    print("Vosk Model Downloader")
    print("=" * 60)
    print(f"Models directory: {models_dir}")
    print()
    
    # ── Select languages to download ────────────────────────────────────────────
    if len(sys.argv) > 1:
        # User specified language codes as positional CLI arguments
        languages = sys.argv[1:]
        print(f"Downloading models for: {', '.join(languages)}")
    else:
        # No arguments = download all supported languages
        print("No languages specified. Downloading all models...")
        print("To download specific languages, use: python download_vosk_models.py en es fr")
        print()
        languages = list(MODELS.keys())
    
    # ── Download each model ──────────────────────────────────────────────────
    success_count = 0
    fail_count    = 0
    
    for lang in languages:
        if download_model(lang, models_dir):
            success_count += 1
        else:
            fail_count += 1
    
    # Clean up the temp directory if it still exists after all downloads
    temp_dir = models_dir / "temp"
    if temp_dir.exists():
        temp_dir.rmdir()  # Only succeeds if the directory is empty
    
    # ── Print download summary ───────────────────────────────────────────────
    print()
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"\u2713 Successful: {success_count}")
    print(f"\u274c Failed: {fail_count}")
    print()
    
    if success_count > 0:
        print("\u2713 Models are ready to use!")
        print("  You can now use speech-to-text in your chatbot.")
    
    if fail_count > 0:
        print("\u26a0 Some models failed to download.")
        print("  Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
