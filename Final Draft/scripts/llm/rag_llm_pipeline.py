"""
RAG + LLM Pipeline
Complete end-to-end pipeline: Translation → RAG → LLM → Translation
100% OFFLINE - No external API calls.

This script glues together the three main components of the chatbot pipeline:
  1. TranslationService  — detects and translates the user's language to/from English
  2. RetrievalEngine     — searches ChromaDB for relevant health/exercise/nutrition facts
  3. LLMInterface        — sends the context+query to Ollama (Llama 3.2) and gets a response

The full flow for each user message:
  User Input (any language)
    → Translate to English
    → Retrieve top-N relevant documents from ChromaDB
    → Build a RAG-augmented prompt (context + question)
    → Send to Llama 3.2 via Ollama
    → Translate response back to user's language
    → Return final response

Usage (standalone test):
  python scripts/llm/rag_llm_pipeline.py
  Requires Ollama running: ollama serve && ollama pull llama3.2
"""

import sys
from pathlib import Path

# Add the parent scripts/ directory to the Python path so that
# intra-package imports (rag.retrieval_engine, translation.translation_service, etc.) work
# when this file is run directly from the command line.
sys.path.append(str(Path(__file__).parent.parent))

from rag.retrieval_engine import RetrievalEngine
from translation.translation_service import TranslationService
from llm.llm_interface import LLMInterface
from typing import Optional, Dict

class RAGLLMPipeline:
    """Complete pipeline for multi-language RAG-powered chatbot."""
    
    def __init__(self):
        print("Initializing RAG + LLM Pipeline...")
        
        # ── Initialise each component ───────────────────────────────────────
        # Each component is instantiated once and reused for every query
        self.retrieval_engine    = RetrievalEngine()     # Connects to ChromaDB on disk
        self.translation_service = TranslationService()  # Loads Argos Translate cache
        self.llm                 = LLMInterface()        # Points to Ollama HTTP API
        
        # Fail early if Ollama isn't running — the rest of the pipeline is useless without it
        if not self.llm.check_connection():
            raise ConnectionError("Ollama is not running. Please start Ollama first.")
        
        print("\u2713 Pipeline initialized\n")
    
    def process_query(self, 
                     user_input: str,
                     domain: Optional[str] = None,
                     n_context_results: int = 3) -> Dict[str, str]:
        """
        Process user query through complete pipeline.
        
        Pipeline flow:
        1. Detect user language
        2. Translate to English (if needed)
        3. Retrieve relevant context from RAG
        4. Generate LLM response with context
        5. Translate response back to user language
        
        Args:
            user_input: User's query in any language
            domain: Specific domain to search ('nutrition', 'exercise', 'mental_health')
            n_context_results: Number of RAG results to include
        
        Returns:
            Dict with response and metadata
        """
        # ── Step 1 & 2: Detect language and translate user input to English ────────────
        # The LLM only understands English, so all user input must be translated first.
        # process_user_input() auto-detects the language using character-set heuristics.
        print(f"User input: {user_input}")
        english_query, user_language = self.translation_service.process_user_input(user_input)
        print(f"Detected language: {user_language}")
        
        if user_language != 'en':
            print(f"Translated to English: {english_query}")
        
        # ── Step 3: Retrieve relevant context from ChromaDB (the RAG step) ────────────
        # The English query is used to do a semantic search (embedding-based) across
        # the ChromaDB collections. The returned context is pre-formatted text
        # labelled with source domain headers (nutrition / exercise / mental_health).
        print(f"Retrieving context from RAG...")
        context = self.retrieval_engine.get_context_for_llm(
            english_query,
            domain=domain,
            n_results=n_context_results
        )
        print(f"Retrieved {n_context_results} context items")
        
        # ── Step 4: Generate the LLM response via Ollama ──────────────────────────
        # Two prompts are sent:
        #   - system_prompt: defines the assistant persona and safety guidelines
        #   - full_prompt:   the RAG-augmented user question with injected context
        print("Generating LLM response...")
        system_prompt = self._create_system_prompt()
        full_prompt   = self._create_rag_prompt(english_query, context)
        
        llm_response = self.llm.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.7,    # Moderate creativity; lower = more factual
            max_tokens=500      # Keep responses concise
        )
        
        # ── Step 5: Translate LLM response back to user's language ────────────────
        # If the user asked in Arabic, French, etc., translate the English response back.
        if user_language != 'en':
            print(f"Translating response to {user_language}...")
            final_response = self.translation_service.process_llm_output(
                llm_response,
                user_language
            )
        else:
            final_response = llm_response  # No translation needed for English users
        
        # Return the final response plus metadata for debugging
        return {
            'response':         final_response,   # The answer in the user's language
            'user_language':    user_language,    # Detected language code
            'english_query':    english_query,    # Question translated to English
            'english_response': llm_response,     # Raw English LLM response (before translation)
            'context_used':     context           # The RAG context that was injected into the prompt
        }
    
    def _create_system_prompt(self) -> str:
        """Build the system prompt that defines the AI assistant's persona and guardrails.
        
        This prompt is sent as the 'system' role in the Ollama chat API.
        It tells the model WHO it is and HOW it should respond, setting boundaries
        around medical advice and establishing a helpful, health-focused persona.
        """
        return """You are a helpful AI lifestyle assistant specializing in health, nutrition, fitness, and wellness.

Your role is to:
- Provide accurate, helpful information based on the context provided
- Give practical, actionable advice
- Be friendly and supportive
- Cite information from the context when relevant
- Admit when you don't have enough information

IMPORTANT:
- This is for informational purposes only
- Not a substitute for professional medical, nutritional, or mental health advice
- Users should consult professionals for serious health concerns"""
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Build the RAG-augmented user prompt by injecting retrieved context before the question.
        
        The context block contains the top-N documents retrieved from ChromaDB,
        formatted with source labels. Placing the context before the question
        follows the standard RAG instruction format and helps the LLM ground
        its answer in the retrieved facts rather than hallucinating.
        """
        return f"""Based on the following context, please answer the user's question.

