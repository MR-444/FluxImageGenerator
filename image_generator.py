import random
import replicate
import requests
import json
import io
import os
from PIL import Image, PngImagePlugin
from datetime import datetime
from api_handler import APIHandler
from constants import (
    SEED_MAX_VALUE,
    SLIDER_STEPS_MIN,
    SLIDER_STEPS_MAX,
    SLIDER_GUIDANCE_MIN,
    SLIDER_GUIDANCE_MAX,
    SLIDER_SAFETY_MIN,
    SLIDER_SAFETY_MAX,
    SLIDER_INTERVAL_MIN,
    SLIDER_INTERVAL_MAX,
    GENERATED_IMAGES_DIR,
    TIMESTAMP_FORMAT
)


class ImageGenerator:

    @staticmethod
    def generate_random_seed():
        """Generate a random seed value within the range of 0 to SEED_MAX_VALUE."""
        return random.randint(0, SEED_MAX_VALUE)

    @staticmethod
    def validate_parameters(seed, steps, guidance, safety_tolerance, interval):
        if seed < 0 or seed > SEED_MAX_VALUE:
            return APIHandler.error_message(f"Seed value must be between 0 and {SEED_MAX_VALUE}.")
        if steps < SLIDER_STEPS_MIN or steps > SLIDER_STEPS_MAX:
            return APIHandler.error_message(f"Steps must be between {SLIDER_STEPS_MIN} and {SLIDER_STEPS_MAX}.")
        if guidance < SLIDER_GUIDANCE_MIN or guidance > SLIDER_GUIDANCE_MAX:
            return APIHandler.error_message(
                f"Guidance must be between {SLIDER_GUIDANCE_MIN} and {SLIDER_GUIDANCE_MAX}.")
        if safety_tolerance < SLIDER_SAFETY_MIN or safety_tolerance > SLIDER_SAFETY_MAX:
            return APIHandler.error_message(
                f"Safety Tolerance must be between {SLIDER_SAFETY_MIN} and {SLIDER_SAFETY_MAX}.")
        if interval < SLIDER_INTERVAL_MIN or interval > SLIDER_INTERVAL_MAX:
            return APIHandler.error_message(
                f"Interval must be between {SLIDER_INTERVAL_MIN} and {SLIDER_INTERVAL_MAX}.")
        return None

    @staticmethod
    def convert_parameters(seed, steps, guidance, safety_tolerance, interval):
        if seed > SEED_MAX_VALUE:
            raise ValueError(f"Seed value must be between 0 and {SEED_MAX_VALUE}.")
        return int(seed), int(steps), float(guidance), int(safety_tolerance), float(interval)

    @staticmethod
    def prepare_input_data(prompt, seed, steps, guidance, aspect_ratio, safety_tolerance, interval):
        return {
            "prompt": prompt,
            "seed": seed,
            "steps": steps,
            "guidance": guidance,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "interval": interval
        }

    @staticmethod
    def run_model(api_token, model, input_data):
        APIHandler.set_api_token(api_token)
        try:
            output = replicate.run(model, input=input_data)
            if not output:
                raise ValueError("Model did not return any output. Please check the model and input parameters.")
        except ValueError as e:
            if "Invalid token" in str(e):
                raise ValueError("Wrong API-Key")
            else:
                raise ValueError(f"API Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"API Error: {str(e)}")
        return output

    @staticmethod
    def embed_metadata_in_image(image_data, metadata):
        """Embed metadata into a PNG image stored in memory (image_data)"""
        try:
            # Open the image from the byte data
            image = Image.open(io.BytesIO(image_data))

            # Convert image to PNG format if it isn't already
            if image.format != 'PNG':
                image = image.convert('RGBA')  # Convert to RGBA (suitable for PNG)
                png_image_data = io.BytesIO()
                image.save(png_image_data, format='PNG')
                png_image_data.seek(0)
                image = Image.open(png_image_data)

            # Create a dictionary of metadata (tEXt tag)
            meta = PngImagePlugin.PngInfo()

            # Add parameters as metadata
            meta.add_text("parameters", metadata)

            # Save image with the metadata to a new BytesIO object
            output = io.BytesIO()
            image.save(output, "PNG", pnginfo=meta)
            output.seek(0)

            return output

        except Exception as e:
            raise ValueError(f"Error embedding metadata: {str(e)}")

    @staticmethod
    def generate_image(api_token, model, prompt, seed, randomize, steps, guidance, aspect_ratio,
                       safety_tolerance, interval):
        try:
            # Handle the API Token validation and setting
            api_token_error = APIHandler.validate_api_token(api_token)
            if api_token_error:
                # Return error message, None for image, current seed
                return api_token_error, None, seed

            APIHandler.set_api_token(api_token)

            # Optionally validate parameters
            param_error = ImageGenerator.validate_parameters(seed, steps, guidance, safety_tolerance, interval)
            if param_error:
                # Return parameter error, None for image, current seed
                return param_error, None, seed

            # Convert numeric parameters
            seed, steps, guidance, safety_tolerance, interval = ImageGenerator.convert_parameters(
                seed, steps, guidance, safety_tolerance, interval
            )

            # Prepare model input data
            input_data = ImageGenerator.prepare_input_data(prompt, seed, steps, guidance, aspect_ratio,
                                                           safety_tolerance, interval)

            # Run the model
            output = ImageGenerator.run_model(api_token, model, input_data)

            # Handle the output and download the generated image
            image_url = output[0] if isinstance(output, list) else output
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Retrieve image data
            img_data = image_response.content

            # Prepare metadata
            metadata = json.dumps({
                "model": model,
                "prompt": prompt,
                "seed": seed,
                "steps": steps,
                "guidance": guidance,
                "aspect_ratio": aspect_ratio,
                "safety_tolerance": safety_tolerance,
                "interval": interval
            })

            # Embed metadata into the image
            img_with_metadata = ImageGenerator.embed_metadata_in_image(img_data, metadata)

            # Ensure the directory for saving the image exists
            os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

            # Generate the filename with the proper format
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            filename_with_metadata = os.path.join(GENERATED_IMAGES_DIR, f'image_{timestamp}.png')

            # Save the in-memory image to a file
            with open(filename_with_metadata, 'wb') as f:
                f.write(img_with_metadata.getvalue())

            # Generate a new seed for the next image generation if randomize is checked
            new_seed = seed
            if randomize:
                new_seed = ImageGenerator.generate_random_seed()

            # Return success message, image filename, new seed
            return APIHandler.success_message(model, filename_with_metadata), filename_with_metadata, new_seed

        except ValueError as e:
            # Return validation error, None for image, current seed
            return APIHandler.error_message(f"Validation Error: {str(e)}"), None, seed
        except requests.exceptions.RequestException as e:
            # Return request error, None for image, current seed
            return APIHandler.error_message(f"Error downloading image: {str(e)}"), None, seed
        except Exception as e:
            # Return unknown error, None for image, current seed
            return APIHandler.error_message(f"An unknown error occurred: {str(e)}"), None, seed
        finally:
            APIHandler.clear_api_token()
