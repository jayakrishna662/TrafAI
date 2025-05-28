from ultralytics import YOLO
import cv2
from pathlib import Path
import os

# Set class IDs based on your trained model
RIDER_CLASS_ID = 0
HELMET_CLASS_ID = 1


def helmet_violation_in_image(model, image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Cannot read image: {image_path}")
        return

    # Use lower confidence threshold to ensure helmets are detected
    results = model(image, conf=0.25)
    boxes = results[0].boxes

    riders = []
    helmets = []

    for box in boxes:
        cls_id = int(box.cls[0])
        xyxy = box.xyxy[0].tolist()  # x1, y1, x2, y2

        if cls_id == RIDER_CLASS_ID:
            riders.append(xyxy)
        elif cls_id == HELMET_CLASS_ID:
            helmets.append(xyxy)

    violation_detected = False

    for rider_box in riders:
        rider_x1, rider_y1, rider_x2, rider_y2 = rider_box
        # Define a larger head region (top 1/2 instead of 1/3) to improve helmet association
        rider_head_region = [
            rider_x1,
            rider_y1,
            rider_x2,
            rider_y1 + (rider_y2 - rider_y1) // 2,
        ]  # top 1/2
        print(f"Rider at coordinates: {rider_box}, head region: {rider_head_region}")

        helmet_found = False
        for helmet_box in helmets:
            helmet_x1, helmet_y1, helmet_x2, helmet_y2 = helmet_box

            # Check if helmet overlaps rider head region
            # Calculate overlap area between helmet and head region
            overlap_width = min(helmet_x2, rider_head_region[2]) - max(
                helmet_x1, rider_head_region[0]
            )
            overlap_height = min(helmet_y2, rider_head_region[3]) - max(
                helmet_y1, rider_head_region[1]
            )

            # Print debug information
            print(
                f"Checking helmet at {[helmet_x1, helmet_y1, helmet_x2, helmet_y2]} with rider head"
            )

            # Check if there's any overlap (more lenient criteria)
            if overlap_width > 0 and overlap_height > 0:
                helmet_found = True
                break

        if not helmet_found:
            violation_detected = True
            break  # One helmetless rider is enough to flag a violation

    if violation_detected:
        print("Helmet violation detected 🚫")
        return True
    else:
        print("Helmet violation not detected ✅")
        return False


def main():
    # Use absolute path to find the model
    model_path = r"C:\Users\Jaykr\Desktop\cursor_project\detect\Helmet_detection\hemletYoloV8_100epochs.pt"  # Use helmetBest.pt which is available
    image_path = r"C:\Users\Jaykr\Desktop\cursor_project\input_images\tp3.jpg"  # Change as needed

    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found at: {model_path}")
        return

    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found at: {image_path}")
        return

    print(f"[INFO] Loading YOLOv8 model: {model_path}")
    model = YOLO(model_path)
    print("[INFO] Model loaded successfully.")

    helmet_violation_in_image(model, image_path)


if __name__ == "__main__":
    main()
