# 🚦 Traffic Violation Detection System

A comprehensive traffic violation detection system using computer vision and deep learning.
The main objective of this project is to detect the traffic violations like helmet violation,tripple riding violation by two-wheeler vehicles and if any vehicle is found to be violated then the respective vehicle's plate number is extracted using a License plate detection module where we used an open source ** Plate Recognizer API ** and then update the logs and check whether the violated vehicle falls under repeat offender or not.
So,"Repeat offender detection is essential for identifying vehicles or individuals who consistently violate traffic rules, enabling authorities to prioritize enforcement efforts, issue escalated penalties, and enhance road safety by targeting the most high-risk drivers."



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
2. **Set Up Database**
   ```bash
   # Create and apply migrations
   python manage.py makemigrations
   python manage.py migrate
   
   # Create superuser (optional, for admin access)
   python manage.py createsuperuser
3. **Run Web App**
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


## TrafAI FlowChart 
![TrafAI_Flowchart](https://github.com/user-attachments/assets/5480f625-cf8c-472a-8060-221152ac5bb0)



## 📊 Outputs and Results

### Example Detections

1. **Helmet Violation Detection**
   - Detects riders without helmets
   - Identifies multiple riders on a two-wheeler
     ![image](https://github.com/user-attachments/assets/3a713867-4d6f-4d7f-bfb0-bc70ee96c65e)

   

2. **Triple Riding Detection**
   - Identifies three or more people on a two-wheeler
   ![image](https://github.com/user-attachments/assets/76e7fe19-3b16-4962-89fe-bd1cbf5706dd)


3. **License Plate Recognition**
   - Extracts license plate information
   - Processes various plate formats
   ![detected_plate](https://github.com/user-attachments/assets/b44a9933-5da7-44f1-9a3a-f2927904cd91)

4. **Repeat offender Tracking**


The system includes a sophisticated repeat offender tracking system that:

- **Automatically Flags Repeat Offenders**: Vehicles with multiple violations are automatically flagged in the system
- **Violation History**: Maintains a complete history of all violations per vehicle
- **Prioritized Monitoring**: Helps law enforcement focus on habitual offenders
- **Custom Thresholds**: Configurable violation thresholds for flagging repeat offenders
- **Detailed Reporting**: Generates comprehensive reports on repeat offenders
![Repeat offender](https://github.com/user-attachments/assets/d869bd03-5f23-4f02-85de-ecaf2b551abd)


