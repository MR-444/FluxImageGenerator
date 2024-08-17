import gradio as gr
from image_generator import ImageGenerator
from constants import (
    SLIDER_STEPS_MIN, SLIDER_STEPS_MAX, SLIDER_STEPS_DEFAULT,
    SLIDER_GUIDANCE_MIN, SLIDER_GUIDANCE_MAX, SLIDER_GUIDANCE_STEP, SLIDER_GUIDANCE_DEFAULT,
    SLIDER_SAFETY_MIN, SLIDER_SAFETY_MAX, SLIDER_SAFETY_DEFAULT,
    SLIDER_INTERVAL_MIN, SLIDER_INTERVAL_MAX, SLIDER_INTERVAL_STEP, SLIDER_INTERVAL_DEFAULT
)

initial_seed = ImageGenerator.generate_random_seed()


def wrapped_update_seed(api_token, model, prompt, seed, randomize, steps, guidance, aspect_ratio, safety_tolerance,
                        interval, current_seed):
    status, image, new_seed = ImageGenerator.generate_image(
        api_token, model, prompt, seed, randomize, steps, guidance, aspect_ratio, safety_tolerance, interval
    )
    return status, image, new_seed


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
                ["black-forest-labs/flux-dev", "black-forest-labs/flux-pro", "black-forest-labs/flux-schnell"],
                label="Model", value="black-forest-labs/flux-pro")
            prompt = gr.Textbox(label="Prompt", placeholder="Describe the image you want to generate")
            seed = gr.Number(label="Seed", value=initial_seed)
            randomize = gr.Checkbox(label="Randomize", value=True)
            steps = gr.Slider(SLIDER_STEPS_MIN, SLIDER_STEPS_MAX, SLIDER_STEPS_DEFAULT, step=1, label="Steps")
            guidance = gr.Slider(SLIDER_GUIDANCE_MIN, SLIDER_GUIDANCE_MAX, SLIDER_GUIDANCE_DEFAULT,
                                 step=SLIDER_GUIDANCE_STEP, label="Guidance")
            aspect_ratio = gr.Dropdown(["1:1", "16:9", "2:3", "3:2", "4:5", "5:4", "9:16"], label="Aspect Ratio",
                                       value="1:1")
            safety_tolerance = gr.Slider(SLIDER_SAFETY_MIN, SLIDER_SAFETY_MAX, SLIDER_SAFETY_DEFAULT, step=1,
                                         label="Safety Tolerance")
            interval = gr.Slider(SLIDER_INTERVAL_MIN, SLIDER_INTERVAL_MAX, SLIDER_INTERVAL_DEFAULT,
                                 step=SLIDER_INTERVAL_STEP, label="Interval")
            current_seed = gr.State(initial_seed)

            generate_button = gr.Button("Generate Image")

        with gr.Column():
            image_output = gr.Image(label="Generated Image")
            status_output = gr.HTML(label="Status")

    generate_button.click(
        fn=wrapped_update_seed,
        inputs=[api_token, model, prompt, seed, randomize, steps, guidance, aspect_ratio, safety_tolerance, interval,
                current_seed],
        outputs=[status_output, image_output, current_seed]
    ).then(
        fn=lambda x: x,
        inputs=[current_seed],
        outputs=[seed]
    )

iface.launch()