CONTEXT:
{context}

USER QUESTION:
{query}

Please provide a helpful, accurate response based on the context above. If the context doesn't contain enough information, say so and provide general guidance."""
    
    def chat_loop(self) -> None:
        """Run an interactive command-line chat loop for testing the full pipeline.
        
        Supports two types of input:
          - 'domain:<name>' command: restrict subsequent searches to nutrition/exercise/mental_health
          - 'domain:all' command:    search all domains (default)
          - 'quit':                  exit the loop
          - Any other text:          processed as a user health question
        """
        print("\n" + "="*60)
        print("RAG + LLM Pipeline - Interactive Chat")
        print("="*60)
        print("\nType 'quit' to exit")
        print("Type 'domain:nutrition', 'domain:exercise', or 'domain:mental_health' to set domain")
        print("Type 'domain:all' to search all domains\n")
        
        current_domain = None  # None = search all domains; set to a string to restrict
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue  # Skip blank lines
                
                if user_input.lower() == 'quit':
                    print("\nGoodbye!")
                    break
                
                # ── Domain switcher command ───────────────────────────────────
                # Allows the tester to narrow or widen the RAG search domain interactively
                if user_input.lower().startswith('domain:'):
                    domain_name = user_input.split(':')[1].strip()
                    if domain_name == 'all':
                        current_domain = None  # Search all collections
                        print("\u2713 Searching all domains")
                    elif domain_name in ['nutrition', 'exercise', 'mental_health']:
                        current_domain = domain_name
                        print(f"\u2713 Domain set to: {domain_name}")
                    else:
                        print("\u26a0 Invalid domain. Use: nutrition, exercise, mental_health, or all")
                    continue  # Don't treat this as a question
                
                # ── Process a regular user health question ────────────────────────
                print("\n" + "-"*60)
                result = self.process_query(user_input, domain=current_domain)
                print("-"*60)
                print(f"\nAssistant: {result['response']}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")  # Log and continue so the loop doesn't crash

if __name__ == "__main__":
    try:
        pipeline = RAGLLMPipeline()
        pipeline.chat_loop()
    except ConnectionError as e:
        print(f"\n✗ {e}")
        print("\nPlease start Ollama:")
        print("  1. Install Ollama from https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. Pull model: ollama pull llama3.2\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
