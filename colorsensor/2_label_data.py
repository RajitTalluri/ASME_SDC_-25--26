import pandas as pd
import os

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'raw_data.csv')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'labeled_data.csv')

def load_raw_data():
    """Load the raw sensor data from CSV"""
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} rows from raw_data.csv")
        return df
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}")
        print("Please run 1_collect_data.py first to collect sensor data.")
        exit(1)

def load_existing_labels():
    """Load previously labeled data if it exists"""
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_csv(OUTPUT_FILE)
            print(f"Found {len(df)} previously labeled objects")
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
        print(f"{category.capitalize()}: {count} objects ({percentage:.1f}%)")
    
    print(f"\nTotal objects labeled: {len(df)}")
    print("="*50)

def display_range_info(data, start, end):
    """Display information about a range of samples"""
    group = data.iloc[start:end]
    
    avg_r = int(group['Red'].mean())
    avg_g = int(group['Green'].mean())
    avg_b = int(group['Blue'].mean())
    
    std_r = group['Red'].std()
    std_g = group['Green'].std()
    std_b = group['Blue'].std()
    
    print(f"\n{'='*50}")
    print(f"Samples {start+1} to {end}")
    print(f"Number of samples: {len(group)}")
    print(f"{'='*50}")
    print(f"Average RGB: ({avg_r}, {avg_g}, {avg_b})")
    print(f"Std Dev:     ({std_r:.1f}, {std_g:.1f}, {std_b:.1f})")
    print("-"*50)
    
    return avg_r, avg_g, avg_b

def find_markers(data):
    """Find all marker rows in the data"""
    markers = []
    for idx, row in data.iterrows():
        if str(row['Red']) == '---OBJECT_CHANGE---':
            markers.append(idx)
    return markers

def show_data_overview(data):
    """Show overview of data including markers"""
    markers = find_markers(data)
    
    # Filter out marker rows to count actual data
    data_rows = data[data['Red'] != '---OBJECT_CHANGE---']
    
    print("\n" + "="*50)
    print("DATA OVERVIEW")
    print("="*50)
    print(f"Total rows: {len(data)}")
    print(f"Data samples: {len(data_rows)}")
    print(f"Markers found: {len(markers)}")
    
    if markers:
        print(f"\nMarker positions (row numbers):")
        for i, marker_idx in enumerate(markers, 1):
            print(f"  Marker {i}: Row {marker_idx + 1}")
        
        # Show suggested ranges based on markers
        print(f"\nSuggested ranges based on markers:")
        prev = 0
        for i, marker_idx in enumerate(markers, 1):
            # Count only data rows in this range
            range_data = data.iloc[prev:marker_idx]
            data_count = len(range_data[range_data['Red'] != '---OBJECT_CHANGE---'])
            if data_count > 0:
                print(f"  Object {i}: Rows {prev + 1} to {marker_idx} ({data_count} samples)")
            prev = marker_idx + 1
        
        # Last range after final marker
        if prev < len(data):
            range_data = data.iloc[prev:]
            data_count = len(range_data[range_data['Red'] != '---OBJECT_CHANGE---'])
            if data_count > 0:
                print(f"  Object {len(markers) + 1}: Rows {prev + 1} to {len(data)} ({data_count} samples)")
    
    print("="*50)

