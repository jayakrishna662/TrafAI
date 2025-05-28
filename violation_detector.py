import os
import cv2
from pathlib import Path
import shutil
from datetime import datetime

# Import detection modules
from detect.Helmet_detection.helmet import helmet_violation_in_image
from detect.Licenseplate_detection.plate_reader import extract_plate_text_from_api
from detect.vehicle_detection import detect_vehicles
from detect.Trippleriding_detection.tripple import TripleRiderDetector
from ultralytics import YOLO

# Import database
#from database import ViolationDatabase


class ViolationDetector:
    def __init__(self):
        # Initialize paths
        self.current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = self.current_dir / "output_images"
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize models
        print("[INFO] Loading detection models...")
        # Use the same model that works in helmet.py directly
        self.helmet_model_path = (
            self.current_dir
            / "detect"
            / "Helmet_detection"
            / "hemletYoloV8_100epochs.pt"
        )
        print(f"[INFO] Using helmet model: {self.helmet_model_path}")
        self.helmet_model = YOLO(str(self.helmet_model_path))

        # Initialize triple riding detector
        self.triple_rider_detector = TripleRiderDetector()

        # API Key for license plate recognition
        self.plate_api_key = " " #paste your api key here

        print("[INFO] Violation detection system initialized.")

    def process_image(self, image_path):
        """Process an image for traffic violations"""
        # Check if the image exists
        if not os.path.exists(image_path):
            print(f"[ERROR] Image not found: {image_path}")
            return None

        print(f"[INFO] Processing image: {image_path}")
        result = {
            "violations": [],
            "plate_number": None,
            "is_repeat_offender": False,
            "violation_count": 0,
            "image_path": image_path,
            "output_path": None,
        }

        # Create a timestamped output image path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(image_path)
        output_path = os.path.join(
            str(self.output_dir), f"processed_{timestamp}_{filename}"
        )

        # Copy the original image to the output path for annotation
        shutil.copy(image_path, output_path)
        result["output_path"] = output_path

        # Check for helmet violation using the actual detection function
        print(f"[INFO] Checking for helmet violations in: {image_path}")
        has_helmet_violation = helmet_violation_in_image(self.helmet_model, image_path)
        print(f"[INFO] Helmet detection result: {has_helmet_violation}")

        if has_helmet_violation:
            result["violations"].append("No Helmet")
            print("[INFO] Helmet violation detected.")

        # Check for triple riding violation
        print("[INFO] Checking for triple riding violation...")
        # Use a lower confidence threshold for triple riding detection to improve reliability
        self.triple_rider_detector.confidence = (
            0.3  # Adjust confidence for better detection
        )
        has_triple_riding_violation = (
            self.triple_rider_detector.has_triple_riding_violation_from_path(image_path)
        )
        print(f"[INFO] Triple riding detection result: {has_triple_riding_violation}")

        if has_triple_riding_violation:
            result["violations"].append("Triple Riding")
            print("[INFO] Triple riding violation detected.")
        else:
            print("[INFO] No triple riding violation detected.")

        # Use vehicle detection (this creates a vehicle_detection_output.jpg file)
        detect_vehicles(image_path)

        # Extract license plate if any violation was detected
        if result["violations"]:
            plate_number = extract_plate_text_from_api(image_path, self.plate_api_key)
            if plate_number:
                result["plate_number"] = plate_number

                # Logging and repeat offender logic now handled by Django view
                print(
                    f"[INFO] Plate: {plate_number}, Violations: {result['violations']}"
                )
            else:
                print("[WARNING] License plate not detected. Violation not logged.")
        else:
            print("[INFO] No violations detected in the image.")

        return result

    def get_repeat_offenders(self):
        """No longer implemented. Use Django ORM in views."""
        return []

    def get_violation_history(self, plate_number):
        """No longer implemented. Use Django ORM in views."""
        return []

    def get_all_violations(self):
        """No longer implemented. Use Django ORM in views."""
        return []

    def delete_violation(self, violation_id):
        """No longer implemented. Use Django ORM in views."""
        return None

    def delete_all_violations(self):
        """No longer implemented. Use Django ORM in views."""
        return None
