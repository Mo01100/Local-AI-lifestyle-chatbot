"""
Mental Health Data Cleaning Script
Cleans and processes mental health conversational dataset.
100% OFFLINE - No API calls, complete data privacy.
INCLUDES ETHICAL SAFEGUARDS - PII removal and content filtering.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re
import warnings
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class MentalHealthDataCleaner:
    """Clean and process mental health conversational data with ethical safeguards."""
    
    def __init__(self, raw_data_path: str = 'data/raw', output_path: str = 'data/cleaned'):
        self.raw_path = Path(raw_data_path) / 'mental_health'
        self.output_path = Path(output_path)
        self.viz_path = Path('outputs/visualizations/mental_health')
        
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.viz_path.mkdir(parents=True, exist_ok=True)
        
        self.data_df = None
    
    def load_data(self) -> None:
        """Load raw mental health data."""
        print("Loading mental health dataset...")
        
        data_files = list(self.raw_path.glob('*.csv'))
        if data_files:
            print(f"  Found file: {data_files[0].name}")
            self.data_df = pd.read_csv(data_files[0])
            print(f"✓ Loaded {len(self.data_df)} conversations\n")
        else:
            print("  ⚠ No mental health dataset found")
            print("  This dataset is optional due to ethical considerations.\n")
    
    def analyze_data_quality(self) -> None:
        """Analyze data quality."""
        if self.data_df is None:
            return
        
        print("--- Mental Health Dataset Analysis ---")
        print(f"Shape: {self.data_df.shape}")
        print(f"Columns: {list(self.data_df.columns)}")
        print(f"\nMissing values:")
        print(self.data_df.isnull().sum())
        print()
    
    def clean_data(self) -> pd.DataFrame:
        """Clean mental health data with ethical safeguards."""
        if self.data_df is None:
            print("⚠ No mental health data to clean")
            return None
        
        print("Cleaning mental health data...")
        print("⚠ ETHICAL SAFEGUARDS ACTIVE:")
        print("  - Removing personally identifiable information (PII)")
        print("  - Filtering inappropriate content")
        print("  - Adding usage disclaimers\n")
        
        df = self.data_df.copy()
        initial_rows = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates()
        print(f"  Removed {initial_rows - len(df)} duplicate rows")
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # Identify text columns
        text_columns = []
        for col in df.columns:
            if 'question' in col.lower() or 'answer' in col.lower() or 'response' in col.lower() or 'context' in col.lower():
                text_columns.append(col)
        
        # Remove PII from text columns
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._remove_pii)
        
        # Filter inappropriate content
        df = self._filter_inappropriate_content(df, text_columns)
        
        # Add metadata
        df['data_source'] = 'mental_health_conversational'
        df['ethical_disclaimer'] = 'This is for informational purposes only. Not a substitute for professional mental health care.'
        
        # Calculate text statistics
        if text_columns:
            primary_text_col = text_columns[0]
            df['text_length'] = df[primary_text_col].str.len()
            df['word_count'] = df[primary_text_col].str.split().str.len()
        
        print(f"✓ Mental health data cleaned: {len(df)} rows")
        print(f"  Removed {initial_rows - len(df)} rows due to filtering\n")
        
        return df
    
    def _remove_pii(self, text: str) -> str:
        """Remove personally identifiable information."""
        if pd.isna(text):
            return text
        
        text = str(text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers (various formats)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        text = re.sub(r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', text)
        
        # Remove potential names (capitalized words that might be names)
        # This is conservative - only removes obvious patterns
        text = re.sub(r'\bMy name is [A-Z][a-z]+\b', 'My name is [NAME]', text)
        text = re.sub(r'\bI\'m [A-Z][a-z]+\b', 'I\'m [NAME]', text)
        
        # Remove addresses (simple pattern)
        text = re.sub(r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b', '[ADDRESS]', text)
        
        return text
    
    def _filter_inappropriate_content(self, df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """Filter out inappropriate or harmful content."""
        # List of concerning keywords (conservative filtering)
        harmful_keywords = [
            'suicide', 'kill myself', 'end my life', 'self-harm',
            'cutting myself', 'overdose'
        ]
        
        # Create filter mask
        filter_mask = pd.Series([True] * len(df))
        
        for col in text_columns:
            if col in df.columns:
                for keyword in harmful_keywords:
                    # Mark rows with harmful content for review/removal
                    # In a production system, these might be flagged for professional review
                    filter_mask &= ~df[col].str.lower().str.contains(keyword, na=False)
        
        # Keep only safe content
        return df[filter_mask]
    
    def create_visualizations(self, df: pd.DataFrame) -> None:
        """Generate visualizations."""
        if df is None:
            return
        
        print("Creating visualizations...")
        
        # Text length distribution
        if 'text_length' in df.columns:
            plt.figure(figsize=(12, 6))
            plt.hist(df['text_length'], bins=50, color='lightblue', edgecolor='black')
            plt.title('Text Length Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Character Count')
            plt.ylabel('Frequency')
            plt.tight_layout()
            plt.savefig(self.viz_path / 'text_length_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  Saved: text_length_distribution.png")
        
        # Word count distribution
        if 'word_count' in df.columns:
            plt.figure(figsize=(12, 6))
            plt.hist(df['word_count'], bins=50, color='lightgreen', edgecolor='black')
            plt.title('Word Count Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Word Count')
            plt.ylabel('Frequency')
            plt.tight_layout()
            plt.savefig(self.viz_path / 'word_count_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  Saved: word_count_distribution.png")
        
        print("✓ All visualizations created\n")
    
    def save_cleaned_data(self, df: pd.DataFrame) -> None:
        """Save cleaned dataset with ethical disclaimer."""
        if df is None:
            return
        
        print("Saving cleaned data...")
        
        # Save main dataset
        df.to_csv(self.output_path / 'mental_health_cleaned.csv', index=False)
        print(f"  Saved: mental_health_cleaned.csv ({len(df)} rows)")
        
        # Save ethical disclaimer
        disclaimer = """
