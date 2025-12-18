import serial
import time
import csv
from datetime import datetime
import os
from pynput import keyboard

# Configuration
SERIAL_PORT = 'COM3'  # Update to Arduino Port
BAUD_RATE = 9600      # Match to Arduino Baud Rate

# Define output file path relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(DATA_DIR, 'raw_data.csv')

# Global flag for spacebar press
marker_flag = False

def on_press(key):
    """Callback for spacebar press to insert markers"""
    global marker_flag
    try:
        if key == keyboard.Key.space:
            marker_flag = True
    except AttributeError:
        pass

def read_arduino_data(duration=None, num_samples=None):
    """
    Read data from Arduino via serial connection.
    
    Args:
        duration: Time in seconds to collect data (optional)
        num_samples: Number of samples to collect (optional)
    """
    global marker_flag
    
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset after connection
        
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        print("Reading data...")
        print("Press SPACEBAR to mark object changes")
        print("Press Ctrl+C to stop\n")
        
        # Start keyboard listener in separate thread
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        # Open CSV file for appending so multiple runs can be combined later
        file_exists = os.path.exists(OUTPUT_FILE)
        with open(OUTPUT_FILE, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header if file is new
            if not file_exists or os.path.getsize(OUTPUT_FILE) == 0:
                csv_writer.writerow(['Timestamp', 'Red', 'Green', 'Blue', 'Raw'])
            
            sample_count = 0
            marker_count = 0
            start_time = time.time()
            
            while True:
                # Check stopping conditions
                if duration and (time.time() - start_time) >= duration:
                    break
                if num_samples and sample_count >= num_samples:
                    break
                
                # Check for spacebar press and insert marker
                if marker_flag:
                    marker_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    csv_writer.writerow([marker_timestamp, '', '', '', '---MARKER---'])
                    marker_count += 1
                    print(f"\n>>> MARKER INSERTED (Total markers: {marker_count}) <<<\n")
                    marker_flag = False
                
                # Read data from Arduino
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:  # If line is not empty
                        # Try to parse common RGB formats: "R:123,G:45,B:67" or "123,45,67"
                        def parse_rgb(s):
                            s = s.strip()
                            try:
                                if ':' in s and ',' in s:
                                    # format like R:123,G:45,B:67
                                    parts = [p.split(':')[1] for p in s.split(',')]
                                    r, g, b = [int(p) for p in parts]
                                    return r, g, b
                                if ',' in s:
                                    parts = [p.strip() for p in s.split(',')]
                                    if len(parts) >= 3:
                                        r, g, b = [int(parts[0]), int(parts[1]), int(parts[2])]
                                        return r, g, b
                            except Exception:
                                return None
                            return None
                        
                        rgb = parse_rgb(line)
                        if rgb is None:
                            r = g = b = ''
                        else:
                            r, g, b = rgb
                        
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        
                        # Print to console
                        print(f"[{timestamp}] {line}")
                        
                        # Write to CSV with parsed columns and raw data
                        csv_writer.writerow([timestamp, r, g, b, line])
                        # Ensure data is written to disk promptly
                        csvfile.flush()
                        try:
                            os.fsync(csvfile.fileno())
                        except Exception:
                            pass
                        
                        sample_count += 1
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
        
        print(f"\nData collection complete! Saved {sample_count} samples to {OUTPUT_FILE}")
        if marker_count > 0:
            print(f"Total markers inserted: {marker_count}")
        
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Arduino is connected")
        print("2. Verify the correct port (use Arduino IDE Tools > Port to find it)")
        print("3. Make sure no other program is using the port")
        
    except KeyboardInterrupt:
        print(f"\n\nStopped by user. Saved {sample_count} samples to {OUTPUT_FILE}")
        if marker_count > 0:
            print(f"Markers inserted: {marker_count}")
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed")
        listener.stop()


def list_available_ports():
    """List all available serial ports"""
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    
    print("Available serial ports:")
    for port in ports:
        print(f"  - {port.device}: {port.description}")
    print()

if __name__ == "__main__":
    print("="*50)
    print("ARDUINO RGB DATA COLLECTION")
    print("="*50)
    print()
    
    # Show available ports
    list_available_ports()
    
    # Collect data for 30 seconds
    # read_arduino_data(duration=30)
    
    # Or collect 100 samples
    # read_arduino_data(num_samples=100)
    
    # Or collect until Ctrl+C
    read_arduino_data()
