"""
RAG Setup Script
Initializes ChromaDB vector database for RAG (Retrieval-Augmented Generation).
100% OFFLINE - No API calls, all embeddings generated locally.

This is the first step in building the RAG pipeline.
It creates the persistent ChromaDB database on disk and sets up the
three domain collections that will store embedded documents:

  nutrition_collection     -> food & recipe data
  exercise_collection      -> gym exercise data
  mental_health_collection -> mental wellness data (optional)

Run this script ONCE before data_ingestion.py.
The database persists at data/chroma_db/ until deleted.

Usage:
  python scripts/rag/rag_setup.py
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
import json

class RAGSetup:
    """Setup ChromaDB vector database for offline RAG.
    
    Creates the database directory, initialises the ChromaDB client,
    and creates the three domain collections. Run run() to execute the
    full setup pipeline.
    """
    
    def __init__(self, persist_directory: str = 'data/chroma_db'):
        self.persist_dir = Path(persist_directory)  # Folder where ChromaDB writes its files
        self.persist_dir.mkdir(parents=True, exist_ok=True)  # Create if absent
        
        self.client      = None  # Populated by initialize_client()
        self.collections = {}    # Maps domain name -> Collection object
    
    def initialize_client(self) -> None:
        """Initialize ChromaDB client with persistent storage."""
        print("Initializing ChromaDB client...")
        
        # Create persistent client (100% offline)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(
                anonymized_telemetry=False,  # Disable telemetry for privacy
                allow_reset=True
            )
        )
        
        print(f"✓ ChromaDB initialized at: {self.persist_dir}\n")
    
    def create_collections(self) -> None:
        """Create separate collections for each domain."""
        print("Creating vector database collections...")
        
        collection_configs = {
            'nutrition': {
                'name': 'nutrition_collection',
                'metadata': {'description': 'Nutrition and food recipe data'}
            },
            'exercise': {
                'name': 'exercise_collection',
                'metadata': {'description': 'Exercise and fitness data'}
            },
            'mental_health': {
                'name': 'mental_health_collection',
                'metadata': {'description': 'Mental health and wellness data (optional)'}
            }
        }
        
        for domain, config in collection_configs.items():
            try:
                # Get or create collection
                collection = self.client.get_or_create_collection(
                    name=config['name'],
                    metadata=config['metadata']
                )
                self.collections[domain] = collection
                print(f"  ✓ Created collection: {config['name']}")
            except Exception as e:
                print(f"  ⚠ Error creating {config['name']}: {e}")
        
        print()
    
    def verify_setup(self) -> None:
        """Verify RAG setup is complete."""
        print("Verifying RAG setup...")
        
        # List all collections
        collections = self.client.list_collections()
        print(f"  Total collections: {len(collections)}")
        
        for collection in collections:
            count = collection.count()
            print(f"  - {collection.name}: {count} documents")
        
        print("\n✓ RAG setup verification complete\n")
    
    def save_config(self) -> None:
        """Save RAG configuration."""
        config = {
            'persist_directory': str(self.persist_dir),
            'collections': {
                domain: {
                    'name': coll.name,
                    'count': coll.count()
                }
                for domain, coll in self.collections.items()
            },
            'embedding_model': 'sentence-transformers (local)',
            'privacy': '100% offline, no API calls'
        }
        
        config_path = Path('data') / 'rag_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, indent=2, fp=f)
        
        print(f"✓ Configuration saved to: {config_path}\n")
    
    def run(self) -> None:
        """Execute complete RAG setup."""
        print("\n" + "="*60)
        print("RAG Setup with ChromaDB (100% Offline)")
        print("="*60 + "\n")
        
        self.initialize_client()
        self.create_collections()
        self.verify_setup()
        self.save_config()
        
        print("="*60)
        print("✓ RAG setup complete!")
        print("="*60)
        print("\nNext step: Ingest cleaned data into ChromaDB")
        print("  python scripts/rag/data_ingestion.py\n")

if __name__ == "__main__":
    setup = RAGSetup()
    setup.run()
