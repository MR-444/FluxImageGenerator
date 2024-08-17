# image_generator.py
import random
import replicate
import requests
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
            "aspect_ratio": aspect_ratio,  # Pass through as-is
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
    def generate_image(api_token, model, prompt, randomize, seed, steps, guidance, aspect_ratio,
                       safety_tolerance, interval):
        try:
            # Handle the API Token validation and setting
            api_token_error = APIHandler.validate_api_token(api_token)
            if api_token_error:
                return api_token_error

            APIHandler.set_api_token(api_token)

            # Optionally validate parameters
            param_error = ImageGenerator.validate_parameters(seed, steps, guidance, safety_tolerance, interval)
            if param_error:
                return param_error

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
            filename = APIHandler.download_image(image_url)

            # Generate a new seed for the next image generation
            new_seed = ImageGenerator.generate_random_seed()
            return APIHandler.success_message(model,
                                              filename), new_seed  # Return the success message and new seed value

        except ValueError as e:
            return APIHandler.error_message(f"Validation Error: {str(e)}")
        except requests.exceptions.RequestException as e:
            return APIHandler.error_message(f"Error downloading image: {str(e)}")
        except Exception as e:
            return APIHandler.error_message(f"An unknown error occurred: {str(e)}")
        finally:
            APIHandler.clear_api_token()