# 🚦 Traffic Violation Detection System

A comprehensive traffic violation detection system using computer vision and deep learning.

## ✨ Features
- Helmet violation detection
- Triple riding detection
- License plate recognition
- Web interface (Django)
- Violation logging
- Repeat offender Tracking


1. **Clone & Setup**
   ```bash
   git clone https://github.com/jayakrishna662/TrafAI.git
   cd TrafAI
   
   # Create and activate virtual env
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   
   # Install requirements
   pip install -r requirements.txt
   ```

2. **Run Web App**
   ```bash
   python manage.py runserver
   ```
   Visit: http://127.0.0.1:8000/


## 📁 Project Structure
```
TrafAI/
├── detect/                 # Detection modules
│   ├── Helmet_detection/
│   ├── Licenseplate_detection/
│   └── Trippleriding_detection/
├── traffic_violation_web/  # Django project
├── violations/            # Violation detection app
├── input_images/          # Sample input images
├── output_images/         # Processed outputs
├── manage.py             # Django management
└── requirements.txt      # Dependencies
```

## 📝 Requirements
- Python 3.8+
- Git LFS (for model files)
- See requirements.txt for Python packages

