import cv2
from ultralytics import YOLO
import os

# Load the pretrained YOLOv8 model (use yolov8n.pt or yolov8s.pt for better speed/accuracy)
model = YOLO("yolov8x.pt")  # Change to yolov8s.pt for more accuracy

# Define allowed vehicle classes
VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck", "bicycle"]


def detect_vehicles(image_path):
    # Run YOLO inference
    results = model(image_path)[0]

    # Load the image using OpenCV
    image = cv2.imread(image_path)

    for box in results.boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]

        if class_name in VEHICLE_CLASSES:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            label = f"{class_name} ({conf:.2f})"

            # Draw rectangle and label
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                image,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

    # Save output
    output_path = os.path.join(
        os.path.dirname(image_path), "vehicle_detection_output.jpg"
    )
    cv2.imwrite(output_path, image)
    print(f"[INFO] Saved detection result to: {output_path}")


# --- Test with your image ---
if __name__ == "__main__":
    test_image = r"C:\Users\Jaykr\Desktop\cursor_project\Riding-a-bike-without-a-helmet-in-Hyderabad_-Well-the-IIT-and-the-city-police-are-working-on-a-system-to-fine-you..jpg"
    detect_vehicles(test_image)
