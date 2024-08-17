# main.py
import gradio as gr
from image_generator import ImageGenerator
from constants import (
    SLIDER_STEPS_MIN,
    SLIDER_STEPS_MAX,
    SLIDER_STEPS_DEFAULT,
    SLIDER_GUIDANCE_MIN,
    SLIDER_GUIDANCE_MAX,
    SLIDER_GUIDANCE_STEP,
    SLIDER_GUIDANCE_DEFAULT,
    SLIDER_SAFETY_MIN,
    SLIDER_SAFETY_MAX,
    SLIDER_SAFETY_DEFAULT,
    SLIDER_INTERVAL_MIN,
    SLIDER_INTERVAL_MAX,
    SLIDER_INTERVAL_STEP,
    SLIDER_INTERVAL_DEFAULT
)

# Initial random seed value for the Seed field
initial_seed = ImageGenerator.generate_random_seed()

iface = gr.Interface(
    fn=ImageGenerator.generate_image,
    inputs=[
        gr.Textbox(label="API Token", placeholder="Enter your Replicate API Token", type="password"),
        gr.Dropdown(["black-forest-labs/flux-dev", "black-forest-labs/flux-pro", "black-forest-labs/flux-schnell"],
                    label="Model", value="black-forest-labs/flux-pro"),
        gr.Textbox(label="Prompt", placeholder="Describe the image you want to generate"),
        gr.Number(label="Seed", value=initial_seed),  # Use the generated random seed
        gr.Checkbox(label="Randomize", value=True),
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