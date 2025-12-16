import pandas as pd
import os

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'raw_data.csv')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'labeled_data.csv')

def load_raw_data():
    """Load the raw sensor data from CSV, excluding markers"""
    try:
        df = pd.read_csv(INPUT_FILE)
        # Remove marker rows
        df = df[df['Raw'] != '---MARKER---']
        # Remove rows where RGB parsing failed
        df = df.dropna(subset=['Red', 'Green', 'Blue'])
        print(f"Loaded {len(df)} valid samples from raw_data.csv")
        return df
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}")
        print("Please run 1_Arduino_to_CSV.py first to collect sensor data.")
        exit(1)

def load_existing_labels():
    """Load previously labeled data if it exists"""
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_csv(OUTPUT_FILE)
            print(f"Found {len(df)} previously labeled samples")
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def get_label():
    """Get valid label input from user"""
    while True:
        label = input("Label (b=blue, g=green, n=neither, u=undo, q=quit): ").lower().strip()
        if label in ['b', 'g', 'n', 'u', 'q']:
            return label
        print("Invalid input. Use b/g/n/u/q")

def expand_label(short_label):
    """Convert short label to full name"""
    mapping = {'b': 'blue', 'g': 'green', 'n': 'neither'}
    return mapping.get(short_label, short_label)

def show_statistics(labeled_data):
    """Display labeling statistics"""
    if not labeled_data:
        return
    
    df = pd.DataFrame(labeled_data)
    print("\n" + "="*50)
    print("STATISTICS")
    print("="*50)
    
    counts = df['Category'].value_counts()
    for category, count in counts.items():
        percentage = (count / len(df)) * 100
        print(f"{category.capitalize()}: {count} samples ({percentage:.1f}%)")
    
    print(f"\nTotal samples labeled: {len(df)}")
    print("="*50)

def simple_label_mode(data):
    """
    Simple labeling mode: show samples one by one and assign labels
    Each sample becomes one training example
    """
    print("\nSIMPLE LABELING MODE")
    print("Each sample will be labeled individually")
    
    labeled_data = []
    current_index = 0
    
    while current_index < len(data):
        print(f"\n{'='*50}")
        print(f"Sample {current_index + 1} of {len(data)}")
        print(f"{'='*50}")
        
        row = data.iloc[current_index]
        r = int(row['Red'])
        g = int(row['Green'])
        b = int(row['Blue'])
        
        print(f"RGB: ({r}, {g}, {b})")
        
        label = get_label()
        
        if label == 'q':
            break
        elif label == 'u':
            if labeled_data:
                removed = labeled_data.pop()
                print(f"Undid last label ({removed['Category']})")
                # Don't increment, stay on same sample for re-labeling
            continue
        elif label in ['b', 'g', 'n']:
            full_label = expand_label(label)
            
            labeled_data.append({
                'Red': r,
                'Green': g,
                'Blue': b,
                'Category': full_label
            })
            
            print(f"Labeled as: {full_label}")
            print(f"Progress: {len(labeled_data)} samples labeled")
            current_index += 1
    
    return labeled_data

def main():
    print("\n" + "="*50)
    print("DATA LABELING TOOL")
    print("="*50)
    
    # Load raw data (excludes markers and invalid rows)
    data = load_raw_data()
    
    # Check for existing labels
    existing_labels = load_existing_labels()
    
    # Start labeling
    new_labeled_data = simple_label_mode(data)
    
    # Save labeled data
    if new_labeled_data:
        # Append to existing labels if present
        if not existing_labels.empty:
            append_choice = input("\nAppend to existing labels? (y/n): ").lower()
            if append_choice == 'y':
                combined = pd.concat([existing_labels, pd.DataFrame(new_labeled_data)], ignore_index=True)
                combined.to_csv(OUTPUT_FILE, index=False)
                print(f"\nAppended {len(new_labeled_data)} new samples")
                print(f"Total samples now: {len(combined)}")
                show_statistics(combined.to_dict('records'))
            else:
                df = pd.DataFrame(new_labeled_data)
                df.to_csv(OUTPUT_FILE, index=False)
                print(f"\nSaved {len(new_labeled_data)} samples (overwrote existing)")
                show_statistics(new_labeled_data)
        else:
            df = pd.DataFrame(new_labeled_data)
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"\nSaved {len(new_labeled_data)} samples to {OUTPUT_FILE}")
            show_statistics(new_labeled_data)
    else:
        print("\nNo data was labeled.")

if __name__ == "__main__":
    main()
