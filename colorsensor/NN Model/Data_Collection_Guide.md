# TCS3200 Color Sensor - Data Collection Guide

## Overview
This document provides instructions for collecting RGB color data using the TCS3200 sensor and Arduino for machine learning model training. Follow these steps to ensure high-quality, consistent data collection.

## Table of Contents
- [Requirements](#requirements)
- [Hardware Setup](#hardware-setup)
- [Software Configuration](#software-configuration)
- [Data Collection Procedure](#data-collection-procedure)
- [Data Labeling](#data-labeling)
- [Data Preparation](#data-preparation)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Requirements

### Hardware
- Arduino Uno (or compatible board)
- TCS3200 color sensor module
- USB cable
- Test objects in various colors (blue, green, and assorted colors)

### Software Dependencies
Install required Python packages:
```bash
pip install pyserial pynput pandas
```

### Project Files
Ensure you have the following scripts:
- `1_collect_data.py` - Data collection script
- `label_data.py` - Interactive labeling tool
- `2_prepare_data.py` - Data validation and preparation

---

## Hardware Setup

### Wiring Configuration
The TCS3200 sensor should be connected to the Arduino with the following pin assignments:
- S0 → Digital Pin 8
- S1 → Digital Pin 9
- S2 → Digital Pin 10
- S3 → Digital Pin 11
- Signal → Digital Pin 12
- VCC → 5V
- GND → GND

### Arduino Firmware Upload
1. Open Arduino IDE
2. Load the sensor sketch file
3. Select board type: **Tools > Board > Arduino Uno**
4. Select port: **Tools > Port > COM3** (verify your specific port)
5. Upload the sketch to the Arduino

### Verification
1. Open Serial Monitor (**Tools > Serial Monitor**, 9600 baud)
2. The sensor will begin calibration sequence
3. Follow on-screen prompts:
   - Position sensor 1-2cm from white surface when prompted
   - Position sensor 1-2cm from black surface when prompted
4. Verify RGB values are streaming (format: `R,G,B`)
5. Close Serial Monitor before proceeding to data collection

---

## Software Configuration

### Port Configuration
Verify the Arduino port in `1_collect_data.py`:
```python
SERIAL_PORT = 'COM3'  # Update if using different port
BAUD_RATE = 9600
```

### Directory Structure
Organize project files as follows:
```
project/
├── scripts/
│   ├── 1_collect_data.py
│   ├── label_data.py
│   └── 2_prepare_data.py
└── data/
    └── (output files saved here)
```

---

## Data Collection Procedure

### Sample Selection
Collect a variety of shades and materials for each object for better training. Each individual object should represent a single data point, label data script has a feature to combine data points for the same object.
**Note the same object can be recorded at different angles as another data point. 

**Blue Category:**
- Multiple shades (navy, royal blue, sky blue, turquoise, cobalt, azure)
- Different materials (plastic, paper, fabric, metal)
- Different finishes (matte, glossy, textured)
- Aim for 20 distinct blue objects minimum

**Green Category:**
- Multiple shades (forest green, lime, mint, olive, emerald, sage)
- Different materials (plastic, paper, fabric, metal)
- Different finishes (matte, glossy, textured)
- Aim for 20 distinct green objects minimum

**Neither Category:**
- Various non-target colors (red, yellow, purple, brown, orange, pink)
- Neutral colors (brown, grey, black in multiple shades)
- Aim for 20 objects to represent diverse non-target colors

**Total Object Count:** 70-80 objects recommended

### Collection Process

#### Start Data Collection
```bash
cd scripts
python 1_collect_data.py
```

Expected output:
```
==================================================
ARDUINO RGB DATA COLLECTION
==================================================
Connected to COM3 at 9600 baud
Reading data...
Press SPACEBAR to mark object changes
Press Ctrl+C to stop
```

#### Per-Object Procedure
For each test object:

1. **Position** - Place object 1-2cm beneath sensor
2. **Stabilize** - Wait 2-3 seconds for readings to settle
3. **Mark Start** - Press SPACEBAR to insert marker
4. **Collect** - Maintain position for ~5 seconds (~10 samples)
5. **Mark End** - Press SPACEBAR to insert second marker
6. **Record** - Record the objects classification (g, b, n) for data labeling later
7. **Next Object** - Remove current object and repeat

#### Monitoring Collection
The console displays real-time RGB values:
```
[2024-12-20 19:47:40.174] 43,23,16
[2024-12-20 19:47:40.680] 41,23,19

>>> MARKER INSERTED (Total markers: 1) <<<
```

#### Stop Collection
Press **Ctrl+C** when finished. Data saves automatically to `../data/raw_data.csv`.

---

## Data Labeling

### Launch Labeling Tool
```bash
python label_data.py
```

### Labeling Interface
The tool presents samples individually:
```
==================================================
Sample 1 of 300
==================================================
RGB: (43, 108, 174)
Label (b=blue, g=green, n=neither, u=undo, q=quit): _
```

### Labeling Guidelines

### Controls
- `b` - Classify as blue
- `g` - Classify as green
- `n` - Classify as neither
- `u` - Undo previous label
- `q` - Save and quit

### Completion
After labeling all samples:
```
==================================================
STATISTICS
==================================================
Blue: 100 samples (33.3%)
Green: 100 samples (33.3%)
Neither: 100 samples (33.3%)

Total samples labeled: 300
==================================================
Saved 300 samples to labeled_data.csv
```

Verify distribution is reasonably balanced (each category 25-40%).

---

## Data Preparation

### Run Preparation Script
```bash
python 2_prepare_data.py
```

### File Selection
1. File picker dialog will open
2. Navigate to `data/` directory
3. Select `labeled_data.csv`
4. Confirm selection

### Validation Output
The script validates data and reports statistics:
```
==================================================
DATA PREPARATION FOR TRAINING
==================================================
Selected 1 file(s): labeled_data.csv

Loading labeled data...
  Loaded 300 samples from labeled_data.csv

Validating data...
Saved 300 samples to training_data.csv

==================================================
TRAINING DATASET STATISTICS
==================================================
Total samples: 300

Category distribution:
  blue: 100 samples (33.3%)
  green: 100 samples (33.3%)
  neither: 100 samples (33.3%)

RGB value ranges:
  Red:   min=20, max=220, mean=120.5
  Green: min=15, max=235, mean=115.3
  Blue:  min=10, max=240, mean=125.1
==================================================
```

The validated data is now ready for model training.

---

## Best Practices

### Data Quality Standards

**Recommended Practices:**
- Maintain consistent 1-2cm sensor-to-object distance
- Allow 2-3 seconds for readings to stabilize before marking
- Collect 10-20 samples per object
- Use diverse shades within each color category
- Ensure consistent ambient lighting
- Utilize spacebar markers to segment data
- Balance sample distribution across categories

**Avoid:**
- Moving objects during sample collection
- Inconsistent lighting conditions
- Accepting readings at extremes (0,0,0 or 255,255,255)
- Rushed data collection
- Imbalanced category distribution (>50% in one category)
- Insufficient total samples (<200)

### Quality Indicators

**High-Quality Data:**
- RGB values range 20-240 (not saturated)
- Consistent readings per object (variance <10)
- Clear inter-category separation
- Balanced distribution (30-40% per category)

**Low-Quality Data:**
- Frequent 0,0,0 or 255,255,255 readings → Recalibrate sensor
- High variance in readings → Improve stability
- Severe class imbalance → Collect additional samples
- Insufficient samples → Continue data collection

---

## Troubleshooting

### Python Package Errors
**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install pyserial pynput pandas
```

### Serial Port Issues
**Error:** `Could not open serial port COM3`

**Solutions:**
1. Verify Arduino connection
2. Check port in Arduino IDE (Tools > Port)
3. Close Arduino Serial Monitor if open
4. Update `SERIAL_PORT` in script if using different port

### Sensor Reading Issues

**All readings show 0,0,0 or 255,255,255:**
1. Reset Arduino and recalibrate
2. Verify sensor distance (1-2cm optimal)
3. Check ambient lighting
4. Inspect sensor wiring connections

**Unstable/Erratic Readings:**
1. Ensure object remains stationary
2. Wait for stabilization period before marking
3. Verify consistent lighting
4. Check for loose connections

### File System Issues

**Script cannot locate `raw_data.csv`:**
1. Verify file location: `data/raw_data.csv`
2. Confirm successful execution of `1_collect_data.py`
3. Check directory structure matches expected layout

**File picker does not open:**
- Install tkinter:
  ```bash
  pip install tk
  ```

## Pre-Training Checklist

Verify the following before proceeding to model training:

- [ ] Diverse samples collected across color categories
- [ ] 25-40 different objects used for data collection
- [ ] Minimum 600 total samples (900+ recommended)
- [ ] Balanced distribution (each category 25-40%)
- [ ] Minimal saturated readings (0,0,0 or 255,255,255)
- [ ] Multiple shades and materials represented per category
- [ ] Edge cases included (colors similar to target categories)
- [ ] All samples labeled correctly
- [ ] `training_data.csv` generated successfully
- [ ] RGB value ranges appear reasonable in statistics

---

## Additional Support

For issues not covered in this guide:
1. Verify Arduino Serial Monitor shows valid sensor output
2. Confirm all Python dependencies installed correctly
3. Review console error messages for specific issues
4. Ensure project directory structure is correct
