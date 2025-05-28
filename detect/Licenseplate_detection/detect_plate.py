from plate_reader import extract_plate_text_from_api

API_KEY = "56531315402d98cb449fcf05f999e057b052696b"

if __name__ == "__main__":
    image_path = r"C:\Users\Jaykr\Desktop\cursor_project\input_images\nohelmet1.jpg"

    plate_text = extract_plate_text_from_api(image_path, API_KEY)

    if plate_text:
        print(f"Final Detected Plate: {plate_text}")
    else:
        print("No plate detected in image.")
