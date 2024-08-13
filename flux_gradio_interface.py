import os
import requests
from datetime import datetime
from PIL import Image
import gradio as gr
import replicate

# Constants
ERROR_COLOR = "<span style='color: red;'>"
SUCCESS_COLOR = "<span style='color: green;'>"
GENERATED_IMAGES_DIR = 'generated_images'
API_TOKEN_ENV_VAR = "REPLICATE_API_TOKEN"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
SLIDER_STEPS_MIN = 1
SLIDER_STEPS_MAX = 50
SLIDER_STEPS_DEFAULT = 25
SLIDER_GUIDANCE_MIN = 2
SLIDER_GUIDANCE_MAX = 5
SLIDER_GUIDANCE_STEP = 0.1
SLIDER_GUIDANCE_DEFAULT = 3
SLIDER_SAFETY_MIN = 1
SLIDER_SAFETY_MAX = 5
SLIDER_SAFETY_DEFAULT = 2
SLIDER_INTERVAL_MIN = 1
SLIDER_INTERVAL_MAX = 4
SLIDER_INTERVAL_STEP = 0.1
SLIDER_INTERVAL_DEFAULT = 2


def error_message(message):
    return None, f"{ERROR_COLOR}{message}</span>"


def success_message(model, filename):
    return filename, f"{SUCCESS_COLOR}Image generated successfully using {model} and saved as {filename}!</span>"


def validate_api_token(api_token):
    if not api_token:
        return error_message("API Token is required.")
    return None


def convert_parameters(seed, steps, guidance, safety_tolerance, interval):
    try:
        return int(seed), int(steps), float(guidance), int(safety_tolerance), float(interval)
    except ValueError:
        raise ValueError("Invalid input values provided. Please check your parameters.")


def set_api_token(api_token):
    os.environ[API_TOKEN_ENV_VAR] = api_token


def clear_api_token():
    os.environ[API_TOKEN_ENV_VAR] = ""


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


def handle_api_token(api_token):
    token_error = validate_api_token(api_token)
    if token_error:
        return token_error
    set_api_token(api_token)
    return None


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


def run_model(api_token, model, input_data):
    handle_api_token(api_token)
    output = replicate.run(model, input=input_data)
    if not output:
        raise ValueError("Model did not return any output")
    return output


def generate_image(api_token, model, prompt, seed, steps, guidance, aspect_ratio, safety_tolerance, interval):
    try:
        api_token_error = handle_api_token(api_token)
        if api_token_error:
            return api_token_error

        seed, steps, guidance, safety_tolerance, interval = convert_parameters(seed, steps, guidance, safety_tolerance,
                                                                               interval)
        input_data = prepare_input_data(prompt, seed, steps, guidance, aspect_ratio, safety_tolerance, interval)

        output = run_model(api_token, model, input_data)
        image_url = output[0] if isinstance(output, list) else output
        filename = download_image(image_url)
        return success_message(model, filename)
    except Exception as e:
        return error_message(f"An error occurred: {str(e)}")
    finally:
        clear_api_token()


iface = gr.Interface(
    fn=generate_image,
    inputs=[
        gr.Textbox(label="API Token", placeholder="Enter your Replicate API Token", type="password"),
        gr.Dropdown(["black-forest-labs/flux-dev", "black-forest-labs/flux-pro", "black-forest-labs/flux-schnell"],
                    label="Model", value="black-forest-labs/flux-pro"),
        gr.Textbox(label="Prompt", placeholder="Describe the image you want to generate"),
        gr.Number(label="Seed", value=42),
        gr.Slider(SLIDER_STEPS_MIN, SLIDER_STEPS_MAX, SLIDER_STEPS_DEFAULT, step=1, label="Steps"),
        gr.Slider(SLIDER_GUIDANCE_MIN, SLIDER_GUIDANCE_MAX, SLIDER_GUIDANCE_DEFAULT, step=SLIDER_GUIDANCE_STEP,
                  label="Guidance"),
        gr.Dropdown(["1:1", "16:9", "2:3", "3:2", "4:5", "5:4", "9:16"], label="Aspect Ratio", value="1:1"),
        gr.Slider(SLIDER_SAFETY_MIN, SLIDER_SAFETY_MAX, SLIDER_SAFETY_DEFAULT, step=1, label="Safety Tolerance"),
        gr.Slider(SLIDER_INTERVAL_MIN, SLIDER_INTERVAL_MAX, SLIDER_INTERVAL_DEFAULT, step=SLIDER_INTERVAL_STEP,
                  label="Interval")
    ],
    outputs=[
        gr.Image(label="Generated Image"),
        gr.HTML(label="Status")
    ],
    title="Flux Image Generator",
    description="Generate images using various Flux models. Adjust parameters to customize the output.",
    theme="default",
    allow_flagging="never"
)
iface.launch(allowed_paths=["."])  # This allows HTML in the output
