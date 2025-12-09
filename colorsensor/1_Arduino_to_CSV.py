import serial
import time
import csv
import os
from pynput import keyboard

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
    """Callback for keyboard press events"""
    global marker_flag
    try:
        if key == keyboard.Key.space: # spacebar pressed
            marker_flag = True
    except AttributeError:
        pass

def read_arduino_data(duration=None, num_samples=None):
    """
    Read data from Arduino via serial connection.
    Press SPACEBAR to insert object change markers.
    
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
        
        # Open CSV file for writing
        with open(OUTPUT_FILE, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write header
            csv_writer.writerow(['Red', 'Green', 'Blue'])
            
            sample_count = 0
            marker_count = 0
            start_time = time.time()
            
            # Skip calibration messages
            calibration_done = False
            
            while True:
                # Check stopping conditions
                if duration and (time.time() - start_time) >= duration:
                    break
                if num_samples and sample_count >= num_samples:
                    break
                
                # Check for spacebar press
                if marker_flag:
                    csv_writer.writerow(['---OBJECT_CHANGE---', '', ''])
                    marker_count += 1
                    print(f"\n>>> MARKER INSERTED (Total markers: {marker_count}) <<<\n")
                    marker_flag = False
                
                # Read data from Arduino
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    
                    if line:
                        # Skip calibration messages
                        skip_keywords = ['calibration', 'point', 'white', 'black', 
                                       'completed', 'prepare', 'min/max', 'starting',
                                       '===', 'data start', '---']
                        
                        if any(keyword in line.lower() for keyword in skip_keywords):
                            print(f"[Calibration] {line}")
                            continue
                        
                        # Check if line contains RGB data (format: "R,G,B")
                        if ',' in line:
                            try:
                                parts = line.split(',')
                                if len(parts) == 3:
                                    r, g, b = map(int, parts)
                                    
                                    # Print to console
                                    print(f"Sample {sample_count + 1}: R={r:3d}, G={g:3d}, B={b:3d}")
                                    
                                    # Write to CSV
                                    csv_writer.writerow([r, g, b])
                                    csvfile.flush()  # Ensure data is written immediately
                                    
                                    sample_count += 1
                            except ValueError:
                                # Skip lines that can't be parsed as integers
                                continue
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
        
        listener.stop()
        print(f"\n{'='*50}")
        print(f"Data collection complete!")
        print(f"Samples collected: {sample_count}")
        print(f"Markers inserted: {marker_count}")
        print(f"Saved to: {OUTPUT_FILE}")
        print(f"{'='*50}")
        
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Arduino is connected")
        print("2. Verify the correct port (use Arduino IDE Tools > Port to find it)")
        print("3. Make sure no other program is using the port")
        
    except KeyboardInterrupt:
        print(f"\n\n{'='*50}")
        print(f"Stopped by user")
        print(f"Samples collected: {sample_count}")
        print(f"Markers inserted: {marker_count}")
        print(f"Saved to: {OUTPUT_FILE}")
        print(f"{'='*50}")
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed")

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
