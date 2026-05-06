"""
Data Ingestion Script for RAG
Ingests cleaned datasets into ChromaDB vector database.
100% OFFLINE - Uses local sentence-transformers for embeddings.

This script is step 2 in the RAG setup (run after rag_setup.py).
It reads cleaned CSV files from data/cleaned/ and adds them to the
ChromaDB vector database, where each row is converted into an embedded
text document for semantic search.

Document format:
  Each CSV row is serialised as:  "Column1: Value1 | Column2: Value2 | ..."
  ChromaDB then embeds this string using sentence-transformers locally.

Domains ingested:
  1. nutrition_collection  <- nutrition_cleaned.csv + recipes_cleaned.csv
  2. exercise_collection   <- exercise_cleaned.csv
  3. mental_health_collection <- mental_health_cleaned.csv (optional)

Usage:
  python scripts/rag/data_ingestion.py
  (requires rag_setup.py to have been run first)
"""

import chromadb
from chromadb.config import Settings
import pandas as pd
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import json

class DataIngestion:
    """Ingest cleaned data into ChromaDB for RAG.
    
    Reads cleaned CSV files and upserts their rows into the appropriate
    ChromaDB collection as embedded text documents. The ChromaDB client
    uses sentence-transformers locally to create the embeddings —
    no internet or OpenAI API is needed.
    """
    
    def __init__(self, 
                 cleaned_data_path: str = 'data/cleaned',  # Folder with cleaned CSVs
                 chroma_db_path:    str = 'data/chroma_db'):  # ChromaDB on-disk path
        self.data_path   = Path(cleaned_data_path)
        self.chroma_path = Path(chroma_db_path)
        
        # Connect to the existing ChromaDB database created by rag_setup.py.
        # anonymized_telemetry=False keeps all data 100% local.
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(anonymized_telemetry=False)
        )
    
    def ingest_nutrition_data(self) -> None:
        """Ingest nutrition and recipe data."""
        print("Ingesting nutrition data...")
        
        # Load cleaned nutrition data
        nutrition_file = self.data_path / 'nutrition_cleaned.csv'
        recipes_file = self.data_path / 'recipes_cleaned.csv'
        
        collection = self.client.get_or_create_collection('nutrition_collection')
        
        # Ingest nutrition data
        if nutrition_file.exists():
            df = pd.read_csv(nutrition_file)
            self._ingest_dataframe(df, collection, 'nutrition', max_rows=1000)
        
        # Ingest recipes data
        if recipes_file.exists():
            df = pd.read_csv(recipes_file)
            self._ingest_recipes(df, collection, max_rows=5000)
        
        print(f"✓ Nutrition collection: {collection.count()} documents\n")
    
    def ingest_exercise_data(self) -> None:
        """Ingest exercise data."""
        print("Ingesting exercise data...")
        
        exercise_file = self.data_path / 'exercise_cleaned.csv'
        megagym_file = self.data_path / 'megaGymDataset.csv'
        
        collection = self.client.get_or_create_collection('exercise_collection')
        
        if exercise_file.exists():
            df = pd.read_csv(exercise_file)
            self._ingest_exercises(df, collection)
            print(f"  ✓ Ingested exercise_cleaned.csv")
            
        if megagym_file.exists():
            df_mega = pd.read_csv(megagym_file)
            df_mega.columns = df_mega.columns.str.lower().str.replace(' ', '_')
            self._ingest_exercises(df_mega, collection)
            print(f"  ✓ Ingested megaGymDataset.csv")
            
        if not exercise_file.exists() and not megagym_file.exists():
            print("  ⚠ No exercise data found\n")
            return
        
        print(f"✓ Exercise collection: {collection.count()} documents\n")
    
    def ingest_mental_health_data(self) -> None:
        """Ingest mental health data (optional)."""
        print("Ingesting mental health data...")
        
        mh_file = self.data_path / 'mental_health_cleaned.csv'
        
        if not mh_file.exists():
            print("  ⚠ No mental health data found (optional)\n")
            return
        
        df = pd.read_csv(mh_file)
        collection = self.client.get_or_create_collection('mental_health_collection')
        
        self._ingest_dataframe(df, collection, 'mental_health', max_rows=1000)
        
        print(f"✓ Mental health collection: {collection.count()} documents\n")
    
    def _ingest_dataframe(self, df: pd.DataFrame, collection, prefix: str, max_rows: int = None) -> None:
        """Generic ingestion: convert any DataFrame's rows into ChromaDB documents.
        
        Each row becomes one document in the collection. The document text is
        built by joining all non-null column values as 'Column: Value' pairs
        separated by ' | ', which is human-readable when retrieved by the LLM.
        
        Args:
            df:         Cleaned DataFrame to ingest
            collection: Target ChromaDB collection object
            prefix:     String prefix for the document IDs (e.g. 'nutrition', 'mental_health')
            max_rows:   If set, only ingest the first N rows (for large datasets)
        """
        if max_rows:
            df = df.head(max_rows)  # Limit rows to avoid overwhelming memory
        
        documents = []  # List of text strings to embed
        metadatas = []  # List of metadata dicts (stored alongside each document)
        ids       = []  # Unique string ID per document
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"  Processing {prefix}"):
            # Build text by joining all non-null column values
            # pd.notna() skips NaN cells so they don't pollute the document
            doc_text = " | ".join([f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])])
            
            documents.append(doc_text)
            metadatas.append({'source': prefix, 'row_id': idx})  # Minimal metadata
            ids.append(f"{prefix}_{idx}")  # Format: 'nutrition_0', 'nutrition_1', ...
        
        # ── Batch insert into ChromaDB ──────────────────────────────────────────────
        # ChromaDB recommends batching large inserts to avoid memory pressure.
        # batch_size=100 is a safe default for most machines.
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )
    
    def _ingest_recipes(self, df: pd.DataFrame, collection, max_rows: int = None) -> None:
        """Ingest recipe data with structured, human-readable labelling.
        
        Unlike the generic _ingest_dataframe, this method arranges the recipe
        fields in a logical narrative order (Recipe -> Ingredients -> Instructions
        -> Calories -> Cooking time) so the retrieved context reads naturally
        when injected into the LLM prompt.
        """
        if max_rows:
            df = df.head(max_rows)
        
        documents = []
        metadatas = []
        ids       = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="  Processing recipes"):
            # Build a structured, human-readable recipe document
            doc_parts = []
            
            if 'name' in row and pd.notna(row['name']):
                doc_parts.append(f"Recipe: {row['name']}")
            
            if 'ingredients' in row and pd.notna(row['ingredients']):
                doc_parts.append(f"Ingredients: {row['ingredients']}")
            
            if 'steps' in row and pd.notna(row['steps']):
                doc_parts.append(f"Instructions: {row['steps']}")
            
            if 'calories' in row and pd.notna(row['calories']):
                doc_parts.append(f"Calories: {row['calories']}")
            
            if 'minutes' in row and pd.notna(row['minutes']):
                doc_parts.append(f"Cooking time: {row['minutes']} minutes")
            
            doc_text = " | ".join(doc_parts)
            
            documents.append(doc_text)
            metadatas.append({
                'source':    'recipe',
                'recipe_id': idx,
                'name':      str(row.get('name', ''))[:100]  # Truncate long names for metadata
            })
            ids.append(f"recipe_{idx}")
        
        # Batch insert into ChromaDB
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )
    
    def _ingest_exercises(self, df: pd.DataFrame, collection) -> None:
        """Ingest exercise data with special formatting."""
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="  Processing exercises"):
            # Create rich exercise document
            doc_parts = []
            
            # Get exercise name
            name_col = next((col for col in ['exercise_name', 'name', 'title'] if col in row), None)
            if name_col and pd.notna(row[name_col]):
                doc_parts.append(f"Exercise: {row[name_col]}")

            # Add description
            if 'desc' in row and pd.notna(row['desc']):
                doc_parts.append(f"Description: {row['desc']}")
                
            # Add type
            if 'type' in row and pd.notna(row['type']):
                doc_parts.append(f"Type: {row['type']}")
            
            # Add body part
            bp_col = next((col for col in ['bodypart', 'body_part'] if col in row), None)
            if bp_col and pd.notna(row[bp_col]):
                doc_parts.append(f"Body part: {row[bp_col]}")
            
            # Add target muscle
            if 'target' in row and pd.notna(row['target']):
                doc_parts.append(f"Target: {row['target']}")
            
            # Add equipment
            if 'equipment' in row and pd.notna(row['equipment']):
                doc_parts.append(f"Equipment: {row['equipment']}")
            
            # Add difficulty
            diff_col = next((col for col in ['level', 'difficulty'] if col in row), None)
            if diff_col and pd.notna(row[diff_col]):
                doc_parts.append(f"Difficulty: {row[diff_col]}")
            
            # Add category
            if 'category' in row and pd.notna(row['category']):
                doc_parts.append(f"Category: {row['category']}")
                
            # Add rating
            if 'rating' in row and pd.notna(row['rating']) and float(row['rating']) > 0:
                doc_parts.append(f"Rating: {row['rating']}")
            
            doc_text = " | ".join(doc_parts)
            
            documents.append(doc_text)
            metadatas.append({
                'source': 'exercise',
                'exercise_id': idx,
                'name': str(row.get(name_col, ''))[:100] if name_col else ''
            })
            ids.append(f"exercise_{idx}")
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )
    
    def verify_ingestion(self) -> None:
        """Verify data ingestion."""
        print("Verifying data ingestion...")
        
        collections = self.client.list_collections()
        
        summary = {}
        for collection in collections:
            count = collection.count()
            summary[collection.name] = count
            print(f"  {collection.name}: {count} documents")
        
        # Save summary
        with open('data/ingestion_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n✓ Verification complete\n")
    
    def run(self) -> None:
        """Execute complete data ingestion."""
        print("\n" + "="*60)
        print("Data Ingestion for RAG (100% Offline)")
        print("="*60 + "\n")
        
        self.ingest_nutrition_data()
        self.ingest_exercise_data()
        self.ingest_mental_health_data()
        self.verify_ingestion()
        
        print("="*60)
        print("✓ Data ingestion complete!")
        print("="*60)
        print("\nNext step: Setup translation layer")
        print("  python scripts/translation/install_translation_models.py\n")

if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run()
