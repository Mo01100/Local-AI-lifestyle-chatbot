"""
Data Quality Analysis Script
Analyzes all three datasets to determine if they are cleaned or not.
Provides detailed quality metrics and recommendations.

This script scans data/raw/ for CSV files across the three main domains
(nutrition, recipes, exercise) and reports quality metrics for each one.
It is used as a diagnostic tool to decide whether to run the cleaning scripts
before ingesting data into ChromaDB.

Cleanliness Score breakdown:
  Start at 100. Deductions:
  - Missing values:         -20
  - Duplicate rows:         -15
  - Negative numeric vals:  -10 per column
  - Whitespace in strings:  -5  per column
  Score is clamped to a minimum of 0.

Usage:
  python scripts/analyze_data_quality.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataQualityAnalyzer:
    """Analyze data quality for all datasets.
    
    Instantiated with the root path of the raw data directory.
    Call run() to execute the full analysis and print the report.
    """
    
    def __init__(self, raw_data_path: str = 'data/raw'):
        self.raw_path = Path(raw_data_path)  # Root directory containing nutrition/, recipes/, exercise/
        self.results = {}  # Stores analysis results keyed by dataset identifier
    
    def analyze_dataset(self, file_path: Path, dataset_name: str) -> Dict:
        """Analyze a single CSV file for data quality issues.
        
        Checks:
          1. Missing values (NaN/None) per column
          2. Duplicate rows
          3. Negative values in numeric columns (usually indicates dirty data)
          4. Leading/trailing whitespace in string columns
        
        Returns a dict summarising counts, types, and the overall cleanliness score.
        """
        try:
            df = pd.read_csv(file_path)  # Load the CSV into a DataFrame for analysis
            
            analysis = {
                'file_name': file_path.name,
                'dataset_name': dataset_name,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'missing_values': {},
                'duplicate_rows': 0,
                'data_types': {},
                'quality_issues': [],
                'is_cleaned': True,    # Optimistically assume clean; set False when issues are found
                'cleanliness_score': 100  # Start at 100 and deduct points for each problem
            }
            
            # ── Check 1: Missing values ───────────────────────────────────────────
            # isnull().sum() counts NaN/None per column
            missing = df.isnull().sum()
            analysis['missing_values'] = {col: int(count) for col, count in missing.items() if count > 0}
            
            if len(analysis['missing_values']) > 0:
                analysis['quality_issues'].append(f"Missing values in {len(analysis['missing_values'])} columns")
                analysis['is_cleaned'] = False
                analysis['cleanliness_score'] -= 20  # Deduct 20 points for any missing values
            
            # ── Check 2: Duplicate rows ───────────────────────────────────────────
            # duplicated() returns a boolean Series; sum() counts True values
            duplicates = df.duplicated().sum()
            analysis['duplicate_rows'] = int(duplicates)
            
            if duplicates > 0:
                analysis['quality_issues'].append(f"{duplicates} duplicate rows found")
                analysis['is_cleaned'] = False
                analysis['cleanliness_score'] -= 15  # Deduct 15 points for duplicates
            
            # ── Check 3: Negative values in numeric columns ────────────────────────
            # Negatives in columns like 'calories' or 'reps' almost always signal bad data
            analysis['data_types'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    analysis['quality_issues'].append(f"{col}: {negative_count} negative values (potential errors)")
                    analysis['is_cleaned'] = False
                    analysis['cleanliness_score'] -= 10  # Deduct 10 per column with negatives
            
            # ── Check 4: Leading/trailing whitespace in text columns ─────────────────
            # Whitespace causes lookup failures (e.g., " Apple" != "Apple")
            text_cols = df.select_dtypes(include=['object']).columns
            for col in text_cols:
                sample = df[col].dropna().head(100)  # Check the first 100 non-null values for speed
                if len(sample) > 0:
                    # Check for mixed case (useful for informational display)
                    has_mixed_case = any(str(val) != str(val).lower() and str(val) != str(val).upper() for val in sample)
                    # Check if any value has a leading or trailing space
                    has_whitespace = any(str(val) != str(val).strip() for val in sample)
                    
                    if has_whitespace:
                        analysis['quality_issues'].append(f"{col}: Contains leading/trailing whitespace")
                        analysis['is_cleaned'] = False
                        analysis['cleanliness_score'] -= 5  # Deduct 5 per column with whitespace issues
            
            # Clamp score to [0, 100] — prevents negative scores from cascading issues
            analysis['cleanliness_score'] = max(0, analysis['cleanliness_score'])
            
            return analysis
            
        except Exception as e:
            return {
                'file_name': file_path.name,
                'dataset_name': dataset_name,
                'error': str(e),
                'is_cleaned': False,
                'cleanliness_score': 0
            }
    
    def analyze_all_datasets(self) -> None:
        """Analyze all three main datasets."""
        print("\n" + "="*70)
        print("DATA QUALITY ANALYSIS - Three Main Datasets")
        print("="*70 + "\n")
        
        # Dataset 1: Nutrition Data
        print("📊 Dataset 1: NUTRITION DATA")
        print("-" * 70)
        nutrition_files = list((self.raw_path / 'nutrition').glob('*.csv'))
        if nutrition_files:
            for file in nutrition_files:
                result = self.analyze_dataset(file, "Nutrition")
                self.results[f"nutrition_{file.stem}"] = result
                self._print_analysis(result)
        else:
            print("⚠️  No nutrition dataset found\n")
        
        # Dataset 2: Recipes Data
        print("\n📊 Dataset 2: RECIPES DATA")
        print("-" * 70)
        recipes_path = self.raw_path / 'recipes'
        recipe_files = ['RAW_recipes.csv', 'RAW_interactions.csv', 'PP_recipes.csv']
        
        for recipe_file in recipe_files:
            file_path = recipes_path / recipe_file
            if file_path.exists():
                result = self.analyze_dataset(file_path, "Recipes")
                self.results[f"recipes_{recipe_file.replace('.csv', '')}"] = result
                self._print_analysis(result)
            else:
                print(f"⚠️  {recipe_file} not found")
        
        # Dataset 3: Exercise Data
        print("\n📊 Dataset 3: EXERCISE DATA")
        print("-" * 70)
        exercise_files = list((self.raw_path / 'exercise').glob('*.csv'))
        if exercise_files:
            for file in exercise_files:
                result = self.analyze_dataset(file, "Exercise")
                self.results[f"exercise_{file.stem}"] = result
                self._print_analysis(result)
        else:
            print("⚠️  No exercise dataset found\n")
    
    def _print_analysis(self, result: Dict) -> None:
        """Print analysis results for a single dataset."""
        if 'error' in result:
            print(f"❌ {result['file_name']}: ERROR - {result['error']}\n")
            return
        
        print(f"\n📁 File: {result['file_name']}")
        print(f"   Rows: {result['total_rows']:,} | Columns: {result['total_columns']}")
        
        # Cleanliness status
        if result['is_cleaned']:
            print(f"   ✅ STATUS: CLEANED (Score: {result['cleanliness_score']}/100)")
        else:
            print(f"   ❌ STATUS: NOT CLEANED (Score: {result['cleanliness_score']}/100)")
        
        # Quality issues
        if result['quality_issues']:
            print(f"   ⚠️  Quality Issues:")
            for issue in result['quality_issues']:
                print(f"      - {issue}")
        
        # Missing values summary
        if result['missing_values']:
            total_missing = sum(result['missing_values'].values())
            print(f"   📉 Missing Values: {total_missing:,} total across {len(result['missing_values'])} columns")
        
        # Duplicates
        if result['duplicate_rows'] > 0:
            print(f"   🔄 Duplicate Rows: {result['duplicate_rows']:,}")
        
        print()
    
    def generate_summary(self) -> None:
        """Generate overall summary."""
        print("\n" + "="*70)
        print("SUMMARY - Data Cleaning Status")
        print("="*70 + "\n")
        
        # Group by dataset type
        nutrition_results = {k: v for k, v in self.results.items() if k.startswith('nutrition')}
        recipes_results = {k: v for k, v in self.results.items() if k.startswith('recipes')}
        exercise_results = {k: v for k, v in self.results.items() if k.startswith('exercise')}
        
        self._print_dataset_summary("Nutrition Dataset", nutrition_results)
        self._print_dataset_summary("Recipes Dataset", recipes_results)
        self._print_dataset_summary("Exercise Dataset", exercise_results)
        
        # Overall recommendation
        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70 + "\n")
        
        all_cleaned = all(r.get('is_cleaned', False) for r in self.results.values() if 'error' not in r)
        
        if all_cleaned:
            print("✅ All datasets appear to be cleaned!")
            print("   You can proceed with RAG setup and data ingestion.")
        else:
            print("❌ Some datasets need cleaning!")
            print("\n   Run the following cleaning scripts:")
            
            if not all(r.get('is_cleaned', False) for r in nutrition_results.values() if 'error' not in r):
                print("   1. python scripts/cleaning/clean_nutrition_data.py")
            
            if not all(r.get('is_cleaned', False) for r in recipes_results.values() if 'error' not in r):
                print("   2. python scripts/cleaning/clean_nutrition_data.py  # Also cleans recipes")
            
            if not all(r.get('is_cleaned', False) for r in exercise_results.values() if 'error' not in r):
                print("   3. python scripts/cleaning/clean_exercise_data.py")
        
        print("\n" + "="*70 + "\n")
    
    def _print_dataset_summary(self, name: str, results: Dict) -> None:
        """Print summary for a dataset group."""
        if not results:
            print(f"📊 {name}: No data found")
            return
        
        total_files = len(results)
        cleaned_files = sum(1 for r in results.values() if r.get('is_cleaned', False))
        avg_score = np.mean([r.get('cleanliness_score', 0) for r in results.values()])
        
        status = "✅ CLEANED" if cleaned_files == total_files else "❌ NEEDS CLEANING"
        
        print(f"📊 {name}:")
        print(f"   Status: {status}")
        print(f"   Files Analyzed: {total_files}")
        print(f"   Clean Files: {cleaned_files}/{total_files}")
        print(f"   Average Quality Score: {avg_score:.1f}/100")
        print()
    
    def run(self) -> None:
        """Execute complete analysis."""
        self.analyze_all_datasets()
        self.generate_summary()

if __name__ == "__main__":
    analyzer = DataQualityAnalyzer()
    analyzer.run()
