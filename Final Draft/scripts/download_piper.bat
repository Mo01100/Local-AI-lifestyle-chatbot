@echo off
echo ============================================================
echo  Piper TTS Setup Script - pip install piper-tts
echo  Installs piper-tts and downloads voice models for
echo  all 7 supported languages: EN, AR, ES, FR, DE, ZH, HI
echo ============================================================
echo.

REM Create voices directory
mkdir "models\piper\voices" 2>nul
echo Created: models\piper\voices\
echo.

echo ============================================================
echo  STEP 1: Install the piper-tts Python package
echo ============================================================
pip install piper-tts
echo.

echo ============================================================
echo  STEP 2: Download voice models (choose the ones you need)
echo  All models are downloaded into models\piper\voices\
echo ============================================================
echo.

echo  [EN] English (US) — default voice, recommended to always download
python -m piper.download_voices en_US-lessac-medium --download-dir models\piper\voices
echo.

echo  Choose any of the following (press Ctrl+C to skip remaining):
echo.

echo  [AR] Arabic
set /p doAR="  Download Arabic voice? (y/n): "
if /i "%doAR%"=="y" python -m piper.download_voices ar_JO-kareem-medium --download-dir models\piper\voices

echo  [ES] Spanish
set /p doES="  Download Spanish voice? (y/n): "
if /i "%doES%"=="y" python -m piper.download_voices es_ES-davefx-medium --download-dir models\piper\voices

echo  [FR] French
set /p doFR="  Download French voice? (y/n): "
if /i "%doFR%"=="y" python -m piper.download_voices fr_FR-mls-medium --download-dir models\piper\voices

echo  [DE] German
set /p doDE="  Download German voice? (y/n): "
if /i "%doDE%"=="y" python -m piper.download_voices de_DE-thorsten-medium --download-dir models\piper\voices

echo  [ZH] Chinese
set /p doZH="  Download Chinese voice? (y/n): "
if /i "%doZH%"=="y" python -m piper.download_voices zh_CN-huayan-x_low --download-dir models\piper\voices

echo  [HI] Hindi
set /p doHI="  Download Hindi voice? (y/n): "
if /i "%doHI%"=="y" python -m piper.download_voices hi_IN-dhruva-medium --download-dir models\piper\voices

echo.
echo ============================================================
echo  Done! Restart the chatbot to enable TTS.
echo  The TTS language will automatically follow the speech
echo  language selector in the chat UI.
echo ============================================================
pause
