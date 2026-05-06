"""
Chat Service - Integrates RAG+LLM pipeline with database

This is the core intelligence layer of the chatbot. It orchestrates:
  1. Translation Service: converts the user's message into English (if needed)
  2. Retrieval Engine: searches the ChromaDB vector DB for relevant context
  3. LLM Interface: sends the context + user query to Llama 3.2 via Ollama
  4. Translation Service again: translates the AI response back to the user's language

This '100% offline' pipeline means no Internet calls are made during chat —
all processing happens on the local machine.
"""

import sys
from pathlib import Path

# Add the scripts/ directory to the Python module search path so we can import
# from scripts/rag/, scripts/translation/, and scripts/llm/ as packages.
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))

from rag.retrieval_engine import RetrievalEngine
from translation.translation_service import TranslationService
from llm.llm_interface import LLMInterface
from typing import Dict, Optional

class ChatService:
    """Service for handling chat with RAG+LLM integration.
    
    This class is instantiated once when the backend starts (as a module-level singleton)
    and reused for every chat request. The initialization connects to ChromaDB and Ollama.
    If any dependency is missing (e.g., Ollama isn't running), it gracefully degrades
    by setting self.initialized = False and returning a helpful error message.
    """
    
    def __init__(self):
        try:
            # Initialize the three main pipeline components
            self.retrieval_engine = RetrievalEngine()       # Connects to ChromaDB for semantic search
            self.translation_service = TranslationService() # Handles language detection and translation
            self.llm = LLMInterface()                       # Interface to Ollama/Llama 3.2
            self.initialized = True
        except Exception as e:
            # If any component fails (e.g., ChromaDB not set up), log a warning
            # and set initialized=False so process_message returns a friendly error
            print(f"Warning: Could not initialize chat service: {e}")
            self.initialized = False
    
    def process_message(self, 
                       user_input: str,
                       domain: Optional[str] = None) -> Dict[str, str]:
        """
        Process user message through RAG+LLM pipeline.
        
        Full pipeline flow:
          1. Translate user input to English (detect language first)
          2. Search ChromaDB for relevant documents matching the English query
          3. Build a RAG-augmented prompt (context + user question) for the LLM
          4. Generate a response using Llama 3.2 via Ollama
          5. Translate the response back into the user's detected language
          6. Return the final response along with language metadata
        
        Returns:
            Dict with 'response', 'user_language', and 'english_query'
        """
        # If dependencies failed to load, return a helpful setup error
        if not self.initialized:
            return {
                'response': "Chat service not initialized. Please ensure datasets are loaded.",
                'user_language': 'en',
                'english_query': user_input
            }
        
        try:
            # ── Step 1: Detect and translate user input to English ───────────────────
            # Returns the English-translated text and the detected source language code
            english_query, user_language = self.translation_service.process_user_input(user_input)
            
            # ── Step 2: Retrieve relevant context from ChromaDB ────────────────────
            # Searches across nutrition, exercise, and/or mental health collections
            context = self.retrieval_engine.get_context_for_llm(
                english_query,
                domain=domain,     # Optional: restrict search to one domain (e.g., 'nutrition')
                n_results=3        # Retrieve the top 3 most relevant document chunks
            )
            
            # ── Step 3 & 4: Build the RAG prompt and generate the LLM response ─────────
            system_prompt = self._create_system_prompt()   # Persona/role instructions for the LLM
            full_prompt = self._create_rag_prompt(english_query, context)  # Context + question
            
            llm_response = self.llm.generate(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.7,  # Balanced creativity/factuality (0=deterministic, 1=creative)
                max_tokens=500    # Limit response length to ~500 tokens
            )
            
            # ── Step 5: Translate the LLM response back to the user's language ─────────
            # Only translate if the user wasn't speaking English to begin with
            if user_language != 'en':
                final_response = self.translation_service.process_llm_output(
                    llm_response,
                    user_language  # Target language to translate the response into
                )
            else:
                final_response = llm_response  # No translation needed for English users
            
            # Return the response along with metadata about language handling
            return {
                'response': final_response,
                'user_language': user_language,
                'english_query': english_query
            }
        
        except Exception as e:
            # Catch any pipeline errors and return a user-friendly message
            return {
                'response': f"Error processing message: {str(e)}",
                'user_language': 'en',
                'english_query': user_input
            }
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for LLM"""
        return """You are a helpful AI lifestyle assistant specializing in health, nutrition, fitness, and wellness.

Your role is to:
- Provide accurate, helpful information based on the context provided
- Give practical, actionable advice
- Be friendly and supportive
- Admit when you don't have enough information
- Only discuss topics that the user has actually asked about — do NOT bring up unrelated subjects

IMPORTANT:
- NEVER reference sources by name (e.g. do not write things like [Source 1], [Source 1 - nutrition], etc.)
- Do NOT invent or assume topics the user never mentioned
- Only answer based on what the user's message actually says
- This is for informational purposes only
- Not a substitute for professional medical, nutritional, or mental health advice
- Users should consult professionals for serious health concerns"""
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create RAG-augmented prompt"""
        return f"""Based on the following context, please answer the user's question.

CONTEXT:
{context}

USER QUESTION:
{query}

Please provide a helpful, accurate response based on the context above. If the context doesn't contain enough information, say so and provide general guidance."""
