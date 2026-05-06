# FFmpeg Installation Guide for Windows

FFmpeg is required for converting WebM audio to WAV format for speech recognition.

## Quick Installation (Recommended)

### Option 1: Using Chocolatey (Easiest)

1. **Install Chocolatey** (if not already installed):
   - Open PowerShell as Administrator
   - Run:
     ```powershell
     Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
     ```

2. **Install FFmpeg**:
   ```powershell
   choco install ffmpeg
   ```

3. **Verify installation**:
   ```powershell
   ffmpeg -version
   ```

### Option 2: Manual Installation

1. **Download FFmpeg**:
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: `ffmpeg-release-essentials.zip`

2. **Extract**:
   - Extract to: `C:\ffmpeg`

3. **Add to PATH**:
   - Open System Properties → Environment Variables
   - Edit "Path" variable
   - Add: `C:\ffmpeg\bin`
   - Click OK

4. **Restart terminal** and verify:
   ```powershell
   ffmpeg -version
   ```

## Verification

After installation, test with:
```powershell
ffmpeg -version
```

You should see FFmpeg version information.

## Troubleshooting

**"ffmpeg not found"** → Restart your terminal after installation

**PATH not working** → Make sure you added `C:\ffmpeg\bin` (not just `C:\ffmpeg`)

## Alternative: Use WAV Recording

If you don't want to install FFmpeg, you can modify the frontend to record in WAV format instead of WebM. See `SPEECH_TO_TEXT_GUIDE.md` for details.