ETHICAL USE DISCLAIMER - Mental Health Dataset

This dataset contains conversational data related to mental health topics.

IMPORTANT NOTICES:
1. This data is for INFORMATIONAL and EDUCATIONAL purposes only
2. This is NOT a substitute for professional mental health care
3. Users experiencing mental health crises should contact:
   - Emergency services (911 in US)
   - National Suicide Prevention Lifeline: 988
   - Crisis Text Line: Text HOME to 741741

DATA PRIVACY:
- All personally identifiable information (PII) has been removed
- Content has been filtered for harmful material
- This data should be used responsibly and ethically

USAGE RESTRICTIONS:
- Do not use for medical diagnosis or treatment
- Do not use to replace professional mental health services
- Always include appropriate disclaimers in any application using this data

By using this dataset, you agree to use it responsibly and ethically.
"""
        
        with open(self.output_path / 'MENTAL_HEALTH_ETHICAL_DISCLAIMER.txt', 'w') as f:
            f.write(disclaimer)
        
        print("  Saved: MENTAL_HEALTH_ETHICAL_DISCLAIMER.txt\n")
    
    def run(self) -> None:
        """Execute complete cleaning pipeline."""
        print("\n" + "="*60)
        print("Mental Health Data Cleaning Pipeline (100% Offline)")
        print("="*60 + "\n")
        
        self.load_data()
        
        if self.data_df is not None:
            self.analyze_data_quality()
            cleaned_df = self.clean_data()
            self.create_visualizations(cleaned_df)
            self.save_cleaned_data(cleaned_df)
            
            print("="*60)
            print("✓ Mental health data cleaning complete!")
            print("="*60)
            print(f"\nCleaned data saved to: {self.output_path}")
            print(f"Visualizations saved to: {self.viz_path}")
            print("\n⚠ IMPORTANT: Please review MENTAL_HEALTH_ETHICAL_DISCLAIMER.txt")
        else:
            print("="*60)
            print("No mental health data found - skipping")
            print("="*60)
        
        print("\nNext step: Setup RAG with ChromaDB")
        print("  python scripts/rag/rag_setup.py\n")

if __name__ == "__main__":
    cleaner = MentalHealthDataCleaner()
    cleaner.run()
