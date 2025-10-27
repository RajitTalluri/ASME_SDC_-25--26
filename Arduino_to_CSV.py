
import serial
import time
import csv
from datetime import datetime

# Configuration
SERIAL_PORT = 'COM3'  # Update to Arduino Port
BAUD_RATE = 9600      # Match to Arduino Baude Rate
OUTPUT_FILE = 'ASMEcolor_data.csv' # file that saves the data

def read_arduino_data(duration=None, num_samples=None):
    """
    Read data from Arduino via serial connection.
    
    Args:
        duration: Time in seconds to collect data (optional)
        num_samples: Number of samples to collect (optional)
    """
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset after connection
        
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        print("Reading data... Press Ctrl+C to stop\n")
        
        # Open CSV file for writing
        with open(OUTPUT_FILE, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write header (adjust based on your data format)
            csv_writer.writerow(['Timestamp', 'Data'])
            
            sample_count = 0
            start_time = time.time()
            
            while True:
                # Check stopping conditions
                if duration and (time.time() - start_time) >= duration:
                    break
                if num_samples and sample_count >= num_samples:
                    break
                
                # Read data from Arduino
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    
                    if line:  # If line is not empty
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        
                        # Print to console
                        print(f"[{timestamp}] {line}")
                        
                        # Write to CSV
                        csv_writer.writerow([timestamp, line])
                        
                        sample_count += 1
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
        
        print(f"\nData collection complete! Saved {sample_count} samples to {OUTPUT_FILE}")
        
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Arduino is connected")
        print("2. Verify the correct port (use Arduino IDE Tools > Port to find it)")
        print("3. Make sure no other program is using the port")
        
    except KeyboardInterrupt:
        print(f"\n\nStopped by user. Saved {sample_count} samples to {OUTPUT_FILE}")
        
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
    # Uncomment to see available ports
    list_available_ports()
    
    # Collect data for 30 seconds
    # read_arduino_data(duration=30)
    
    # Or collect 100 samples
    # read_arduino_data(num_samples=100)
    
    # Or collect until Ctrl+C
    read_arduino_data()
