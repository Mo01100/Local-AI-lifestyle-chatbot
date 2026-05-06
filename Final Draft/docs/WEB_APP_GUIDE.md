# Web Application Startup Guide

## Quick Start

### 1. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Start Backend Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start at: http://localhost:8000

**API Documentation**: http://localhost:8000/docs

### 3. Access the Application

Open your browser and visit: **http://localhost:8000**

The frontend is automatically served by FastAPI.

---

## Features

###  Chat
- Multi-language support (7 languages)
- RAG-powered responses from knowledge base
- Domain selection (nutrition, exercise, all)
- Conversation persistence

###  History
- View all past conversations
- Search conversations
- Delete conversations
- Resume conversations

###  Daily Planning
- Meal planning (breakfast, lunch, dinner, snacks)
- Exercise planning
- Wellness goals tracking
- Notes and reflections
- Date picker for any day

###  Reminders
- Create reminders with categories
- Recurring reminders (daily, weekly, monthly)
- Mark as complete
- Edit and delete reminders

###  Settings
- **Accessibility**: Contrast mode, brightness, font size
- **Appearance**: Light/dark theme
- **Language**: Preferred language selection
- **Notifications**: Enable/disable, sound on/off

###  About
- Project information
- Features list
- Technology stack
- Privacy & security information

---

## System Requirements

- **Python 3.8+**
- **Ollama** with Llama 3.2 model
- **All dependencies** from requirements.txt
- **Datasets** (optional for RAG features)

---

## Troubleshooting

### Backend won't start
- Ensure all dependencies installed: `pip install -r backend/requirements.txt`
- Check port 8000 is not in use

### Chat not working
- Ensure Ollama is running: `ollama serve`
- Ensure Llama 3.2 downloaded: `ollama pull llama3.2`
- Check backend logs for errors

### No RAG context
- Ensure datasets are downloaded and cleaned
- Run data ingestion: `python scripts/rag/data_ingestion.py`

### Translation not working
- Install translation models: `python scripts/translation/install_translation_models.py`

---

## Development

### Backend Structure
```
backend/
├── main.py              # FastAPI application
├── api/                 # API endpoints
│   ├── chat.py
│   ├── planning.py
│   ├── reminders.py
│   └── settings.py
├── database/            # Database models
│   ├── models.py
│   └── db.py
└── services/            # Business logic
    └── chat_service.py
```

### Frontend Structure
```
frontend/
├── index.html           # Main HTML
├── css/
│   └── main.css        # Styles
└── js/
    ├── app.js          # Main app logic
    ├── chat.js         # Chat functionality
    ├── history.js      # History management
    ├── planning.js     # Planning features
    ├── reminders.js    # Reminders management
    └── settings.js     # Settings management
```

---

## API Endpoints

### Chat
- `POST /api/chat/` - Send message
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}` - Get conversation
- `DELETE /api/chat/conversations/{id}` - Delete conversation

### Planning
- `GET /api/planning/today` - Get today's plan
- `GET /api/planning/{date}` - Get plan by date
- `POST /api/planning/` - Create/update plan

### Reminders
- `GET /api/reminders/` - List all reminders
- `GET /api/reminders/active` - Get active reminders
- `POST /api/reminders/` - Create reminder
- `PUT /api/reminders/{id}` - Update reminder
- `PATCH /api/reminders/{id}/complete` - Mark complete
- `DELETE /api/reminders/{id}` - Delete reminder

### Settings
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings

---

## Data Storage

All data stored locally in SQLite database:
- **Location**: `data/app.db`
- **Tables**: conversations, messages, daily_plans, reminders, settings

**100% Offline** - No external API calls, complete privacy.
