"""
Exercise Data Cleaning Script
Cleans and processes gym exercise dataset.
100% OFFLINE - No API calls, complete data privacy.

This script reads raw exercise CSVs from data/raw/exercise/, applies a series
of cleaning transformations, generates visualisation charts, and saves the
cleaned dataset to data/cleaned/exercise_cleaned.csv.

Cleaning steps performed:
  1. Load any CSV file found under data/raw/exercise/ (auto-detected)
  2. Analyse and visualise data quality (missing values, dtypes)
  3. Remove duplicate rows
  4. Standardise column names (lowercase, underscores)
  5. Normalise difficulty levels to: beginner / intermediate / advanced
  6. Lowercase body-part, equipment, and target-muscle columns
  7. Fill missing equipment values with 'bodyweight'
  8. Derive a 'category' column (cardio vs. strength) via heuristics
  9. Save cleaned CSV and all visualisation PNGs

Usage:
  python scripts/cleaning/clean_exercise_data.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class ExerciseDataCleaner:
    """Clean and process exercise datasets with comprehensive visualizations.
    
    Creates output directories on instantiation and stores the loaded DataFrame
    as self.exercise_df for use across the pipeline methods.
    """
    
    def __init__(self, raw_data_path: str = 'data/raw', output_path: str = 'data/cleaned'):
        self.raw_path  = Path(raw_data_path) / 'exercise'  # Source: data/raw/exercise/
        self.output_path = Path(output_path)               # Destination: data/cleaned/
        self.viz_path  = Path('outputs/visualizations/exercise')  # Charts output directory
        
        # Ensure all output directories exist before writing any files
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.viz_path.mkdir(parents=True, exist_ok=True)
        
        self.exercise_df = None  # Populated by load_data()
    
    def load_data(self) -> None:
        """Load raw exercise CSV data from data/raw/exercise/.
        
        Searches recursively for any .csv file, filtering out files that are
        already cleaned (name contains 'cleaned') to avoid re-processing.
        on_bad_lines='skip' tolerates malformed rows without crashing.
        """
        print("Loading exercise dataset...")
        
        # Look specifically for the megaGymDataset.csv file
        exercise_files = list(self.raw_path.rglob('megaGymDataset.csv'))
        
        if exercise_files:
            print(f"  Found file: {exercise_files[0].name}")
            # Use the specific CSV found; skip malformed rows rather than crashing
            self.exercise_df = pd.read_csv(exercise_files[0], on_bad_lines='skip')
            print(f"  [OK] Loaded {len(self.exercise_df)} exercises\n")
        else:
            print("  [WARNING] No exercise dataset (megaGymDataset.csv) found\n")
    
    def analyze_data_quality(self) -> None:
        """Analyze data quality."""
        if self.exercise_df is None:
            return
        
        print("--- Exercise Dataset Analysis ---")
        print(f"Shape: {self.exercise_df.shape}")
        print(f"Columns: {list(self.exercise_df.columns)}")
        print(f"\nMissing values:")
        print(self.exercise_df.isnull().sum())
        print(f"\nData types:")
        print(self.exercise_df.dtypes)
        print()
        
        # Missing data visualization
        plt.figure(figsize=(10, 6))
        missing_data = self.exercise_df.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        if len(missing_data) > 0:
            missing_data.plot(kind='bar', color='coral')
            plt.title('Missing Values by Column', fontsize=14, fontweight='bold')
            plt.xlabel('Columns')
            plt.ylabel('Missing Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(self.viz_path / 'missing_data.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  Saved: missing_data.png")
    
    def clean_data(self) -> pd.DataFrame:
        """Apply all cleaning transformations to the exercise DataFrame.
        
        Transformations:
          - Drop duplicate rows
          - Standardise column names to snake_case
          - Rename 'title' column to 'exercise_name' if present
          - Strip and title-case exercise names; drop blank entries
          - Map difficulty/level to standard tiers (beginner/intermediate/advanced)
          - Lowercase body part, equipment, and target muscle columns
          - Fill null equipment with 'bodyweight'
          - Add a 'category' column derived from body part and equipment heuristics
        """
        if self.exercise_df is None:
            print("[WARNING] No exercise data to clean")
            return None
        
        print("Cleaning exercise data...")
        df = self.exercise_df.copy()  # Never mutate the original loaded data
        initial_rows = len(df)
        
        # ── Step 1: Remove duplicate rows ────────────────────────────────────────
        df = df.drop_duplicates()
        print(f"  Removed {initial_rows - len(df)} duplicate rows")
        
        # ── Step 2: Standardise column names to lowercase snake_case ────────────────
        # Ensures consistent column access regardless of source file formatting
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # ── Step 3: Normalise exercise name column ───────────────────────────────
        if 'title' in df.columns:
            df.rename(columns={'title': 'exercise_name'}, inplace=True)  # Standardise name
        
        if 'exercise_name' in df.columns or 'name' in df.columns:
            name_col = 'exercise_name' if 'exercise_name' in df.columns else 'name'
            df[name_col] = df[name_col].str.strip().str.title()  # Strip whitespace and title-case
            df = df[df[name_col].str.len() > 0]  # Remove rows with empty names
        
        # ── Step 4: Standardise difficulty levels to three canonical tiers ──────────
        if 'level' in df.columns or 'difficulty' in df.columns:
            diff_col = 'level' if 'level' in df.columns else 'difficulty'
            df[diff_col] = df[diff_col].str.lower().str.strip()
            
            # Map common variant names to the three canonical difficulty labels
            difficulty_mapping = {
                'beginner':     'beginner',
                'intermediate': 'intermediate',
                'advanced':     'advanced',
                'expert':       'advanced',    # 'expert' is treated as 'advanced'
                'easy':         'beginner',    # 'easy' maps to 'beginner'
                'medium':       'intermediate',
                'hard':         'advanced'
            }
            # Unmapped values fall back to 'intermediate' via fillna
            df[diff_col] = df[diff_col].map(difficulty_mapping).fillna('intermediate')
        
        # ── Step 5: Normalise categorical text columns ─────────────────────────────
        if 'bodypart' in df.columns or 'body_part' in df.columns:
            bp_col = 'bodypart' if 'bodypart' in df.columns else 'body_part'
            df[bp_col] = df[bp_col].str.lower().str.strip()
        
        if 'equipment' in df.columns:
            df['equipment'] = df['equipment'].str.lower().str.strip()
            df['equipment'] = df['equipment'].fillna('bodyweight')  # Assume bodyweight if unspecified
        
        if 'target' in df.columns:
            df['target'] = df['target'].str.lower().str.strip()
        
        # ── Step 6: Derive exercise category (cardio vs. strength) ────────────────
        # Applied row-wise using a helper method based on body part and equipment clues
        df['category'] = df.apply(self._categorize_exercise, axis=1)
        
        print(f"[OK] Exercise data cleaned: {len(df)} rows\n")
        return df
    
    def _categorize_exercise(self, row) -> str:
        """Derive the exercise category ('cardio' or 'strength') for a single row.
        
        Uses a keyword search on the body-part and equipment fields:
          - If body part is 'cardio', or equipment is a cardio machine -> 'cardio'
          - Otherwise defaults to 'strength'
        """
        if 'bodypart' in row:
            bp = str(row['bodypart']).lower()
            if 'cardio' in bp:
                return 'cardio'
            elif any(word in bp for word in ['chest', 'back', 'shoulders', 'arms', 'legs']):
                return 'strength'
        
        if 'equipment' in row:
            eq = str(row['equipment']).lower()
            # Cardio machines typically used for sustained aerobic exercise
            if 'treadmill' in eq or 'bike' in eq or 'elliptical' in eq:
                return 'cardio'
        
        return 'strength'  # Default category when no cardio signals are found
    
    def create_visualizations(self, df: pd.DataFrame) -> None:
        """Generate comprehensive visualizations."""
        if df is None:
            return
        
        print("Creating visualizations...")
        
        # Body part distribution
        if 'bodypart' in df.columns or 'body_part' in df.columns:
            bp_col = 'bodypart' if 'bodypart' in df.columns else 'body_part'
            self._plot_distribution(df, bp_col, 'Body Part Distribution', 'bodypart_distribution.png')
        
        # Equipment distribution
        if 'equipment' in df.columns:
            self._plot_distribution(df, 'equipment', 'Equipment Distribution', 'equipment_distribution.png')
        
        # Difficulty distribution
        if 'level' in df.columns or 'difficulty' in df.columns:
            diff_col = 'level' if 'level' in df.columns else 'difficulty'
            self._plot_pie_chart(df, diff_col, 'Difficulty Level Distribution', 'difficulty_distribution.png')
        
        # Target muscle distribution
        if 'target' in df.columns:
            self._plot_distribution(df, 'target', 'Target Muscle Distribution', 'target_muscle_distribution.png', top_n=15)
        
        # Category distribution
        self._plot_pie_chart(df, 'category', 'Exercise Category Distribution', 'category_distribution.png')
        
        # Muscle group coverage heatmap
        self._create_muscle_coverage_heatmap(df)
        
        print("[OK] All visualizations created\n")
    
    def _plot_distribution(self, df: pd.DataFrame, column: str, title: str, filename: str, top_n: int = 10) -> None:
        """Create bar chart for distribution."""
        plt.figure(figsize=(12, 6))
        
        value_counts = df[column].value_counts().head(top_n)
        value_counts.plot(kind='barh', color='skyblue', edgecolor='black')
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Count')
        plt.ylabel(column.replace('_', ' ').title())
        plt.tight_layout()
        plt.savefig(self.viz_path / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {filename}")
    
    def _plot_pie_chart(self, df: pd.DataFrame, column: str, title: str, filename: str) -> None:
        """Create pie chart for distribution."""
        plt.figure(figsize=(10, 8))
        
        value_counts = df[column].value_counts()
        colors = sns.color_palette('Set3', len(value_counts))
        
        plt.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.viz_path / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {filename}")
    
    def _create_muscle_coverage_heatmap(self, df: pd.DataFrame) -> None:
        """Create heatmap showing muscle group coverage by difficulty."""
        if 'bodypart' not in df.columns and 'body_part' not in df.columns:
            return
        
        bp_col = 'bodypart' if 'bodypart' in df.columns else 'body_part'
        diff_col = 'level' if 'level' in df.columns else ('difficulty' if 'difficulty' in df.columns else None)
        
        if diff_col is None:
            return
        
        # Create crosstab
        coverage = pd.crosstab(df[bp_col], df[diff_col])
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(coverage, annot=True, fmt='d', cmap='YlOrRd', linewidths=0.5)
        plt.title('Muscle Group Coverage by Difficulty Level', fontsize=14, fontweight='bold')
        plt.xlabel('Difficulty Level')
        plt.ylabel('Body Part')
        plt.tight_layout()
        plt.savefig(self.viz_path / 'muscle_coverage_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  Saved: muscle_coverage_heatmap.png")
    
    def save_cleaned_data(self, df: pd.DataFrame) -> None:
        """Save cleaned dataset."""
        if df is None:
            return
        
        print("Saving cleaned data...")
        df.to_csv(self.output_path / 'exercise_cleaned.csv', index=False)
        print(f"  Saved: exercise_cleaned.csv ({len(df)} rows)\n")
    
    def run(self) -> None:
        """Execute complete cleaning pipeline."""
        print("\n" + "="*60)
        print("Exercise Data Cleaning Pipeline (100% Offline)")
        print("="*60 + "\n")
        
        self.load_data()
        self.analyze_data_quality()
        
        cleaned_df = self.clean_data()
        self.create_visualizations(cleaned_df)
        self.save_cleaned_data(cleaned_df)
        
        print("="*60)
        print("[OK] Exercise data cleaning complete!")
        print("="*60)
        print(f"\nCleaned data saved to: {self.output_path}")
        print(f"Visualizations saved to: {self.viz_path}")
        print("\nNext step: Run mental health data cleaning (optional)")
        print("  python scripts/cleaning/clean_mental_health_data.py\n")

if __name__ == "__main__":
    cleaner = ExerciseDataCleaner()
    cleaner.run()
