# api_handler.py
import os
import requests
from datetime import datetime
from constants import (
    ERROR_COLOR,
    SUCCESS_COLOR,
    GENERATED_IMAGES_DIR,
    API_TOKEN_ENV_VAR,
    TIMESTAMP_FORMAT
)


class APIHandler:
    @staticmethod
    def error_message(message):
        return None, f"{ERROR_COLOR}{message}</span>"

    @staticmethod
    def success_message(model, filename):
        return filename, f"{SUCCESS_COLOR}Image generated successfully using {model} and saved as {filename}!</span>"

    @staticmethod
    def validate_api_token(api_token):
        if not api_token:
            return APIHandler.error_message("API Token is required.")
        return None

    @staticmethod
    def set_api_token(api_token):
        os.environ[API_TOKEN_ENV_VAR] = api_token

    @staticmethod
    def clear_api_token():
        os.environ[API_TOKEN_ENV_VAR] = ""

    @staticmethod
    def download_image(image_url):
        response = requests.get(image_url)
        if response.status_code == 200:
            os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            filename = f"{GENERATED_IMAGES_DIR}/image_{timestamp}.png"
            with open(filename, "wb") as file:
                file.write(response.content)
            return filename
        raise ValueError(f"Failed to download the image. Status code: {response.status_code}")
