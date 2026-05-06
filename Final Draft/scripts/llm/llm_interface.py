"""
LLM Interface
Interface to Ollama for running Llama 3.2 locally.
100% OFFLINE - No API calls to external services.

Ollama exposes a local HTTP API (default: http://localhost:11434) that wraps
locally-downloaded language models. This module provides two ways to interact:

  generate()  — single-turn completion: builds one text prompt and gets one response.
                Used by the RAG pipeline for context-augmented answers.
  chat()      — multi-turn chat API: sends a list of {role, content} messages.
                Useful for maintaining conversation history (future use).

Prerequisites:
  1. Install Ollama from https://ollama.ai
  2. Start the Ollama server: ollama serve
  3. Download the model:      ollama pull llama3.2
"""

import requests
import json
from typing import Optional, Dict, List
import os

class LLMInterface:
    """Interface to a locally-running Ollama LLM instance.
    
    All HTTP requests go to the local Ollama server, which processes them
    using the downloaded model files. No internet connection is required
    after the model is downloaded.
    """
    
    def __init__(self, 
                 host: str = "http://localhost:11434",  # Ollama default port
                 model: str = "llama3.2"):              # The model tag to use
        self.host    = host
        self.model   = model
        self.api_url = f"{host}/api"  # Base URL for all Ollama API endpoints
    
    def check_connection(self) -> bool:
        """Ping the Ollama server to check if it is running and reachable.
        
        Returns True if the /api/tags endpoint responds with HTTP 200,
        False if Ollama is not running or the connection times out.
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)  # Short timeout
            return response.status_code == 200
        except:
            return False  # Any connection error = Ollama not available
    
    def list_models(self) -> List[str]:
        """Return a list of model tags available in the local Ollama installation.
        Calls the /api/tags endpoint which lists all downloaded models.
        """
        try:
            response = requests.get(f"{self.api_url}/tags")
            if response.status_code == 200:
                data = response.json()
                # Each entry in 'models' has 'name', 'size', 'modified_at', etc.
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def generate(self, 
                 prompt: str,
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 500) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        # ── Build prompt ───────────────────────────────────────────────────────────
        # If a system prompt is provided, concatenate it before the user message
        # using the standard instruction format: System → User → Assistant.
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        
        # ── Build Ollama /api/generate request payload ──────────────────────────
        payload = {
            "model":  self.model,    # Model tag e.g. 'llama3.2'
            "prompt": full_prompt,   # The complete instruction + context + question
            "stream": False,         # Disable streaming; wait for full response
            "options": {
                "temperature": temperature,   # Higher = more creative but less factual
                "num_predict": max_tokens     # Maximum output tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=60   # Llama inference can take several seconds on CPU
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()  # Extract and clean the generated text
            else:
                return f"Error: {response.status_code} - {response.text}"
        
        except Exception as e:
            return f"Error generating response: {e}"
    
    def chat(self,
             messages: List[Dict[str, str]],
             temperature: float = 0.7,
             max_tokens: int = 500) -> str:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated response
        """
        # Build the Ollama /api/chat payload with the full message history
        # Each message is a dict with 'role' ('system'/'user'/'assistant') and 'content'
        payload = {
            "model":    self.model,
            "messages": messages,    # Full conversation history for multi-turn context
            "stream":   False,       # Disable streaming; get full response at once
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                # The chat API returns the assistant's reply under result['message']['content']
                return result.get('message', {}).get('content', '').strip()
            else:
                return f"Error: {response.status_code}"
        
        except Exception as e:
            return f"Error in chat: {e}"

if __name__ == "__main__":
    # Test LLM interface
    print("\n" + "="*60)
    print("LLM Interface Test (Ollama + Llama 3.2)")
    print("="*60 + "\n")
    
    llm = LLMInterface()
    
    # Check connection
    print("Checking Ollama connection...")
    if llm.check_connection():
        print("✓ Ollama is running\n")
    else:
        print("✗ Ollama is not running")
        print("\nPlease start Ollama:")
        print("  1. Install Ollama from https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. Pull model: ollama pull llama3.2\n")
        exit(1)
    
    # List models
    print("Available models:")
    models = llm.list_models()
    for model in models:
        print(f"  - {model}")
    print()
    
    # Test generation
    print("Testing text generation...")
    print("-" * 60)
    
    system_prompt = "You are a helpful AI lifestyle assistant focused on health, nutrition, and fitness."
    user_prompt = "What are some healthy breakfast options?"
    
    print(f"System: {system_prompt}")
    print(f"User: {user_prompt}\n")
    
    response = llm.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=200
    )
    
    print(f"Assistant: {response}\n")
    
    print("="*60)
    print("✓ LLM interface test complete")
    print("="*60)
    print("\nNext step: Create RAG + LLM pipeline")
    print("  python scripts/llm/rag_llm_pipeline.py\n")