def range_label_mode(data):
    """
    Label ranges of samples as single objects
    Averages all samples in range to create one training example
    """
    print("\nRANGE LABELING MODE")
    print("Specify start and end row numbers for each object")
    print("All samples in range will be averaged into one training example")
    print("Marker rows (---OBJECT_CHANGE---) will be skipped automatically")
    
    labeled_data = []
    current_index = 0
    
    # Skip to first non-marker row
    while current_index < len(data) and str(data.iloc[current_index]['Red']) == '---OBJECT_CHANGE---':
        current_index += 1
    
    while current_index < len(data):
        print(f"\n{'='*50}")
        print(f"Current position: Row {current_index + 1} of {len(data)}")
        print(f"{'='*50}")
        
        # Show current sample if it's not a marker
        if str(data.iloc[current_index]['Red']) != '---OBJECT_CHANGE---':
            print(f"\nCurrent sample:")
            print(f"Red: {data.iloc[current_index]['Red']}, "
                  f"Green: {data.iloc[current_index]['Green']}, "
                  f"Blue: {data.iloc[current_index]['Blue']}")
        
        try:
            # Get range from user
            start_input = input(f"\nStart row (press ENTER for {current_index + 1}, or 'q' to quit): ").strip()
            
            if start_input.lower() == 'q':
                break
            
            start = int(start_input) - 1 if start_input else current_index
            
            if start < 0 or start >= len(data):
                print("Invalid start index")
                continue
            
            end_input = input(f"End row (or 'q' to quit): ").strip()
            
            if end_input.lower() == 'q':
                break
            
            end = int(end_input)
            
            if end <= start or end > len(data):
                print("Invalid end index")
                continue
            
            # Filter out marker rows from the range
            range_data = data.iloc[start:end]
            range_data = range_data[range_data['Red'] != '---OBJECT_CHANGE---']
            
            if len(range_data) == 0:
                print("No data samples in this range (only markers)")
                continue
            
            # Calculate averages
            avg_r = int(range_data['Red'].mean())
            avg_g = int(range_data['Green'].mean())
            avg_b = int(range_data['Blue'].mean())
            
            std_r = range_data['Red'].std()
            std_g = range_data['Green'].std()
            std_b = range_data['Blue'].std()
            
            print(f"\n{'='*50}")
            print(f"Rows {start+1} to {end}")
            print(f"Data samples: {len(range_data)} (markers excluded)")
            print(f"{'='*50}")
            print(f"Average RGB: ({avg_r}, {avg_g}, {avg_b})")
            print(f"Std Dev:     ({std_r:.1f}, {std_g:.1f}, {std_b:.1f})")
            print("-"*50)
            
            # Get label
            label = get_label()
            
            if label == 'q':
                break
            elif label == 'u':
                if labeled_data:
                    removed = labeled_data.pop()
                    print(f"Undid last label ({removed['Category']})")
                continue
            elif label in ['b', 'g', 'n']:
                full_label = expand_label(label)
                
                # Add single averaged sample
                labeled_data.append({
                    'Red': avg_r,
                    'Green': avg_g,
                    'Blue': avg_b,
                    'Category': full_label
                })
                
                print(f"\nLabeled as: {full_label}")
                print(f"Created 1 training example from {len(range_data)} samples")
                print(f"Progress: {len(labeled_data)} objects labeled")
                
                # Move to next position after this range
                current_index = end
        
        except ValueError:
            print("Invalid input. Enter numeric row numbers.")
            continue
    
    return labeled_data

def main():
    print("\n" + "="*50)
    print("DATA LABELING TOOL")
    print("="*50)
    
    # Load raw data
    data = load_raw_data()
    
    # Show data overview with marker positions
    show_data_overview(data)
    
    # Check for existing labels
    existing_labels = load_existing_labels()
    
    # Start labeling
    labeled_data = range_label_mode(data)
    
    # Save labeled data
    if labeled_data:
        # Append to existing labels if present
        if not existing_labels.empty:
            append = input("\nAppend to existing labels? (y/n): ").lower()
            if append == 'y':
                combined = pd.concat([existing_labels, pd.DataFrame(labeled_data)], ignore_index=True)
                combined.to_csv(OUTPUT_FILE, index=False)
                print(f"Appended {len(labeled_data)} new objects")
                print(f"Total objects now: {len(combined)}")
                show_statistics(combined.to_dict('records'))
            else:
                df = pd.DataFrame(labeled_data)
                df.to_csv(OUTPUT_FILE, index=False)
                print(f"Saved {len(labeled_data)} objects (overwrote existing)")
                show_statistics(labeled_data)
        else:
            df = pd.DataFrame(labeled_data)
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Saved {len(labeled_data)} objects to {OUTPUT_FILE}")
            show_statistics(labeled_data)
    else:
        print("\nNo data was labeled.")

if __name__ == "__main__":
    main()
