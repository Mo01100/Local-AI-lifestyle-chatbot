"""
Chat API Endpoints

This module defines all HTTP API routes related to the chat feature.
It handles:
  - Receiving user messages and returning AI responses
  - Managing conversations (create, list, retrieve, delete)
  - Integrating with the ChatService which runs the RAG+LLM pipeline
  - Saving all messages and conversations to the SQLite database
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database.db import get_db
from ..database.models import Conversation, Message
from ..services.chat_service import ChatService

# Create a FastAPI router with the /api/chat URL prefix; all routes in this file will be mounted here
router = APIRouter(prefix="/api/chat", tags=["chat"])
# Instantiate the chat service singleton that connects to the RAG+LLM pipeline
chat_service = ChatService()

# ─── Pydantic Models (request/response schemas validated automatically by FastAPI) ───

class ChatRequest(BaseModel):
    """Schema for incoming chat requests from the frontend."""
    message: str                         # The user's text message
    conversation_id: Optional[int] = None  # If set, continues an existing conversation; if None, starts a new one
    domain: Optional[str] = None         # Optional domain to restrict RAG search: 'nutrition', 'exercise', etc.

class ChatResponse(BaseModel):
    """Schema for the response returned after processing a chat message."""
    conversation_id: int  # The ID of the conversation (existing or newly created)
    message: str          # The AI-generated response text
    language: str         # The detected language of the user's message

class ConversationResponse(BaseModel):
    """Schema for a conversation summary (shown in the conversation list)."""
    id: int                # Unique conversation ID
    title: str             # Auto-generated title derived from the first user message
    created_at: datetime   # When the conversation was first created
    updated_at: datetime   # When the conversation was last updated
    message_count: int     # Total number of messages in the conversation

class MessageResponse(BaseModel):
    """Schema for a single message within a conversation."""
    id: int              # Unique message ID
    role: str            # Either 'user' or 'assistant'
    content: str         # The full text content of the message
    language: str        # Language code the message was stored in
    timestamp: datetime  # When the message was created

@router.post("/", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a chat message and get AI response.
    
    This is the core chat endpoint. It:
    1. Retrieves or creates the conversation record
    2. Saves the user's raw message to the database
    3. Sends the message through the RAG+LLM pipeline via ChatService
    4. Saves the AI's response to the database
    5. Auto-generates a conversation title from the first message
    """
    
    # ── Step 1: Get or create a conversation record ────────────────────────────
    if request.conversation_id:
        # Look up an existing conversation by its ID
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if not conversation:
            # Return 404 if the given conversation ID doesn't exist
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # No conversation_id provided → start a brand-new conversation with a placeholder title
        conversation = Conversation(title="New Conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)  # Refresh to get the auto-assigned database ID
    
    # ── Step 2: Save the user's message to the database ────────────────────────
    user_message = Message(
        conversation_id=conversation.id,
        role="user",        # Mark this as a user-side message
        content=request.message,
        language="auto"    # Language will be detected by the translation service
    )
    db.add(user_message)
    
    # ── Step 3: Process the message through the RAG+LLM pipeline ────────────────
    # ChatService translates the input, retrieves RAG context, and generates a response
    result = chat_service.process_message(request.message, request.domain)
    
    # ── Step 4: Save the AI assistant's response to the database ────────────────
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",             # Mark this as an assistant-side message
        content=result['response'],
        language=result['user_language']  # Store the detected user language for the response
    )
    db.add(assistant_message)
    
    # ── Step 5: Auto-title the conversation from the first user message ──────────
    if conversation.title == "New Conversation":
        # Take up to 5 words from the user's first message as the conversation title
        title_words = request.message.split()[:5]
        conversation.title = " ".join(title_words) + ("..." if len(title_words) == 5 else "")
    
    # Update the conversation's last-modified timestamp and persist everything
    conversation.updated_at = datetime.utcnow()
    db.commit()
    
    # Return the response to the frontend
    return ChatResponse(
        conversation_id=conversation.id,
        message=result['response'],
        language=result['user_language']
    )

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    """Get all conversations, ordered by most recently updated first.
    Used by the frontend to populate the conversation sidebar/history page.
    """
    # Query all conversations, sorted newest-first by the updated_at timestamp
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    
    # Build the response list, including the computed message_count for each conversation
    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages)  # Count messages via the SQLAlchemy relationship
        )
        for conv in conversations
    ]

@router.get("/conversations/{conversation_id}", response_model=List[MessageResponse])
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages in a specific conversation.
    Used when the user clicks on a past conversation to view its full message history.
    """
    # Find the conversation by its ID; return 404 if not found
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Return all messages in the conversation in their stored order
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,         # 'user' or 'assistant'
            content=msg.content,
            language=msg.language,
            timestamp=msg.timestamp
        )
        for msg in conversation.messages
    ]

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete a conversation"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}
