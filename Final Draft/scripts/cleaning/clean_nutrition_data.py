"""
Nutrition Data Cleaning Script
Cleans and processes nutrition and recipe datasets.
100% OFFLINE - No API calls, complete data privacy.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class NutritionDataCleaner:
    """Clean and process nutrition datasets with comprehensive visualizations."""
    
    def __init__(self, raw_data_path: str = 'data/raw', output_path: str = 'data/cleaned'):
        self.raw_path = Path(raw_data_path)
        self.output_path = Path(output_path)
        self.viz_path = Path('outputs/visualizations/nutrition')
        
        # Create output directories
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.viz_path.mkdir(parents=True, exist_ok=True)
        
        self.nutrition_df = None
        self.recipes_df = None
        self.interactions_df = None
        
    def load_data(self) -> None:
        """Load raw nutrition and recipe data."""
        print("Loading raw datasets...")
        
        # Load nutrition dataset - search recursively in subdirectories
        nutrition_files = list((self.raw_path / 'nutrition').rglob('*.csv'))
        if nutrition_files:
            # Filter out already cleaned files
            nutrition_files = [f for f in nutrition_files if 'cleaned' not in f.name.lower()]
            if nutrition_files:
                print(f"  Found nutrition file: {nutrition_files[0].name}")
                self.nutrition_df = pd.read_csv(nutrition_files[0], on_bad_lines='skip')
            else:
                print("  ⚠ No nutrition dataset found")
        else:
            print("  ⚠ No nutrition dataset found")
        
        # Load recipes dataset - search recursively
        recipes_path = self.raw_path / 'recipes'
        recipe_files = list(recipes_path.rglob('RAW_recipes.csv'))
        if recipe_files:
            print(f"  Found recipes file: {recipe_files[0].name}")
            self.recipes_df = pd.read_csv(recipe_files[0])
        
        interaction_files = list(recipes_path.rglob('RAW_interactions.csv'))
        if interaction_files:
            print(f"  Found interactions file: {interaction_files[0].name}")
            self.interactions_df = pd.read_csv(interaction_files[0])
        
        print("✓ Data loading complete\n")
    
    def analyze_data_quality(self) -> None:
        """Analyze and visualize data quality issues."""
        print("Analyzing data quality...")
        
        if self.nutrition_df is not None:
            print("\n--- Nutrition Dataset ---")
            print(f"Shape: {self.nutrition_df.shape}")
            print(f"Columns: {list(self.nutrition_df.columns)}")
            print(f"\nMissing values:")
            print(self.nutrition_df.isnull().sum())
            
            # Visualize missing data
            self._plot_missing_data(self.nutrition_df, 'nutrition_missing_data.png')
        
        if self.recipes_df is not None:
            print("\n--- Recipes Dataset ---")
            print(f"Shape: {self.recipes_df.shape}")
            print(f"Columns: {list(self.recipes_df.columns)}")
            print(f"\nMissing values:")
            print(self.recipes_df.isnull().sum())
            
            # Visualize missing data
            self._plot_missing_data(self.recipes_df, 'recipes_missing_data.png')
        
        print("\n✓ Data quality analysis complete\n")
    
    def _plot_missing_data(self, df: pd.DataFrame, filename: str) -> None:
        """Create heatmap of missing data."""
        plt.figure(figsize=(12, 8))
        sns.heatmap(df.isnull(), cbar=True, cmap='viridis', yticklabels=False)
        plt.title('Missing Data Heatmap', fontsize=16, fontweight='bold')
        plt.xlabel('Columns', fontsize=12)
        plt.ylabel('Rows', fontsize=12)
        plt.tight_layout()
        plt.savefig(self.viz_path / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {filename}")
    
    def clean_nutrition_data(self) -> pd.DataFrame:
        """Clean nutrition dataset."""
        if self.nutrition_df is None:
            print("⚠ No nutrition data to clean")
            return None
        
        print("Cleaning nutrition data...")
        df = self.nutrition_df.copy()
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        print(f"  Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing values in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                # Fill with median for nutritional values
                df[col].fillna(df[col].median(), inplace=True)
        
        # Remove rows with negative nutritional values (data errors)
        for col in numeric_cols:
            if (df[col] < 0).any():
                df = df[df[col] >= 0]
        
        # Standardize text columns (if any)
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            df[col] = df[col].str.strip().str.lower()
        
        print(f"✓ Nutrition data cleaned: {len(df)} rows\n")
        return df
    
    def clean_recipes_data(self) -> pd.DataFrame:
        """Clean recipes dataset."""
        if self.recipes_df is None:
            print("⚠ No recipes data to clean")
            return None
        
        print("Cleaning recipes data...")
        df = self.recipes_df.copy()
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates(subset=['id'] if 'id' in df.columns else None)
        print(f"  Removed {initial_rows - len(df)} duplicate rows")
        
        # Clean recipe names
        if 'name' in df.columns:
            df['name'] = df['name'].str.strip()
            df = df[df['name'].str.len() > 0]  # Remove empty names
        
        # Clean and parse ingredients
        if 'ingredients' in df.columns:
            df['ingredients'] = df['ingredients'].apply(self._clean_ingredients)
            df['ingredient_count'] = df['ingredients'].apply(len)
        
        # Clean steps/instructions
        if 'steps' in df.columns:
            df['steps'] = df['steps'].apply(self._clean_steps)
            df['step_count'] = df['steps'].apply(len)
        
        # Handle cooking time
        if 'minutes' in df.columns:
            # Remove unrealistic cooking times (> 24 hours or < 1 minute)
            df = df[(df['minutes'] >= 1) & (df['minutes'] <= 1440)]
        
        # Parse nutrition information
        if 'nutrition' in df.columns:
            nutrition_df = df['nutrition'].apply(self._parse_nutrition)
            df = pd.concat([df, nutrition_df], axis=1)
        
        print(f"✓ Recipes data cleaned: {len(df)} rows\n")
        return df
    
    def _clean_ingredients(self, ingredients_str: str) -> List[str]:
        """Parse and clean ingredients list."""
        try:
            # Remove brackets and quotes, split by comma
            ingredients = str(ingredients_str).replace('[', '').replace(']', '').replace("'", "").split(',')
            return [ing.strip() for ing in ingredients if ing.strip()]
        except:
            return []
    
    def _clean_steps(self, steps_str: str) -> List[str]:
        """Parse and clean cooking steps."""
        try:
            steps = str(steps_str).replace('[', '').replace(']', '').replace("'", "").split(',')
            return [step.strip() for step in steps if step.strip()]
        except:
            return []
    
    def _parse_nutrition(self, nutrition_str: str) -> pd.Series:
        """Parse nutrition information from string format."""
        try:
            # Nutrition format: [calories, total_fat, sugar, sodium, protein, saturated_fat, carbs]
            values = str(nutrition_str).replace('[', '').replace(']', '').split(',')
            values = [float(v.strip()) for v in values]
            
            return pd.Series({
                'calories': values[0] if len(values) > 0 else np.nan,
                'total_fat_pdv': values[1] if len(values) > 1 else np.nan,
                'sugar_pdv': values[2] if len(values) > 2 else np.nan,
                'sodium_pdv': values[3] if len(values) > 3 else np.nan,
                'protein_pdv': values[4] if len(values) > 4 else np.nan,
                'saturated_fat_pdv': values[5] if len(values) > 5 else np.nan,
                'carbs_pdv': values[6] if len(values) > 6 else np.nan
            })
        except:
            return pd.Series({
                'calories': np.nan,
                'total_fat_pdv': np.nan,
                'sugar_pdv': np.nan,
                'sodium_pdv': np.nan,
                'protein_pdv': np.nan,
                'saturated_fat_pdv': np.nan,
                'carbs_pdv': np.nan
            })
    
    def create_visualizations(self, nutrition_df: pd.DataFrame, recipes_df: pd.DataFrame) -> None:
        """Generate comprehensive visualizations."""
        print("Creating visualizations...")
        
        if nutrition_df is not None:
            self._visualize_nutrition_distribution(nutrition_df)
        
        if recipes_df is not None:
            self._visualize_recipe_statistics(recipes_df)
            self._visualize_cooking_complexity(recipes_df)
            self._visualize_nutrition_correlations(recipes_df)
        
        print("✓ All visualizations created\n")
    
    def _visualize_nutrition_distribution(self, df: pd.DataFrame) -> None:
        """Create nutrition distribution visualizations."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:6]  # First 6 numeric columns
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for idx, col in enumerate(numeric_cols):
            if idx < len(axes):
                axes[idx].hist(df[col].dropna(), bins=50, color='skyblue', edgecolor='black')
                axes[idx].set_title(f'{col} Distribution', fontweight='bold')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.viz_path / 'nutrition_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  Saved: nutrition_distributions.png")
    
    def _visualize_recipe_statistics(self, df: pd.DataFrame) -> None:
        """Visualize recipe statistics."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Cooking time distribution
        if 'minutes' in df.columns:
            axes[0, 0].hist(df['minutes'], bins=50, color='coral', edgecolor='black')
            axes[0, 0].set_title('Cooking Time Distribution', fontweight='bold')
            axes[0, 0].set_xlabel('Minutes')
            axes[0, 0].set_ylabel('Frequency')
        
        # Ingredient count distribution
        if 'ingredient_count' in df.columns:
            axes[0, 1].hist(df['ingredient_count'], bins=30, color='lightgreen', edgecolor='black')
            axes[0, 1].set_title('Ingredient Count Distribution', fontweight='bold')
            axes[0, 1].set_xlabel('Number of Ingredients')
            axes[0, 1].set_ylabel('Frequency')
        
        # Calorie distribution
        if 'calories' in df.columns:
            axes[1, 0].hist(df['calories'].dropna(), bins=50, color='gold', edgecolor='black')
            axes[1, 0].set_title('Calorie Distribution', fontweight='bold')
            axes[1, 0].set_xlabel('Calories')
            axes[1, 0].set_ylabel('Frequency')
        
        # Step count distribution
        if 'step_count' in df.columns:
            axes[1, 1].hist(df['step_count'], bins=30, color='plum', edgecolor='black')
            axes[1, 1].set_title('Cooking Steps Distribution', fontweight='bold')
            axes[1, 1].set_xlabel('Number of Steps')
            axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.viz_path / 'recipe_statistics.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  Saved: recipe_statistics.png")
    
    def _visualize_cooking_complexity(self, df: pd.DataFrame) -> None:
        """Visualize relationship between cooking complexity metrics."""
        if 'minutes' in df.columns and 'ingredient_count' in df.columns and 'calories' in df.columns:
            fig = px.scatter(
                df.sample(min(5000, len(df))),  # Sample for performance
                x='ingredient_count',
                y='minutes',
                color='calories',
                size='calories',
                title='Recipe Complexity: Ingredients vs Cooking Time vs Calories',
                labels={
                    'ingredient_count': 'Number of Ingredients',
                    'minutes': 'Cooking Time (minutes)',
                    'calories': 'Calories'
                },
                color_continuous_scale='Viridis'
            )
            fig.write_html(self.viz_path / 'recipe_complexity_interactive.html')
            print("  Saved: recipe_complexity_interactive.html")
    
    def _visualize_nutrition_correlations(self, df: pd.DataFrame) -> None:
        """Create correlation heatmap for nutritional values."""
        nutrition_cols = ['calories', 'total_fat_pdv', 'sugar_pdv', 'sodium_pdv', 
                         'protein_pdv', 'saturated_fat_pdv', 'carbs_pdv']
        
        available_cols = [col for col in nutrition_cols if col in df.columns]
        
        if len(available_cols) > 1:
            corr_matrix = df[available_cols].corr()
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                       center=0, square=True, linewidths=1)
            plt.title('Nutritional Values Correlation Matrix', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(self.viz_path / 'nutrition_correlations.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  Saved: nutrition_correlations.png")
    
    def save_cleaned_data(self, nutrition_df: pd.DataFrame, recipes_df: pd.DataFrame) -> None:
        """Save cleaned datasets."""
        print("Saving cleaned data...")
        
        if nutrition_df is not None:
            nutrition_df.to_csv(self.output_path / 'nutrition_cleaned.csv', index=False)
            print(f"  Saved: nutrition_cleaned.csv ({len(nutrition_df)} rows)")
        
        if recipes_df is not None:
            recipes_df.to_csv(self.output_path / 'recipes_cleaned.csv', index=False)
            print(f"  Saved: recipes_cleaned.csv ({len(recipes_df)} rows)")
        
        print("✓ All cleaned data saved\n")
    
    def run(self) -> None:
        """Execute complete cleaning pipeline."""
        print("\n" + "="*60)
        print("Nutrition Data Cleaning Pipeline (100% Offline)")
        print("="*60 + "\n")
        
        self.load_data()
        self.analyze_data_quality()
        
        nutrition_cleaned = self.clean_nutrition_data()
        recipes_cleaned = self.clean_recipes_data()
        
        self.create_visualizations(nutrition_cleaned, recipes_cleaned)
        self.save_cleaned_data(nutrition_cleaned, recipes_cleaned)
        
        print("="*60)
        print("✓ Nutrition data cleaning complete!")
        print("="*60)
        print(f"\nCleaned data saved to: {self.output_path}")
        print(f"Visualizations saved to: {self.viz_path}")
        print("\nNext step: Run exercise data cleaning")
        print("  python scripts/cleaning/clean_exercise_data.py\n")

if __name__ == "__main__":
    cleaner = NutritionDataCleaner()
    cleaner.run()
