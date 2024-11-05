# api_handler.py
import os
from datetime import datetime

import requests

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
        """Generate and return a formatted error message."""
        return None, f"{ERROR_COLOR}{message}</span>"

    @staticmethod
    def success_message(model, filename):
        """Generate and return a formatted success message."""
        return True, f"{SUCCESS_COLOR}Image generated successfully using {model} and saved as {filename}!</span>"

    @staticmethod
    def validate_api_token(api_token):
        """Validate the given API token."""
        if not api_token:
            return APIHandler.error_message("API Token is required.")
        return None

    @staticmethod
    def set_api_token(api_token):
        """Set the given API token as an environment variable."""
        os.environ[API_TOKEN_ENV_VAR] = api_token

    @staticmethod
    def clear_api_token():
        """Clear the API token environment variable."""
        if API_TOKEN_ENV_VAR in os.environ:
            del os.environ[API_TOKEN_ENV_VAR]

    @staticmethod
    def download_image(image_url):
        """Download an image from the given URL and save it to a file."""
        response = requests.get(image_url)
        if response.status_code == 200:
            os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)  # Ensure the directory exists
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            filename = os.path.join(GENERATED_IMAGES_DIR, f"image_{timestamp}.png")
            with open(filename, "wb") as file:
                file.write(response.content)
            return filename
        raise ValueError(f"Failed to download the image. Status code: {response.status_code}")
