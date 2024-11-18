# image_generator.py

import io
import json
import os
import random
from datetime import datetime

import replicate
import requests
from PIL import Image, PngImagePlugin

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
    TIMESTAMP_FORMAT,
    IMAGE_WIDTH_MIN,
    IMAGE_WIDTH_MAX,
    IMAGE_HEIGHT_MIN,
    IMAGE_HEIGHT_MAX,
    SLIDER_OUTPUT_QUALITY_MIN,
    SLIDER_OUTPUT_QUALITY_MAX
)


class ImageGenerator:
    VALID_ASPECT_RATIOS = {"1:1", "16:9", "2:3", "3:2", "4:5", "5:4", "9:16", "21:9", "9:21", "3:4", "4:3", "custom"}

    @staticmethod
    def generate_random_seed():
        """Generate a random seed value within the range of 0 to SEED_MAX_VALUE."""
        return random.randint(0, SEED_MAX_VALUE)

    @staticmethod
    def validate_parameters(seed, steps, guidance, safety_tolerance, interval, width, height, output_quality,
                            aspect_ratio, raw):
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
        if width < IMAGE_WIDTH_MIN or width > IMAGE_WIDTH_MAX:
            return APIHandler.error_message(
                f"Width must be between {IMAGE_WIDTH_MIN} and {IMAGE_WIDTH_MAX}.")
        if height < IMAGE_HEIGHT_MIN or height > IMAGE_HEIGHT_MAX:
            return APIHandler.error_message(
                f"Height must be between {IMAGE_HEIGHT_MIN} and {IMAGE_HEIGHT_MAX}.")
        if width % 16 != 0:
            return APIHandler.error_message("Width must be a multiple of 16.")
        if height % 16 != 0:
            return APIHandler.error_message("Height must be a multiple of 16.")
        if output_quality < SLIDER_OUTPUT_QUALITY_MIN or output_quality > SLIDER_OUTPUT_QUALITY_MAX:
            return APIHandler.error_message(
                f"Output Quality must be between {SLIDER_OUTPUT_QUALITY_MIN} and {SLIDER_OUTPUT_QUALITY_MAX}.")
        if aspect_ratio not in ImageGenerator.VALID_ASPECT_RATIOS:
            return APIHandler.error_message("Aspect Ratio is not valid.")
        if not isinstance(raw, bool):
            return APIHandler.error_message("Raw must be a boolean value.")
        return None

    @staticmethod
    def convert_parameters(seed, steps, guidance, safety_tolerance, interval, width, height, output_quality):
        if seed > SEED_MAX_VALUE:
            raise ValueError(f"Seed value must be between 0 and {SEED_MAX_VALUE}.")
        return int(seed), int(steps), float(guidance), int(safety_tolerance), float(interval), int(width), int(
            height), int(output_quality)

    @staticmethod
    def prepare_input_data(prompt, seed, steps, guidance, aspect_ratio, width, height, safety_tolerance, interval, raw,
                           output_format, output_quality, prompt_upsampling):
        input_data = {
            "prompt": prompt,
            "seed": seed,
            "steps": steps,
            "guidance": guidance,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "raw": raw,
            "interval": interval,
            "output_format": output_format,
            "output_quality": output_quality,
            "prompt_upsampling": prompt_upsampling
        }
        # Conditionally add width and height if aspect ratio is 'custom'
        if aspect_ratio == "custom":
            input_data["width"] = width
            input_data["height"] = height

        return input_data

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
        try:
            image = Image.open(io.BytesIO(image_data))

            # Convert image to PNG format if it isn't already
            if image.format != 'PNG':
                image = image.convert('RGBA')  # Convert to RGBA (suitable for PNG)
                png_image_data = io.BytesIO()
                image.save(png_image_data, format='PNG')
                png_image_data.seek(0)
                image = Image.open(png_image_data)

            meta = PngImagePlugin.PngInfo()
            meta.add_text("parameters", metadata)
            output = io.BytesIO()
            image.save(output, "PNG", pnginfo=meta)
            output.seek(0)
            return output

        except Exception as e:
            raise ValueError(f"Error embedding metadata: {str(e)}")

    @staticmethod
    def generate_image(api_token, model, prompt, seed, randomize, steps, guidance, aspect_ratio,
                       width, height, safety_tolerance, interval, raw, output_format, output_quality, prompt_upsampling):
        try:
            api_token_error = APIHandler.validate_api_token(api_token)
            if api_token_error:
                _, error_message = api_token_error
                return error_message, None, seed

            APIHandler.set_api_token(api_token)

            param_error = ImageGenerator.validate_parameters(seed, steps, guidance, safety_tolerance, interval, width,
                                                             height, output_quality, aspect_ratio, raw)
            if param_error:
                _, error_message = param_error
                return error_message, None, seed

            seed, steps, guidance, safety_tolerance, interval, width, height, output_quality = ImageGenerator.convert_parameters(
                seed, steps, guidance, safety_tolerance, interval, width, height, output_quality
            )

            input_data = ImageGenerator.prepare_input_data(prompt, seed, steps, guidance, aspect_ratio, width, height,
                                                           safety_tolerance, interval, raw, output_format, output_quality,
                                                           prompt_upsampling)

            output = ImageGenerator.run_model(api_token, model, input_data)

            image_url = output[0] if isinstance(output, list) else output
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            img_data = image_response.content

            metadata = json.dumps({
                "model": model,
                "prompt": prompt,
                "seed": seed,
                "steps": steps,
                "guidance": guidance,
                "aspect_ratio": aspect_ratio,
                "width": width,
                "height": height,
                "safety_tolerance": safety_tolerance,
                "interval": interval,
                "raw": raw,
                "output_format": output_format,
                "output_quality": output_quality,
                "prompt_upsampling": prompt_upsampling
            })

            img_with_metadata = ImageGenerator.embed_metadata_in_image(img_data, metadata)

            os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            filename_with_metadata = os.path.join(GENERATED_IMAGES_DIR, f'image_{timestamp}.{output_format}')

            # Save the in-memory image to a file
            with open(filename_with_metadata, 'wb') as f:
                if output_format == 'jpg':
                    Image.open(img_with_metadata).convert('RGB').save(f, format='JPEG', quality=output_quality)
                else:
                    f.write(img_with_metadata.getvalue())

            new_seed = seed
            if randomize:
                new_seed = ImageGenerator.generate_random_seed()

            _, success_message = APIHandler.success_message(model, filename_with_metadata)
            return success_message, filename_with_metadata, new_seed

        except ValueError as e:
            _, error_message = APIHandler.error_message(f"Validation Error: {str(e)}")
            return error_message, None, seed
        except requests.exceptions.RequestException as e:
            _, error_message = APIHandler.error_message(f"Error downloading image: {str(e)}")
            return error_message, None, seed
        except Exception as e:
            _, error_message = APIHandler.error_message(f"An unknown error occurred: {str(e)}")
            return error_message, None, seed
        finally:
            APIHandler.clear_api_token()
