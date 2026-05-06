"""
RAG Retrieval Engine
Performs semantic search across ChromaDB collections.
100% OFFLINE - No API calls, all processing local.

This module is the retrieval (R) step in the RAG pipeline.
It connects to the persistent ChromaDB vector database that was populated
by data_ingestion.py and exposes two public methods:

  search()             — returns a list of raw result dicts with distance scores
  get_context_for_llm() — returns results formatted as a readable context string
                           for inclusion in the LLM prompt

ChromaDB's default embedding model (sentence-transformers/all-MiniLM-L6-v2)
is used for semantic similarity — no OpenAI or external embedding API needed.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path

class RetrievalEngine:
    """Semantic search engine for RAG.
    
    Connects to the persistent ChromaDB database on disk and exposes
    methods to search across one or all domain collections.
    """
    
    # Resolve the default ChromaDB path relative to this file's location so that
    # the engine works correctly regardless of which directory Python is invoked from.
    _DEFAULT_DB_PATH: str = str(Path(__file__).parent.parent.parent / "data" / "chroma_db")

    def __init__(self, chroma_db_path: str = None):
        resolved = chroma_db_path if chroma_db_path is not None else self._DEFAULT_DB_PATH
        self.chroma_path = Path(resolved)  # Path to the ChromaDB storage folder on disk
        
        # Create a persistent ChromaDB client that reads/writes to the folder.
        # anonymized_telemetry=False ensures no usage data is sent externally.
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Pre-load the two mandatory collections (must already exist from data_ingestion.py)
        self.collections = {
            'nutrition': self.client.get_collection('nutrition_collection'),
            'exercise':  self.client.get_collection('exercise_collection'),
        }
        
        # The mental health collection is optional — only loaded if it was ingested
        try:
            self.collections['mental_health'] = self.client.get_collection('mental_health_collection')
        except:
            pass  # Silently skip if the collection doesn't exist
    
    def search(self, 
               query: str, 
               domain: Optional[str] = None,
               n_results: int = 5) -> List[Dict]:
        """
        Search for semantically relevant documents using the ChromaDB embedding model.
        
        How it works:
          - ChromaDB converts the query text into an embedding vector
          - It then finds the n_results vectors in the collection that are
            closest to the query vector (by cosine distance)
          - Lower distance = more semantically similar to the query
        
        Args:
            query: Natural language search query (in English)
            domain: Specific domain to search ('nutrition', 'exercise', 'mental_health').
                   If None, searches ALL loaded collections (fan-out search).
            n_results: Number of documents to return per collection
        
        Returns:
            List of result dicts: {'domain', 'document', 'metadata', 'distance'}
            Sorted by distance ascending (best match first).
        """
        results = []
        
        # Determine which collections to search:
        # If a specific domain is given, only search that one.
        # Otherwise fan out across all loaded collections.
        if domain and domain in self.collections:
            collections_to_search = {domain: self.collections[domain]}
        else:
            collections_to_search = self.collections  # Search all domains
        
        # Query each selected collection and collect the results
        for domain_name, collection in collections_to_search.items():
            try:
                search_results = collection.query(
                    query_texts=[query],   # ChromaDB embeds this text automatically
                    n_results=n_results
                )
                
                # Unpack the ChromaDB result structure into flat dicts for easier use
                for i in range(len(search_results['documents'][0])):
                    results.append({
                        'domain':    domain_name,
                        'document':  search_results['documents'][0][i],   # The matched text chunk
                        'metadata':  search_results['metadatas'][0][i],   # Source metadata (row_id, etc.)
                        'distance':  search_results['distances'][0][i] if 'distances' in search_results else None
                    })
            except Exception as e:
                print(f"Error searching {domain_name}: {e}")
        
        # Sort all results from all queried collections by distance (best first)
        if results and results[0]['distance'] is not None:
            results.sort(key=lambda x: x['distance'])
        
        # Trim to n_results total (in case multiple collections were searched)
        return results[:n_results]
    
    def get_context_for_llm(self, 
                           query: str, 
                           domain: Optional[str] = None,
                           n_results: int = 3) -> str:
        """
        Retrieve documents and format them as a plain-text context block for the LLM prompt.
        
        Each retrieved document is labelled with a source index and its domain name
        so the LLM can cite where the information came from.
        
        Example output:
            [Source 1 - nutrition]
            Recipe: Oatmeal | Calories: 150 | ...
            
            [Source 2 - exercise]
            Exercise: Push-up | Body part: chest | ...
        
        Args:
            query:     User query (in English) to search for
            domain:    Specific domain to restrict the search to (optional)
            n_results: How many top results to include in the context
        
        Returns:
            Formatted multi-line string ready to inject into the LLM prompt.
        """
        results = self.search(query, domain, n_results)
        
        if not results:
            return "No relevant information found."  # LLM handles this case gracefully
        
        # Build the context string with numbered source labels
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Source {i} - {result['domain']}]")  # Source header
            context_parts.append(result['document'])                       # Document content
            context_parts.append("")   # Blank line separator between sources
        
        return "\n".join(context_parts)

if __name__ == "__main__":
    # Example usage
    engine = RetrievalEngine()
    
    print("RAG Retrieval Engine - Test Queries\n")
    print("="*60)
    
    # Test query 1
    query1 = "high protein breakfast recipes"
    print(f"\nQuery: {query1}")
    print("-" * 60)
    context = engine.get_context_for_llm(query1, domain='nutrition', n_results=2)
    print(context)
    
    # Test query 2
    query2 = "chest exercises for beginners"
    print(f"\n\nQuery: {query2}")
    print("-" * 60)
    context = engine.get_context_for_llm(query2, domain='exercise', n_results=2)
    print(context)
    
    print("\n" + "="*60)
    print("✓ Retrieval engine test complete\n")
