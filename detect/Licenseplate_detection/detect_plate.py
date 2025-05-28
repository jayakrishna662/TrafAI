from plate_reader import extract_plate_text_from_api

API_KEY = " " #paste your api key here

if __name__ == "__main__":
    image_path = " " #give your image path

    plate_text = extract_plate_text_from_api(image_path, API_KEY)

    if plate_text:
        print(f"Final Detected Plate: {plate_text}")
    else:
        print("No plate detected in image.")
