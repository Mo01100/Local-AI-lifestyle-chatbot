# AI Lifestyle Chatbot - Data Pipeline & RAG System

A privacy-focused, offline AI lifestyle assistant with multi-language support, RAG capabilities, and voice interaction. This project uses local models and datasets to ensure 100% data privacy.

---

##  Features

- **Multi-Language Support**: Translate between English, Arabic, Spanish, French, German using Argos Translate
- **RAG-Powered Responses**: ChromaDB vector database for context-aware responses
- **Offline LLM**: Llama 3.2 via Ollama for complete privacy
- **Voice Interface**: Vosk (STT) and Piper TTS for hands-free interaction
- **Multiple Domains**: Nutrition, fitness, mental health 
- **100% Offline**: No cloud APIs, no data sent to external services.

---

## Prerequisites Checklist

Before starting, ensure you have:
- ✅ Python 3.8+ installed
- ✅ Ollama installed ([https://ollama.ai](https://ollama.ai))
- ✅ At least 10GB free disk space
- ✅ Internet connection (for initial setup and dataset downloads only)

---

##  Complete Startup Guide

To start the system from scratch, follow these steps in order.

### Step 1: Install Dependencies & Download Models

Open a terminal in the project directory (`c:\Users\Mohamed Metwaly\Downloads\Final Draft`):

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Download Llama 3.2 model
ollama pull llama3.2

# Download Translation Models (Argos Translate)
python scripts/translation/install_translation_models.py

# Download Speech-to-Text Models (Vosk)
python scripts/speech/download_vosk_models.py

# Download Text-to-Speech Models (Piper TTS)
scripts\download_piper.bat
```

### Step 2: Download & Prepare Datasets

> **Note:** The raw datasets and AI models for this project total over 2.8 GB, which exceeds GitHub's size limits. They are not included in this repository and must be downloaded manually.

Manually download datasets from Kaggle into their respective folders:
1. **[Daily Food and Nutrition Dataset](https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset)** ➔ `data/raw/nutrition/`
2. **[Food.com Recipes and User Interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)** ➔ `data/raw/recipes/`
3. **[Gym Exercise Data](https://www.kaggle.com/datasets/niharika41298/gym-exercise-data)** ➔ `data/raw/exercise/`
*(Optional: Download Mental Health / Sleep datasets as desired)*

THE data models  https://drive.google.com/drive/folders/1SaW5sl5LqX0MNZFJW8cg2HAGbfUNB1cx?usp=sharing but you need to download it 
After downloading, run the cleaning scripts:
```bash
python scripts/verify_datasets.py
python scripts/cleaning/clean_nutrition_data.py
python scripts/cleaning/clean_exercise_data.py
```

### Step 3: Setup RAG (Vector Database)

Ingest the cleaned data so the AI can use it:
```bash
python scripts/rag/rag_setup.py
python scripts/rag/data_ingestion.py
```

### Step 4: Run the Application

You can use the provided batch files for a 1-click startup:
- **`start_chatbot.bat`**: Starts the Ollama server, the FastAPI backend, and opens the web application in your browser.
- **`stop_chatbot.bat`**: Safely stops all running processes.

Alternatively, to run manually:
1. **Terminal 1**: `ollama serve` (keep open)
2. **Terminal 2**: `cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000` (keep open)
3. **Browser**: Navigate to `http://localhost:8000`

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    YOUR BROWSER (http://localhost:8000)      │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend Server (Port 8000)              │
└─────┬──────────────────┬──────────────────┬─────────────────┘
      ▼                  ▼                  ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│  Ollama  │      │ ChromaDB │      │  Argos   │
│  Server  │      │  Vector  │      │ Translate│
│ (Llama 3.2)     │ Database │      │  Models  │
└──────────┘      └──────────┘      └──────────┘
```

---

##  License & Purpose

This project is submitted as part of university coursework. It demonstrates the integration of multiple offline AI models, RAG architecture, and responsive web design.
