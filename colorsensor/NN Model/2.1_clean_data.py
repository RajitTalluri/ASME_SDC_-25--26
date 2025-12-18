import pandas as pd
import os
import sys
from tkinter import Tk, filedialog

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
TRAINING_DATA_PATH = os.path.join(DATA_DIR, 'training_data.csv')

def select_files():
    """
    Open a file picker dialog to select labeled CSV files to combine.
    Returns list of selected file paths.
    """
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring to front
    
    print("Opening file picker...")
    print("Select one or more labeled CSV files to combine")
    
    file_paths = filedialog.askopenfilenames(
        title="Select labeled data CSV files to combine",
        initialdir=DATA_DIR,
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    root.destroy()
    
    return list(file_paths)

def combine_labeled_data(file_paths):
    """
    Combine and validate selected labeled data files into a single training CSV.
    
    Args:
        file_paths: List of CSV file paths to combine
    """
    
    print("="*50)
    print("DATA PREPARATION FOR TRAINING")
    print("="*50)
    
    if not file_paths:
        print("\nNo files selected. Exiting.")
        return
    
    print(f"\nSelected {len(file_paths)} file(s):")
    for fp in file_paths:
        print(f"  - {fp}")
    
    # Load and combine all files
    print("\nLoading labeled data...")
    dfs = []
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            print(f"  Loaded {len(df)} samples from {os.path.basename(file_path)}")
            dfs.append(df)
        except Exception as e:
            print(f"  Warning: Could not load {file_path}: {e}")
    
    if not dfs:
        print("Error: No valid files loaded")
        exit(1)
    
    # Combine all dataframes
    df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal samples before validation: {len(df)}")
    
    # Validate columns
    required_columns = ['Red', 'Green', 'Blue', 'Category']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns: {missing_columns}")
        exit(1)
    
    print("Validating data...")
    initial_count = len(df)
    
    # Convert RGB to numeric
    df['Red'] = pd.to_numeric(df['Red'], errors='coerce')
    df['Green'] = pd.to_numeric(df['Green'], errors='coerce')
    df['Blue'] = pd.to_numeric(df['Blue'], errors='coerce')
    
    # Remove rows with invalid RGB
    df = df.dropna(subset=['Red', 'Green', 'Blue'])
    invalid_removed = initial_count - len(df)
    if invalid_removed > 0:
        print(f"Removed {invalid_removed} rows with invalid RGB data")
    
    # Validate RGB ranges (0-255)
    initial_count = len(df)
    df = df[
        (df['Red'] >= 0) & (df['Red'] <= 255) &
        (df['Green'] >= 0) & (df['Green'] <= 255) &
        (df['Blue'] >= 0) & (df['Blue'] <= 255)
    ]
    out_of_range = initial_count - len(df)
    if out_of_range > 0:
        print(f"Removed {out_of_range} rows with out-of-range RGB values")
    
    # Remove rows with empty Category
    initial_count = len(df)
    df = df.dropna(subset=['Category'])
    df = df[df['Category'].str.strip() != '']
    category_removed = initial_count - len(df)
    if category_removed > 0:
        print(f"Removed {category_removed} rows with empty category")
    
    if len(df) == 0:
        print("Error: No valid samples after validation")
        exit(1)
    
    # Save training data
    print(f"\nSaving training data...")
    df.to_csv(TRAINING_DATA_PATH, index=False)
    print(f"Saved {len(df)} samples to {TRAINING_DATA_PATH}")
    
    # Display statistics
    print("\n" + "="*50)
    print("TRAINING DATASET STATISTICS")
    print("="*50)
    print(f"Total samples: {len(df)}")
    
    print(f"\nCategory distribution:")
    counts = df['Category'].value_counts()
    for category, count in counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {category}: {count} samples ({percentage:.1f}%)")
    
    print(f"\nRGB value ranges:")
    print(f"  Red:   min={int(df['Red'].min())}, max={int(df['Red'].max())}, mean={df['Red'].mean():.1f}")
    print(f"  Green: min={int(df['Green'].min())}, max={int(df['Green'].max())}, mean={df['Green'].mean():.1f}")
    print(f"  Blue:  min={int(df['Blue'].min())}, max={int(df['Blue'].max())}, mean={df['Blue'].mean():.1f}")
    
    print("="*50)
    print("\nReady for training! Use training_data.csv as input to 3_train_model.py")

if __name__ == "__main__":
    # Open file picker and get selected files
    selected_files = select_files()
    
    # Combine and validate selected files
    combine_labeled_data(selected_files)
