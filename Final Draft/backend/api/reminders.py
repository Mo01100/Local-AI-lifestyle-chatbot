"""
Reminders API Endpoints

This module provides HTTP routes for managing user reminders.
Reminders support:
  - Categorization (meal, exercise, medication, custom)
  - One-time or recurring schedules (daily, weekly, monthly)
  - Completion tracking

Full CRUD (Create, Read, Update, Delete) is supported, plus a PATCH endpoint
to mark a specific reminder as completed without overwriting all its fields.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database.db import get_db
from ..database.models import Reminder

# All routes in this router are mounted under the /api/reminders URL prefix
router = APIRouter(prefix="/api/reminders", tags=["reminders"])

# ─── Pydantic Models ─────────────────────────────────────────────────────────

class ReminderRequest(BaseModel):
    """Schema for creating or updating a reminder."""
    title: str                              # Short name for the reminder (required)
    description: Optional[str] = None       # Optional longer description
    category: str = "custom"               # Category: 'meal', 'exercise', 'medication', or 'custom'
    due_datetime: datetime                  # When the reminder should trigger
    is_recurring: bool = False              # Whether this reminder repeats
    recurrence_pattern: Optional[str] = None  # How it repeats: 'daily', 'weekly', 'monthly'

class ReminderResponse(BaseModel):
    """Schema for returning reminder data from the database."""
    id: int                                 # Auto-incremented database ID
    title: str                              # Reminder title
    description: Optional[str]              # Optional description
    category: str                           # Reminder category
    due_datetime: datetime                  # Due date and time
    is_recurring: bool                      # Whether this reminder repeats
    recurrence_pattern: Optional[str]       # Recurrence pattern (if recurring)
    is_completed: bool                      # Whether the user has marked this as done
    created_at: datetime                    # When this reminder was first created

@router.get("/", response_model=List[ReminderResponse])
def get_all_reminders(db: Session = Depends(get_db)):
    """Get all reminders (both active and completed), sorted by due date ascending.
    Used by the frontend Reminders page to display the full list.
    """
    # Fetch all reminders ordered soonest-first
    reminders = db.query(Reminder).order_by(Reminder.due_datetime).all()
    return reminders

@router.get("/active", response_model=List[ReminderResponse])
def get_active_reminders(db: Session = Depends(get_db)):
    """Get only reminders that are not yet completed AND are still in the future.
    Useful for notification systems or showing only upcoming reminders.
    """
    reminders = db.query(Reminder).filter(
        Reminder.is_completed == False,         # Exclude already-completed reminders
        Reminder.due_datetime >= datetime.utcnow()  # Exclude past reminders
    ).order_by(Reminder.due_datetime).all()
    return reminders

@router.post("/", response_model=ReminderResponse)
def create_reminder(request: ReminderRequest, db: Session = Depends(get_db)):
    """Create a new reminder"""
    reminder = Reminder(
        title=request.title,
        description=request.description,
        category=request.category,
        due_datetime=request.due_datetime,
        is_recurring=request.is_recurring,
        recurrence_pattern=request.recurrence_pattern
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: int, request: ReminderRequest, db: Session = Depends(get_db)):
    """Update a reminder"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.title = request.title
    reminder.description = request.description
    reminder.category = request.category
    reminder.due_datetime = request.due_datetime
    reminder.is_recurring = request.is_recurring
    reminder.recurrence_pattern = request.recurrence_pattern
    
    db.commit()
    db.refresh(reminder)
    return reminder

@router.patch("/{reminder_id}/complete")
def complete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Mark a reminder as completed without updating any other fields.
    Uses PATCH (partial update) since only the completion flag changes.
    """
    # Look up the reminder; return 404 if it doesn't exist
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Toggle the completion flag to True
    reminder.is_completed = True
    db.commit()
    
    return {"message": "Reminder marked as completed"}

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Delete a reminder"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    
    return {"message": "Reminder deleted successfully"}
