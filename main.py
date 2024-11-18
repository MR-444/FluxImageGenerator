# main.py
import gradio as gr

from constants import (
    SLIDER_STEPS_MIN, SLIDER_STEPS_MAX, SLIDER_STEPS_DEFAULT,
    SLIDER_GUIDANCE_MIN, SLIDER_GUIDANCE_MAX, SLIDER_GUIDANCE_STEP, SLIDER_GUIDANCE_DEFAULT,
    SLIDER_SAFETY_MIN, SLIDER_SAFETY_MAX, SLIDER_SAFETY_DEFAULT,
    SLIDER_INTERVAL_MIN, SLIDER_INTERVAL_MAX, SLIDER_INTERVAL_STEP, SLIDER_INTERVAL_DEFAULT,
    IMAGE_WIDTH_MIN, IMAGE_WIDTH_MAX, IMAGE_WIDTH_DEFAULT,
    IMAGE_HEIGHT_MIN, IMAGE_HEIGHT_MAX, IMAGE_HEIGHT_DEFAULT,
    SLIDER_OUTPUT_QUALITY_MIN, SLIDER_OUTPUT_QUALITY_MAX, SLIDER_OUTPUT_QUALITY_DEFAULT
)
from image_generator import ImageGenerator

initial_seed = ImageGenerator.generate_random_seed()


def toggle_custom_resolution(ar):
    if ar == "custom":
        return gr.update(visible=True), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False)


with gr.Blocks(
        title="Flux Image Generator",
        theme="default"
) as iface:
    gr.Markdown(
        """
        # Flux Image Generator
        Generate images using various Flux models. Adjust parameters to customize the output.
        """
    )
    with gr.Row():
        with gr.Column():
            api_token = gr.Textbox(label="API Token", placeholder="Enter your Replicate API Token", type="password")
            model = gr.Dropdown(
                ["black-forest-labs/flux-dev", "black-forest-labs/flux-pro", "black-forest-labs/flux-1.1-pro",
                 "black-forest-labs/flux-schnell", "black-forest-labs/flux-1.1-pro-ultra"],
                label="Model", value="black-forest-labs/flux-1.1-pro")
            prompt = gr.Textbox(label="Prompt", placeholder="Describe the image you want to generate")
            seed = gr.Number(label="Seed", value=initial_seed)
            randomize = gr.Checkbox(label="Randomize", value=True)
            steps = gr.Slider(SLIDER_STEPS_MIN, SLIDER_STEPS_MAX, SLIDER_STEPS_DEFAULT, step=1, label="Steps")
            guidance = gr.Slider(SLIDER_GUIDANCE_MIN, SLIDER_GUIDANCE_MAX, SLIDER_GUIDANCE_DEFAULT,
                                 step=SLIDER_GUIDANCE_STEP, label="Guidance")
            aspect_ratio = gr.Dropdown(["1:1", "16:9", "2:3", "3:2", "4:5", "5:4", "9:16", "21:9", "9:21", "3:4", "4:3", "custom"],
                                       label="Aspect Ratio", value="1:1")
            width = gr.Slider(IMAGE_WIDTH_MIN, IMAGE_WIDTH_MAX, IMAGE_WIDTH_DEFAULT, step=16,
                              label="Width (if custom aspect ratio)", visible=False)
            height = gr.Slider(IMAGE_HEIGHT_MIN, IMAGE_HEIGHT_MAX, IMAGE_HEIGHT_DEFAULT, step=16,
                               label="Height (if custom aspect ratio)", visible=False)
            safety_tolerance = gr.Slider(SLIDER_SAFETY_MIN, SLIDER_SAFETY_MAX, SLIDER_SAFETY_DEFAULT, step=1,
                                         label="Safety Tolerance")
            interval = gr.Slider(SLIDER_INTERVAL_MIN, SLIDER_INTERVAL_MAX, SLIDER_INTERVAL_DEFAULT,
                                 step=SLIDER_INTERVAL_STEP, label="Interval")
            raw = gr.Checkbox(label="Raw", value=False)
            output_format = gr.Dropdown(["png", "jpg", "webp"], label="Output Format", value="png")
            output_quality = gr.Slider(SLIDER_OUTPUT_QUALITY_MIN, SLIDER_OUTPUT_QUALITY_MAX,
                                       SLIDER_OUTPUT_QUALITY_DEFAULT, step=1, label="Output Quality")
            prompt_upsampling = gr.Checkbox(label="Prompt Upsampling", value=False)
            current_seed = gr.State(initial_seed)
            generate_button = gr.Button("Generate Image")

        with gr.Column():
            image_output = gr.Image(label="Generated Image")
            status_output = gr.HTML(label="Status")
            gr.Markdown(
                """
                ### Silmas image portfolios
                - [Civitai](https://civitai.com/user/Silmas)
                - [DeviantArt](https://www.deviantart.com/silmasone)
                - [Fotocommunity](https://www.fotocommunity.de/user_photos/1505747)
                """
            )
            gr.Markdown(
                """
                &copy; 2024 Silmas. All rights reserved.
                """
            )

    aspect_ratio.change(
        toggle_custom_resolution,
        inputs=[aspect_ratio],
        outputs=[width, height]
    )

    generate_button.click(
        fn=ImageGenerator.generate_image,
        inputs=[
            api_token, model, prompt, seed, randomize, steps, guidance, aspect_ratio,
            width, height, safety_tolerance, interval, raw, output_format, output_quality, prompt_upsampling
        ],
        outputs=[status_output, image_output, current_seed]
    ).then(
        fn=lambda x: x,
        inputs=[current_seed],
        outputs=[seed]
    )

print("Starting Gradio Interface")
iface.launch()
