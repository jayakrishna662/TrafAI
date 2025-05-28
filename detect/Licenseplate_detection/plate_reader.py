import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_plate_text_from_api(image_path, api_token):
    url = "https://api.platerecognizer.com/v1/plate-reader/"
    headers = {"Authorization": f"Token {api_token}"}

    try:
        with open(image_path, "rb") as img_file:
            response = requests.post(url, files={"upload": img_file}, headers=headers)

        # Accept both 200 (OK) and 201 (Created) as success
        if response.status_code not in (200, 201):
            logger.error(f"API request failed: {response.status_code} {response.text}")
            return None

        result = response.json()
        logger.info(f"API response: {result}")

        if result["results"]:
            plate_text = result["results"][0]["plate"].upper()
            confidence = result["results"][0]["score"]
            logger.info(f"Detected plate: {plate_text} (confidence: {confidence:.2f})")
            print(f"Detected plate: {plate_text} (confidence: {confidence:.2f})")
            return plate_text

        logger.info("No plate text extracted.")
        print("No license plate detected.")
        return None

    except Exception as e:
        logger.error(f"Exception during API request: {str(e)}")
        return None
