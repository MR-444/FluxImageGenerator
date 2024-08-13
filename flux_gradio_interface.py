import gradio as gr
import replicate
import requests
import os
from datetime import datetime
from PIL import Image


def generate_image(api_token, model, prompt, seed, steps, guidance, aspect_ratio, safety_tolerance, interval):
    try:
        # Validate API token
        if not api_token:
            return None, "<span style='color: red;'>API Token is required.</span>"

        # Convert inputs to proper types
        try:
            seed = int(seed)
            steps = int(steps)
            guidance = float(guidance)
            safety_tolerance = int(safety_tolerance)
            interval = float(interval)
        except ValueError:
            return None, "<span style='color: red;'>Invalid input values provided. Please check your parameters.</span>"

        # Set the API token securely
        os.environ["REPLICATE_API_TOKEN"] = api_token

        try:
            # Prepare input data for the model
            input_data = {
                "prompt": prompt,
                "seed": seed,
                "steps": steps,
                "guidance": guidance,
                "aspect_ratio": aspect_ratio,
                "safety_tolerance": safety_tolerance,
                "interval": interval
            }

            # Create a prediction using the selected model
            output = replicate.run(model, input=input_data)
            if not output:
                raise ValueError("Model did not return any output")

            # Ensure the output is a string URL and not a list
            image_url = output[0] if isinstance(output, list) else output

            response = requests.get(image_url)
            if response.status_code == 200:
                os.makedirs('generated_images', exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_images/image_{timestamp}.png"

                with open(filename, "wb") as file:
                    file.write(response.content)

                return filename, f"<span style='color: green;'>Image generated successfully using {model} and saved as {filename}!</span>"
            else:
                return None, f"<span style='color: red;'>Failed to download the image. Status code: {response.status_code}</span>"

        finally:
            os.environ["REPLICATE_API_TOKEN"] = ""

    except Exception as e:
        return None, f"<span style='color: red;'>An error occurred: {str(e)}</span>"


iface = gr.Interface(
    fn=generate_image,
    inputs=[
        gr.Textbox(label="API Token", placeholder="Enter your Replicate API Token", type="password"),
        gr.Dropdown(
            ["black-forest-labs/flux-dev", "black-forest-labs/flux-pro", "black-forest-labs/flux-schnell"],
            label="Model",
            value="black-forest-labs/flux-pro"
        ),
        gr.Textbox(label="Prompt", placeholder="Describe the image you want to generate"),
        gr.Number(label="Seed", value=42),
        gr.Slider(1, 50, 25, step=1, label="Steps"),
        gr.Slider(2, 5, 3, step=0.1, label="Guidance"),
        gr.Dropdown(["1:1", "16:9", "2:3", "3:2", "4:5", "5:4", "9:16"], label="Aspect Ratio", value="1:1"),
        gr.Slider(1, 5, 2, step=1, label="Safety Tolerance"),
        gr.Slider(1, 4, 2, step=0.1, label="Interval")
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
