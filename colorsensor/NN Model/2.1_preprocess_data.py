import pandas as pd
import os
from tkinter import Tk, filedialog

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

def select_files():
    """
    Open a file picker dialog to select labeled CSV files to combine.
    Returns list of selected file paths.
    """
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring to front
    
    print("Opening file picker...")
    print("Select one or more labeled CSV files to combine and preprocess")
    
    file_paths = filedialog.askopenfilenames(
        title="Select labeled data CSV files to combine",
        initialdir=DATA_DIR,
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    root.destroy()
    
    return list(file_paths)

def get_output_filename():
    """
    Prompt user to name the output file.
    Returns the full path with filename.
    """
    default_name = "preprocessed_training_data.csv"
    user_input = input(f"\nEnter output filename (default: {default_name}): ").strip()
    
    if user_input:
        # Remove .csv if user added it
        if user_input.endswith('.csv'):
            filename = user_input
        else:
            filename = user_input + '.csv'
    else:
        filename = default_name
    
    output_path = os.path.join(DATA_DIR, filename)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    return output_path

def is_preprocessed(df):
    """
    Check if a dataframe is already preprocessed.
    Returns True if RGB values are in 0-1 range and Category is numeric.
    """
    # Check if RGB values are in 0-1 range (with small tolerance for rounding)
    rgb_normalized = (
        df['Red'].max() <= 1.0 and 
        df['Green'].max() <= 1.0 and 
        df['Blue'].max() <= 1.0 and
        df['Red'].min() >= 0.0 and
        df['Green'].min() >= 0.0 and
        df['Blue'].min() >= 0.0
    )
    
    # Check if Category is numeric (0 or 1)
    try:
        category_numeric = pd.to_numeric(df['Category'], errors='coerce').notna().all()
        if category_numeric:
            unique_vals = df['Category'].unique()
            category_is_binary = all(val in [0, 1, '0', '1'] for val in unique_vals)
        else:
            category_is_binary = False
    except:
        category_is_binary = False
    
    return rgb_normalized and category_is_binary

def combine_and_preprocess(file_paths):
    """
    Combine multiple labeled data files, validate, normalize RGB to 0-1 range,
    and convert category labels to numerical values.
    Handles both preprocessed and non-preprocessed files automatically.
    
    Args:
        file_paths: List of CSV file paths to combine
    """
    
    print("="*50)
    print("DATA PREPARATION & PREPROCESSING")
    print("="*50)
    
    if not file_paths:
        print("\nNo files selected. Exiting.")
        return
    
    print(f"\nSelected {len(file_paths)} file(s):")
    for fp in file_paths:
        print(f"  - {os.path.basename(fp)}")
    
    # Load and process each file individually
    print("\nLoading and analyzing files...")
    processed_dfs = []
    
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            filename = os.path.basename(file_path)
            print(f"\n  {filename}: {len(df)} samples")
            
            # Check if already preprocessed
            if is_preprocessed(df):
                print(f"    ✓ Already preprocessed (RGB in 0-1 range, numeric labels)")
                processed_dfs.append(df)
            else:
                print(f"    → Needs preprocessing (will normalize RGB and convert labels)")
                processed_dfs.append(df)
                
        except Exception as e:
            print(f"  Warning: Could not load {file_path}: {e}")
    
    if not processed_dfs:
        print("Error: No valid files loaded")
        exit(1)
    
    # Combine all dataframes
    df = pd.concat(processed_dfs, ignore_index=True)
    print(f"\nTotal samples after combining: {len(df)}")
    
    # Validate columns
    required_columns = ['Red', 'Green', 'Blue', 'Category']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns: {missing_columns}")
        exit(1)
    
    print("\nValidating data...")
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
    
    # Detect if data needs normalization (check if any RGB value > 1)
    needs_normalization = (df['Red'].max() > 1.0 or 
                          df['Green'].max() > 1.0 or 
                          df['Blue'].max() > 1.0)
    
    if needs_normalization:
        # Validate RGB ranges (0-255) before normalization
        initial_count = len(df)
        
        # Separate already normalized (0-1) from unnormalized (0-255) rows
        normalized_mask = (df['Red'] <= 1.0) & (df['Green'] <= 1.0) & (df['Blue'] <= 1.0)
        df_normalized = df[normalized_mask].copy()
        df_unnormalized = df[~normalized_mask].copy()
        
        print(f"  {len(df_normalized)} rows already normalized (RGB in 0-1 range)")
        print(f"  {len(df_unnormalized)} rows need normalization (RGB in 0-255 range)")
        
        # Validate unnormalized data is in 0-255 range
        if len(df_unnormalized) > 0:
            valid_range = (
                (df_unnormalized['Red'] >= 0) & (df_unnormalized['Red'] <= 255) &
                (df_unnormalized['Green'] >= 0) & (df_unnormalized['Green'] <= 255) &
                (df_unnormalized['Blue'] >= 0) & (df_unnormalized['Blue'] <= 255)
            )
            df_unnormalized = df_unnormalized[valid_range]
            out_of_range = len(df[~normalized_mask]) - len(df_unnormalized)
            if out_of_range > 0:
                print(f"  Removed {out_of_range} rows with out-of-range RGB values")
            
            # Normalize the unnormalized data
            print(f"\nNormalizing {len(df_unnormalized)} rows to 0-1 range...")
            df_unnormalized['Red'] = df_unnormalized['Red'] / 255.0
            df_unnormalized['Green'] = df_unnormalized['Green'] / 255.0
            df_unnormalized['Blue'] = df_unnormalized['Blue'] / 255.0
        
        # Recombine
        df = pd.concat([df_normalized, df_unnormalized], ignore_index=True)
    else:
        print("  All data already normalized (RGB in 0-1 range)")
    
    # Remove rows with empty Category
    initial_count = len(df)
    df = df.dropna(subset=['Category'])
    df['Category'] = df['Category'].astype(str)
    df = df[df['Category'].str.strip() != '']
    category_removed = initial_count - len(df)
    if category_removed > 0:
        print(f"Removed {category_removed} rows with empty category")
    
    if len(df) == 0:
        print("Error: No valid samples after validation")
        exit(1)
    
    # Display current RGB ranges
    print(f"\nCurrent RGB ranges (normalized 0-1):")
    print(f"  Red:   min={df['Red'].min():.4f}, max={df['Red'].max():.4f}, mean={df['Red'].mean():.4f}")
    print(f"  Green: min={df['Green'].min():.4f}, max={df['Green'].max():.4f}, mean={df['Green'].mean():.4f}")
    print(f"  Blue:  min={df['Blue'].min():.4f}, max={df['Blue'].max():.4f}, mean={df['Blue'].mean():.4f}")
    
    # Convert category labels to numerical values if needed
    print("\nProcessing category labels...")
    
    # Check if already numeric
    try:
        df['Category'] = pd.to_numeric(df['Category'], errors='raise')
        print("  Categories already numeric")
    except:
        # Need to convert text labels to numeric
        print("  Converting text labels to numeric values...")
        print("  Mapping: blue/green → 1, neither → 0")
        
        # Show original category distribution
        print(f"\n  Original category distribution:")
        orig_counts = df['Category'].value_counts()
        for category, count in orig_counts.items():
            percentage = (count / len(df)) * 100
            print(f"    {category}: {count} samples ({percentage:.1f}%)")
        
        def convert_label(category):
            category_str = str(category).lower().strip()
            if category_str in ['blue', 'green', '1', '1.0']:
                return 1
            else:  # neither or 0
                return 0
        
        df['Category'] = df['Category'].apply(convert_label)
    
    # Save preprocessed training data
    output_file = get_output_filename()
    print(f"\nSaving preprocessed training data...")
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} samples to {output_file}")
    
    # Display final statistics
    print("\n" + "="*50)
    print("FINAL DATASET STATISTICS")
    print("="*50)
    print(f"Total samples: {len(df)}")
    
    print(f"\nNumerical category distribution:")
    counts = df['Category'].value_counts()
    for category, count in counts.items():
        percentage = (count / len(df)) * 100
        label = "blue/green" if category == 1 else "neither"
        print(f"  {category} ({label}): {count} samples ({percentage:.1f}%)")
    
    print("\n" + "="*50)
    print("Ready for training! Use the saved file as input to your training script")

if __name__ == "__main__":
    # Open file picker and get selected files
    selected_files = select_files()
    
    # Combine, validate, and preprocess selected files
    combine_and_preprocess(selected_files)