# Traffic Violation Detector

This project implements a system to detect traffic violations (red light jumping) using computer vision and deep learning techniques.

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Download YOLOv8 model (will be downloaded automatically on first run)

## Usage

1. Place your test image in the project directory
2. Update the `image_path` in `traffic_violation_detector.py` with your image filename
3. Run the script:
```bash
python traffic_violation_detector.py
```

## Features
- Vehicle detection using YOLOv8
- Image processing and visualization
- Violation detection logic

## Next Steps

1. Test with sample images
2. Adjust detection parameters as needed
3. Implement stop line detection
4. Add violation zone detection
5. Enhance accuracy with additional validation steps 