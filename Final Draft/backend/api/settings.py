"""
Settings API Endpoints

This module provides HTTP routes for reading and updating user settings.
Settings are stored in the SQLite database as key-value pairs in the 'settings' table,
allowing them to persist across app restarts.

Supported settings:
  - contrast_mode: 'normal', 'high', or 'low' contrast
  - brightness:    integer percentage (0-200), controls page brightness filter
  - font_size:     'small', 'medium', or 'large'
  - language:      preferred UI/chat language code ('en', 'ar', etc.)
  - theme:         'light' or 'dark' UI theme
  - notifications_enabled: whether desktop notifications are on
  - notification_sound:    whether notification sounds play
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict

from ..database.db import get_db
from ..database.models import Setting

# All routes are mounted under /api/settings
router = APIRouter(prefix="/api/settings", tags=["settings"])

# ─── Pydantic Models ─────────────────────────────────────────────────────────

class SettingsResponse(BaseModel):
    """Schema for returning the app's current settings.
    Defaults match factory/first-run values so callers always get a usable response.
    """
    contrast_mode: str = "normal"           # Contrast level for accessibility
    brightness: int = 100                   # Page brightness as a percentage
    font_size: str = "medium"               # Text size: 'small', 'medium', 'large'
    language: str = "en"                    # Preferred language code
    theme: str = "light"                    # UI color theme: 'light' or 'dark'
    notifications_enabled: bool = True      # Whether browser notifications are enabled
    notification_sound: bool = True         # Whether notification sounds play

class SettingsUpdate(BaseModel):
    """Schema for a partial settings update (all fields optional).
    Only fields that are provided (non-None) will be saved.
    """
    contrast_mode: str = None               # New contrast mode (optional)
    brightness: int = None                  # New brightness value (optional)
    font_size: str = None                   # New font size (optional)
    language: str = None                    # New language code (optional)
    theme: str = None                       # New theme (optional)
    notifications_enabled: bool = None      # New notifications toggle (optional)
    notification_sound: bool = None         # New sound toggle (optional)

def get_setting_value(db: Session, key: str, default: str) -> str:
    """Retrieve a setting's value from the database by its key.
    If the key hasn't been saved yet, return the provided default value.
    All values are stored as strings in the DB (even booleans and integers).
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting.value if setting else default  # Fall back to default if not found

def set_setting_value(db: Session, key: str, value: str):
    """Save a setting value to the database.
    Uses an upsert pattern: updates the existing record if the key exists, or
    inserts a new record if it doesn't. Does NOT commit — the caller must commit.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        # Key already exists — just update the value
        setting.value = value
    else:
        # Key is new — create a new Setting record
        setting = Setting(key=key, value=value)
        db.add(setting)

@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get all current settings.
    Reads each setting from the database, converting to the correct Python type.
    Missing settings fall back to sensible defaults defined in the helper function.
    """
    return SettingsResponse(
        contrast_mode=get_setting_value(db, "contrast_mode", "normal"),
        brightness=int(get_setting_value(db, "brightness", "100")),  # Stored as string, cast to int
        font_size=get_setting_value(db, "font_size", "medium"),
        language=get_setting_value(db, "language", "en"),
        theme=get_setting_value(db, "theme", "light"),
        notifications_enabled=get_setting_value(db, "notifications_enabled", "true") == "true",  # String 'true' → bool
        notification_sound=get_setting_value(db, "notification_sound", "true") == "true"         # String 'true' → bool
    )

@router.put("", response_model=SettingsResponse)
def update_settings(request: SettingsUpdate, db: Session = Depends(get_db)):
    """Update one or more settings in a single request.
    Only fields that are provided (non-None) are persisted.
    All values are serialized to strings before saving (since the DB stores everything as text).
    After saving, the full current settings are returned so the frontend can update its state.
    """
    # Each block checks if a setting was included in the request before saving it
    if request.contrast_mode is not None:
        set_setting_value(db, "contrast_mode", request.contrast_mode)
    
    if request.brightness is not None:
        set_setting_value(db, "brightness", str(request.brightness))  # Cast int to string for storage
    
    if request.font_size is not None:
        set_setting_value(db, "font_size", request.font_size)
    
    if request.language is not None:
        set_setting_value(db, "language", request.language)
    
    if request.theme is not None:
        set_setting_value(db, "theme", request.theme)
    
    if request.notifications_enabled is not None:
        set_setting_value(db, "notifications_enabled", str(request.notifications_enabled).lower())  # True → 'true'
    
    if request.notification_sound is not None:
        set_setting_value(db, "notification_sound", str(request.notification_sound).lower())  # False → 'false'
    
    # Commit all changes to the database
    db.commit()
    
    # Return the updated settings by re-reading from the database
    return get_settings(db)
