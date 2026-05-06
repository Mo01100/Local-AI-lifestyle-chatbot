"""
Daily Planning API Endpoints

This module provides HTTP routes for managing daily health plans.
Each plan is tied to a specific calendar date and can include:
  - Meal entries (breakfast, lunch, dinner, snacks)
  - Exercise/workout notes
  - Wellness goals and freeform notes

If a plan already exists for a given date, POSTing to create will update it instead
(upsert behavior) — so the frontend never needs to know whether to POST or PUT.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from ..database.db import get_db
from ..database.models import DailyPlan

# All routes in this router are accessible under the /api/planning URL prefix
router = APIRouter(prefix="/api/planning", tags=["planning"])

# ─── Pydantic Models ─────────────────────────────────────────────────────────

class PlanRequest(BaseModel):
    """Schema for creating or updating a daily plan (all meal/activity fields are optional)."""
    date: date                           # The calendar date this plan belongs to
    breakfast: Optional[str] = None      # What the user ate/plans to eat for breakfast
    lunch: Optional[str] = None          # Lunch entry
    dinner: Optional[str] = None         # Dinner entry
    snacks: Optional[str] = None         # Snacks throughout the day
    exercise: Optional[str] = None       # Exercise/workout description
    wellness_goals: Optional[str] = None # Personal wellness goals for the day
    notes: Optional[str] = None          # Any additional freeform notes

class PlanResponse(BaseModel):
    """Schema for returning a daily plan from the database (includes auto-generated fields)."""
    id: int                              # Auto-incremented database ID
    date: date                           # The date this plan applies to
    breakfast: Optional[str]             # Breakfast entry (may be null if not set)
    lunch: Optional[str]                 # Lunch entry
    dinner: Optional[str]                # Dinner entry
    snacks: Optional[str]                # Snacks entry
    exercise: Optional[str]              # Exercise entry
    wellness_goals: Optional[str]        # Wellness goals
    notes: Optional[str]                 # Freeform notes
    created_at: datetime                 # When this plan was first created
    updated_at: datetime                 # When this plan was last modified

@router.get("/today", response_model=Optional[PlanResponse])
def get_today_plan(db: Session = Depends(get_db)):
    """Get the plan for today's date.
    Returns None (null) if no plan has been created for today yet.
    The frontend calls this when the user first opens the Planning page.
    """
    today = date.today()  # Get the server's current date (no time component)
    plan = db.query(DailyPlan).filter(DailyPlan.date == today).first()
    return plan  # Returns None if no plan exists for today

@router.get("/{plan_date}", response_model=Optional[PlanResponse])
def get_plan_by_date(plan_date: date, db: Session = Depends(get_db)):
    """Get the plan for a specific date (passed in the URL path as YYYY-MM-DD).
    Used when the user navigates to a different date using the date picker.
    """
    plan = db.query(DailyPlan).filter(DailyPlan.date == plan_date).first()
    return plan  # Returns None if no plan exists for this date

@router.post("/", response_model=PlanResponse)
def create_or_update_plan(request: PlanRequest, db: Session = Depends(get_db)):
    """Create a new plan or update an existing one for the given date (upsert).
    
    The frontend only needs to call POST — this endpoint automatically detects
    whether a plan already exists for the specified date:
      - If yes: updates all fields with the new values
      - If no: creates a brand-new plan record
    """
    
    # ── Check if a plan already exists for this date ───────────────────────────
    plan = db.query(DailyPlan).filter(DailyPlan.date == request.date).first()
    
    if plan:
        # ── UPDATE: overwrite all fields of the existing plan ─────────────────
        plan.breakfast = request.breakfast
        plan.lunch = request.lunch
        plan.dinner = request.dinner
        plan.snacks = request.snacks
        plan.exercise = request.exercise
        plan.wellness_goals = request.wellness_goals
        plan.notes = request.notes
        plan.updated_at = datetime.utcnow()  # Manually update the timestamp
    else:
        # ── CREATE: build a new DailyPlan record and add it to the session ─────
        plan = DailyPlan(
            date=request.date,
            breakfast=request.breakfast,
            lunch=request.lunch,
            dinner=request.dinner,
            snacks=request.snacks,
            exercise=request.exercise,
            wellness_goals=request.wellness_goals,
            notes=request.notes
        )
        db.add(plan)
    
    # Persist changes and refresh the object to get any DB-generated values
    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/{plan_date}")
def delete_plan(plan_date: date, db: Session = Depends(get_db)):
    """Permanently delete the daily plan for a given date.
    Returns 404 if no plan exists for that date.
    """
    # Find the plan for the given date
    plan = db.query(DailyPlan).filter(DailyPlan.date == plan_date).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Remove the plan from the database
    db.delete(plan)
    db.commit()
    
    return {"message": "Plan deleted successfully"}
