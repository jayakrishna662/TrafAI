import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import os
from PIL import Image


class TripleRiderDetector:
    def __init__(self, confidence=0.35, iou=0.3, model_size="m"):
        self.confidence = confidence
        self.iou = iou

        # Initialize YOLO model based on size
        try:
            model_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(model_dir, f"yolov8{model_size}.pt")
            print(f"Loading YOLO model: {model_path}")
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Attempting alternative loading method...")
            os.environ["TORCH_WEIGHTS_ONLY"] = "true"
            self.model = YOLO(model_path)

        self.tracker = sv.ByteTrack()
        self.box_annotator = sv.BoxAnnotator(thickness=2)

    def calculate_overlap(self, box1, box2):
        """Calculate IoU between two bounding boxes"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        if x2 < x1 or y2 < y1:
            return 0.0

        intersection = (x2 - x1) * (y2 - y1)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

        # Calculate IoU
        iou = intersection / float(box1_area + box2_area - intersection)
        return iou

    def filter_overlapping_detections(self, boxes, scores, classes, iou_threshold=0.4):
        """Filter out overlapping detections keeping the ones with higher confidence"""
        indices = []

        # Convert to numpy arrays if they aren't already
        boxes = np.array(boxes)
        scores = np.array(scores)

        print(f"\nFiltering {len(boxes)} detections with IoU threshold {iou_threshold}")

        # Get indices sorted by score
        score_indices = np.argsort(scores)[::-1]

        while len(score_indices) > 0:
            # Keep the current highest scoring box
            current_index = score_indices[0]
            indices.append(current_index)

            # Calculate IoU of the kept box with the rest
            ious = [
                self.calculate_overlap(boxes[current_index], boxes[i])
                for i in score_indices[1:]
            ]

            # Print debug information
            print(
                f"\nKeeping box {current_index} with score {scores[current_index]:.2f}"
            )
            print(f"Box coordinates: {boxes[current_index]}")

            # Filter out boxes with high IoU
            filtered_indices = []
            for i, iou in zip(score_indices[1:], ious):
                if iou < iou_threshold:
                    filtered_indices.append(i)
                else:
                    print(
                        f"Filtering out box {i} with IoU {iou:.2f} and score {scores[i]:.2f}"
                    )

            score_indices = filtered_indices

        print(f"After filtering: {len(indices)} detections remain")
        return indices

    def detect_triple_riders(self, frame):
        """Detect triple riders in a frame and return if violation detected"""
        print("Running YOLO detection...")
        # Run detection with different confidence thresholds for persons and motorcycles
        # Use a lower confidence threshold to ensure we detect all potential riders
        results = self.model(frame, classes=[0, 3], conf=self.confidence)[0]
        print(f"YOLO detection completed. Found {len(results.boxes)} objects")

        # Flag to track if violations were detected
        violations_detected = False

        # Convert YOLO results to supervision Detections format
        detections = sv.Detections(
            xyxy=results.boxes.xyxy.cpu().numpy(),
            confidence=results.boxes.conf.cpu().numpy(),
            class_id=results.boxes.cls.cpu().numpy().astype(int),
        )

        if len(detections) == 0:
            print("No objects detected in the frame")
            return False

        print(f"Detected {len(detections)} objects before filtering.")

        # Track objects
        detections = self.tracker.update_with_detections(detections)
        print("Object tracking completed")

        # Extract motorcycle and people boxes with scores
        motorcycles = []
        motorcycles_scores = []
        people = []
        people_scores = []

        for i, (xyxy, conf, class_id) in enumerate(
            zip(detections.xyxy, detections.confidence, detections.class_id)
        ):
            # Person class_id = 0, Motorcycle class_id = 3
            if class_id == 0:  # Person
                people.append(xyxy)
                people_scores.append(conf)
            elif class_id == 3:  # Motorcycle
                motorcycles.append(xyxy)
                motorcycles_scores.append(conf)

        print(
            f"Initial detection: {len(people)} people and {len(motorcycles)} motorcycles"
        )

        # Filter out overlapping motorcycles using IoU
        if len(motorcycles) > 1:
            motorcycles_indices = self.filter_overlapping_detections(
                motorcycles, motorcycles_scores, [3] * len(motorcycles), self.iou
            )
            motorcycles = [motorcycles[i] for i in motorcycles_indices]
            motorcycles_scores = [motorcycles_scores[i] for i in motorcycles_indices]

        print(
            f"After motorcycle filtering: {len(people)} people and {len(motorcycles)} motorcycles"
        )

        # Store violations for annotation
        violations = []
        for motorcycle in motorcycles:
            riders = []
            motorcycle_center = (
                (motorcycle[0] + motorcycle[2]) / 2,
                (motorcycle[1] + motorcycle[3]) / 2,
            )
            motorcycle_width = motorcycle[2] - motorcycle[0]
            motorcycle_height = motorcycle[3] - motorcycle[1]

            print(
                f"\nChecking motorcycle at {motorcycle_center} with size {motorcycle_width}x{motorcycle_height}"
            )

            # Sort people by their vertical position (top to bottom)
            sorted_people = sorted(
                enumerate(people), key=lambda x: x[1][1]
            )  # Sort by y-coordinate
            print(f"People sorted by vertical position: {len(sorted_people)}")

            for idx, person in sorted_people:
                person_center = (
                    (person[0] + person[2]) / 2,
                    (person[1] + person[3]) / 2,
                )
                person_height = person[3] - person[1]
                person_width = person[2] - person[0]

                # Calculate distance from person center to motorcycle center
                distance = np.sqrt(
                    (person_center[0] - motorcycle_center[0]) ** 2
                    + (person_center[1] - motorcycle_center[1]) ** 2
                )

                # More lenient distance threshold based on motorcycle size
                distance_threshold = (
                    max(motorcycle_width, motorcycle_height) * 2.0
                )  # 100% more lenient

                # Calculate vertical overlap
                vertical_overlap = min(person[3], motorcycle[3]) - max(
                    person[1], motorcycle[1]
                )
                vertical_ratio = vertical_overlap / min(
                    person_height, motorcycle_height
                )

                # Calculate horizontal overlap
                horizontal_overlap = min(person[2], motorcycle[2]) - max(
                    person[0], motorcycle[0]
                )
                horizontal_ratio = horizontal_overlap / min(
                    person_width, motorcycle_width
                )

                print(f"\nPerson {idx} at {person_center}:")
                print(
                    f"  Distance: {distance:.2f}, threshold: {distance_threshold:.2f}"
                )
                print(f"  Vertical ratio: {vertical_ratio:.2f}")
                print(f"  Horizontal ratio: {horizontal_ratio:.2f}")
                print(f"  Confidence: {people_scores[idx]:.2f}")

                # Consider a person as a rider if they meet any of these criteria:
                # Make criteria more lenient to detect all riders
                if (
                    distance < distance_threshold
                    or vertical_ratio > 0.1
                    or horizontal_ratio > 0.1
                ):
                    riders.append((person, people_scores[idx]))
                    print(f"  Added as rider!")
                else:
                    print(f"  Not considered a rider")

            print(f"\nFound {len(riders)} riders for this motorcycle")

            # Sort riders by confidence score
            riders.sort(key=lambda x: x[1], reverse=True)

            # Only flag as a violation if 3 or more riders are detected
            if len(riders) >= 3:  # Triple riding requires 3+ riders
                violations.append((motorcycle, [r[0] for r in riders]))
                print(f"Violation detected with {len(riders)} riders!")
                # Set violation detected flag
                violations_detected = True

                # For debugging only
                violation_type = "TRIPLE RIDING"
                print(f"VIOLATION DETECTED: {violation_type} with {len(riders)} riders")

        return violations_detected

    def preprocess_image(self, image):
        """Apply preprocessing to enhance image quality while preserving color channels"""
        # Create a copy of the original image
        enhanced = image.copy()

        # Split the image into its BGR channels
        b, g, r = cv2.split(enhanced)

        # Apply CLAHE for contrast enhancement on each channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        b = clahe.apply(b)
        g = clahe.apply(g)
        r = clahe.apply(r)

        # Merge the enhanced channels back
        enhanced = cv2.merge([b, g, r])

        # Apply slight sharpening filter
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)

        # Ensure output image has 3 channels as required by YOLO
        if len(enhanced.shape) == 2 or enhanced.shape[2] != 3:
            print("Warning: Converting image to ensure 3 channels")
            if len(enhanced.shape) == 2:  # If somehow it's grayscale
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        return enhanced

    def has_triple_riding_violation_from_path(self, image_path):
        """Check if there are triple riding violations in an image and return True/False"""
        print(f"\nProcessing image: {image_path}")

        # Open image
        image = cv2.imread(image_path)

        if image is None:
            print(f"Error: Image not found at {image_path}")
            return False

        image = self.preprocess_image(image)

        # Detect violations and return the result (True if violation detected, False otherwise)
        return self.detect_triple_riders(image)


if __name__ == "__main__":
    # Set image path directly here
    image_path = r"C:\Users\Jaykr\Desktop\cursor_project\input_images\tp4.jpg"  # Change this to your image path

    detector = TripleRiderDetector()
    result = detector.has_triple_riding_violation_from_path(image_path)

    if result:
        print("\n== RESULT: TRIPLE RIDING VIOLATION DETECTED ==")
    else:
        print("\n== RESULT: NO VIOLATION DETECTED ==")
