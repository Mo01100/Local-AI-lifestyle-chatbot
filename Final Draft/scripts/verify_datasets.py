"""
Dataset Verification Script
Checks if all required datasets are downloaded and in the correct location.
NO API CALLS - Completely offline verification.

This script is the first step in the data pipeline. Before cleaning or ingesting
any data, run this script to confirm that every expected dataset directory exists
under data/raw/ and contains at least one CSV file.

Expected directory layout:
  data/raw/
  ├── nutrition/      (required)
  ├── recipes/        (required)
  ├── exercise/       (required)
  └── mental_health/  (optional)

Usage:
  python scripts/verify_datasets.py
"""

import os
from pathlib import Path
from typing import Dict, List

# ─── Terminal Colour Codes ────────────────────────────────────────────────────
# ANSI escape sequences used to colour-code the terminal output:
#   GREEN  = dataset found and ready
#   YELLOW = directory exists but no CSV files found (possibly empty)
#   RED    = directory missing entirely
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
RESET  = '\033[0m'   # Resets colour back to terminal default

def check_directory_exists(path: Path) -> bool:
    """Return True if the given path exists AND is a directory (not a file)."""
    return path.exists() and path.is_dir()

def check_files_in_directory(path: Path, extensions: List[str] = ['.csv']) -> List[str]:
    """Return a list of filenames (with matching extensions) found directly in path.
    Returns an empty list if the directory doesn't exist or contains no matching files.
    """
    if not path.exists():
        return []  # Directory doesn't exist at all; treat as no files found
    
    files = []
    for ext in extensions:
        # glob() finds all files with the given extension in this directory level
        files.extend([f.name for f in path.glob(f'*{ext}')])
    return files

def verify_datasets() -> Dict[str, bool]:
    """Verify all required datasets are present under data/raw/.
    
    Prints a detailed per-dataset report showing:
      - Whether the directory exists
      - The first 5 CSV filenames found in it
      - An overall readiness status
    
    Also prints next-step instructions based on the results.
    
    Returns:
        Dict mapping dataset names to True (present) or False (missing/empty)
    """
    base_path = Path('data/raw')  # Root directory containing all raw dataset folders
    
    # Define expected dataset directories (mental_health is optional)
    datasets = {
        'Nutrition Dataset':                base_path / 'nutrition',
        'Recipes Dataset':                  base_path / 'recipes',
        'Exercise Dataset':                 base_path / 'exercise',
        'Mental Health Dataset (Optional)': base_path / 'mental_health'
    }
    
    results = {}
    
    print("\n" + "="*60)
    print("Dataset Verification Report (100% Offline)")
    print("="*60 + "\n")
    
    for name, path in datasets.items():
        print(f"Checking: {name}")
        print(f"Location: {path}")
        
        if check_directory_exists(path):
            files = check_files_in_directory(path)  # Find CSV files
            if files:
                print(f"{GREEN}\u2713 Found {len(files)} file(s){RESET}")
                for file in files[:5]:  # Only print the first 5 to keep output readable
                    print(f"  - {file}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")
                results[name] = True
            else:
                # Directory exists but is empty — possibly incomplete download
                print(f"{YELLOW}\u26a0 Directory exists but no CSV files found{RESET}")
                results[name] = False
        else:
            # Directory doesn't exist at all — dataset never downloaded
            print(f"{RED}\u2717 Directory not found{RESET}")
            results[name] = False
        
        print()
    
    # ── Summary ───────────────────────────────────────────────────────
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    # Filter out optional datasets when computing required count
    required_datasets  = [k for k in results.keys() if 'Optional' not in k]
    required_found = sum([results[k] for k in required_datasets])
    
    print(f"Required datasets found: {required_found}/{len(required_datasets)}")
    
    if required_found == len(required_datasets):
        # All required datasets are present — tell the user what to do next
        print(f"{GREEN}\u2713 All required datasets are ready!{RESET}")
        print("\nNext step: Run data cleaning scripts")
        print("  python scripts/cleaning/clean_nutrition_data.py")
    else:
        print(f"{RED}\u2717 Some datasets are missing{RESET}")
        print("\nPlease download missing datasets manually:")
        print("  See docs/DATASET_DOWNLOAD_GUIDE.md for instructions")
    
    print()
    
    return results

if __name__ == "__main__":
    # Create base directories if they don't exist
    base_path = Path('data/raw')
    for subdir in ['nutrition', 'recipes', 'exercise', 'mental_health']:
        (base_path / subdir).mkdir(parents=True, exist_ok=True)
    
    verify_datasets()
