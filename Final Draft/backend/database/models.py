"""
Database Models for AI Lifestyle Chatbot
SQLAlchemy models for SQLite database.

This file defines the ORM (Object-Relational Mapping) classes that map directly
to database tables. SQLAlchemy uses these class definitions to:
  - Create the tables automatically on first startup (via Base.metadata.create_all)
  - Let you query and manipulate database records using Python objects

Tables defined here:
  - conversations: Chat session metadata
  - messages:      Individual messages within a conversation
  - daily_plans:   Daily meal/exercise/wellness plans per calendar date
  - reminders:     User-created reminders with optional recurrence
  - settings:      Key-value store for user preferences and accessibility settings
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Base is the declarative base class all models inherit from.
# It gives SQLAlchemy the information needed to create tables and map Python classes to DB rows.
Base = declarative_base()

class Conversation(Base):
    """Stores metadata about a single chat session (a group of related messages).
    Each conversation has an auto-generated title derived from the first user message.
    Messages are linked via a one-to-many relationship.
    """
    __tablename__ = 'conversations'  # The actual SQL table name
    
    id = Column(Integer, primary_key=True)           # Auto-incrementing unique ID
    title = Column(String(200))                      # Human-readable title (up to 200 characters)
    created_at = Column(DateTime, default=datetime.utcnow)                          # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto-updates on change
    
    # One conversation has many messages; deleting a conversation cascades to all its messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Stores a single chat message (either from the user or the AI assistant).
    Messages belong to a Conversation and are never shared across conversations.
    """
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)                        # Auto-incrementing unique ID
    conversation_id = Column(Integer, ForeignKey('conversations.id'))  # Links back to the parent conversation
    role = Column(String(20))    # 'user' for human messages, 'assistant' for AI responses
    content = Column(Text)       # Full message text (no length limit, stored as TEXT in SQLite)
    language = Column(String(10))  # Language code of the message (e.g., 'en', 'ar', 'es')
    timestamp = Column(DateTime, default=datetime.utcnow)  # When this message was created
    
    # Back-reference to the parent Conversation object
    conversation = relationship("Conversation", back_populates="messages")

class DailyPlan(Base):
    """Stores one daily health plan entry per calendar date.
    Each date can only have one plan (enforced by the unique=True constraint on the date column).
    All meal and activity fields are optional — the user can fill in as much or as little as they want.
    """
    __tablename__ = 'daily_plans'
    
    id = Column(Integer, primary_key=True)                # Auto-incrementing unique ID
    date = Column(Date, unique=True, nullable=False)       # One plan per date (unique prevents duplicates)
    breakfast = Column(Text)        # What the user ate/plans for breakfast
    lunch = Column(Text)            # Lunch
    dinner = Column(Text)           # Dinner
    snacks = Column(Text)           # Any snacks throughout the day
    exercise = Column(Text)         # Exercise activity description
    wellness_goals = Column(Text)   # Personal wellness or health goals for the day
    notes = Column(Text)            # Any freeform notes
    created_at = Column(DateTime, default=datetime.utcnow)                           # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Auto-updated on change

class Reminder(Base):
    """Stores a single reminder entry created by the user.
    Reminders can be one-time or recurring and can be marked as completed.
    """
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)                    # Auto-incrementing unique ID
    title = Column(String(200), nullable=False)               # Reminder name (required)
    description = Column(Text)                                # Optional longer description
    category = Column(String(50))   # Type: 'meal', 'exercise', 'medication', or 'custom'
    due_datetime = Column(DateTime, nullable=False)           # When the reminder should trigger
    is_recurring = Column(Boolean, default=False)             # True if this reminder repeats
    recurrence_pattern = Column(String(50))  # How often it repeats: 'daily', 'weekly', 'monthly'
    is_completed = Column(Boolean, default=False)             # Completion status
    created_at = Column(DateTime, default=datetime.utcnow)   # When this reminder was created

class Setting(Base):
    """Stores user application settings as key-value pairs.
    All values are serialized to strings so any type of setting can be stored
    in the same table (e.g., booleans become 'true'/'false', integers become their string repr).
    """
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)                # Auto-incrementing ID
    key = Column(String(100), unique=True, nullable=False)  # Setting name (unique, e.g., 'theme')
    value = Column(Text)                                  # Setting value stored as a string
