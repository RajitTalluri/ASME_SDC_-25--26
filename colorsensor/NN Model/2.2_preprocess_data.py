import pandas as pd
import os
from tkinter import Tk, filedialog


# Script to put RGB values in 0-1 range by dividing by 255
# Numerical values to labels:
        # 0 for neither
        # 1 for blue/green
        


# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
PREPROCESSED_DATA_PATH = os.path.join(DATA_DIR, 'preprocessed_data.csv')

def select_file():
    """
    Open a file picker dialog to select a labeled CSV file to preprocess.
    Returns the selected file path.
    """
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring to front
    
    print("Opening file picker...")
    print("Select a labeled data CSV file to preprocess")
    
    file_path = filedialog.askopenfilename(
        title="Select labeled data CSV file to preprocess",
        initialdir=DATA_DIR,
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    root.destroy()
    
    return file_path

def get_output_filename():
    """
    Prompt user to name the output file.
    Returns the full path with filename.
    """
    default_name = "preprocessed_data.csv"
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
    return output_path

def preprocess_data(file_path):
    """
    Load CSV, normalize RGB values to 0-1 range by dividing by 255,
    and save to user-specified filename.
    
    Args:
        file_path: Path to the labeled CSV file
    """
    
    print("="*50)
    print("DATA PREPROCESSING")
    print("="*50)
    
    if not file_path:
        print("\nNo file selected. Exiting.")
        return
    
    print(f"\nSelected file: {file_path}")
    
    # Load data
    print("\nLoading data...")
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} samples")
    except Exception as e:
        print(f"Error: Could not load file: {e}")
        exit(1)
    
    # Validate columns
    required_columns = ['Red', 'Green', 'Blue', 'Category']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns: {missing_columns}")
        exit(1)
    
    print("\nNormalizing RGB values...")
    
    # Display original values
    print(f"\nBefore normalization:")
    print(f"  Red:   min={df['Red'].min()}, max={df['Red'].max()}")
    print(f"  Green: min={df['Green'].min()}, max={df['Green'].max()}")
    print(f"  Blue:  min={df['Blue'].min()}, max={df['Blue'].max()}")
    
    # Normalize RGB by dividing by 255
    df['Red'] = df['Red'] / 255.0
    df['Green'] = df['Green'] / 255.0
    df['Blue'] = df['Blue'] / 255.0
    
    # Display normalized values
    print(f"\nAfter normalization:")
    print(f"  Red:   min={df['Red'].min():.4f}, max={df['Red'].max():.4f}")
    print(f"  Green: min={df['Green'].min():.4f}, max={df['Green'].max():.4f}")
    print(f"  Blue:  min={df['Blue'].min():.4f}, max={df['Blue'].max():.4f}")
    
    # Convert category labels to numerical values
    print("\nConverting labels to numerical values...")
    def convert_label(category):
        if category.lower() in ['blue', 'green']:
            return 1
        else:  # neither
            return 0
    
    df['Category'] = df['Category'].apply(convert_label)
    print("  blue → 1")
    print("  green → 1")
    print("  neither → 0")
    
    # Save preprocessed data
    output_file = get_output_filename()
    print(f"\nSaving preprocessed data...")
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} samples to {output_file}")
    
    # Display statistics
    print("\n" + "="*50)
    print("PREPROCESSING COMPLETE")
    print("="*50)
    print(f"Total samples: {len(df)}")
    
    print(f"\nCategory distribution:")
    counts = df['Category'].value_counts()
    for category, count in counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {category}: {count} samples ({percentage:.1f}%)")
    
    print("\n" + "="*50)
    print("Ready for training! Use the saved file as input to 3_train_model.py")

if __name__ == "__main__":
    # Open file picker and get selected file
    selected_file = select_file()
    
    # Preprocess the selected file
    preprocess_data(selected_file)
