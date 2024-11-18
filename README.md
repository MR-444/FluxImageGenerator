### Program Description: Flux Image Generator

The **Flux Image Generator** is an interactive web application designed to help users generate unique images using the three Flux models. This application requires a Replicate API token, and you will need to cover any associated fees for using the Replicate service. Powered by Gradio, an intuitive Python library for creating interactive UI components, this application allows users to customize parameters and instantly see the results of their image generation requests.

#### Features:

- **Generate Custom Images**: Use different models like `flux-dev`, `flux-pro`, and `flux-schnell` to create a variety of images based on your descriptive prompts.
- **Adjustable Parameters**: Fine-tune your image generation with adjustable parameters such as:
  - **Steps**: Control the number of steps in the image generation process.
  - **Guidance**: Adjust the strength of the adherence to the given prompt.
  - **Aspect Ratio**: Choose from standard aspect ratios like 1:1, 16:9, and more.
  - **Safety Tolerance**: Set the safety levels to filter the content.
  - **Interval**: Modify the interval steps in the generation process.
  - **Seed**: Utilize a specific seed for reproducible results or randomize it for different images.
- **Integrated API Token Management**: Securely manage your API token for authentication with the model service.
- **Instant Feedback**: See the generated image and status updates immediately after clicking the "Generate Image" button.
- **Generated Image Metadata**: All the parameters used for generating the image are saved within the PNG file, allowing for easy reference and reproducibility.
- **Portfolio Links**: Quick links to the image portfolios of the image artist "Silmas" on platforms like Civitai, DeviantArt, and Fotocommunity.

# Installation Guide

## Prerequisites

Before proceeding, ensure you have Python installed on your system.

## Setup

### 1. Create a Virtual Environment (Optional but Recommended)

Creating a virtual environment isolates your project dependencies:

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

Activate the virtual environment based on your operating system:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS and Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Requirements

Install the project dependencies using pip:

```bash
pip install -r requirements.txt
```

This command will install all the packages listed in your `requirements.txt` file.



## Metadata Process and Structure

### Purpose and Process

In this project, metadata is embedded into each generated PNG image. This metadata includes the parameters used for generating the image, allowing for reproducibility and traceability.

The process for embedding metadata is as follows:

1. **Image Acquisition**: An image is generated via an API call.
2. **Open Image**: The generated image is opened from byte data.
3. **Metadata Creation**: Metadata is created as a dictionary and converted to a format suitable for embedding.
4. **Embed Metadata**: The metadata is embedded into the image using the `PngImagePlugin.PngInfo()` method.
5. **Save Image**: The image with the embedded metadata is saved to disk.

### Metadata Schema

The metadata schema defines the structure and content of the metadata embedded in each PNG image. This schema ensures consistency and provides useful information for future reference.

#### Metadata Fields

| Field Name        | Type     | Description                                                    | Constraints                           |
|-------------------|----------|----------------------------------------------------------------|---------------------------------------|
| **model**         | String   | The name or identifier of the machine learning model used.     | Must be a valid model identifier.     |
| **prompt**        | String   | The text prompt describing the desired content of the image.   | Cannot be empty.                      |
| **seed**          | Integer  | The random seed for image generation, useful for reproducibility. | Must be between 0 and `SEED_MAX_VALUE`.|
| **steps**         | Integer  | The number of steps in the generation process.                 | Must be between `SLIDER_STEPS_MIN` and `SLIDER_STEPS_MAX`. |
| **guidance**      | Float    | The guidance scale for image generation.                       | Must be between `SLIDER_GUIDANCE_MIN` and `SLIDER_GUIDANCE_MAX`. |
| **aspect_ratio**  | String   | The aspect ratio of the generated image (e.g., '16:9').        | Must be in the format 'W:H'.          |
| **safety_tolerance** | Integer | The safety tolerance level during generation.                   | Must be between `SLIDER_SAFETY_MIN` and `SLIDER_SAFETY_MAX`. |
| **interval**      | Float    | Interval rate used in the generation process.                  | Must be between `SLIDER_INTERVAL_MIN` and `SLIDER_INTERVAL_MAX`. |

#### Example Metadata

Here’s an example of how the metadata might look for a generated image:

```json
{
  "model": "black-forest-labs/flux-1.1-pro-ultra",
  "prompt": "A blonde woman with long hair stands in profile, wearing white thigh highs, a snug white crop top, and a vibrant red short skirt that complements her red baseball cap.",
  "seed": 2344559566,
  "steps": 25,
  "guidance": 3.0,
  "aspect_ratio": "2:3",
  "width": 512,
  "height": 512,
  "safety_tolerance": 2,
  "interval": 2.0,
  "raw": true,
  "output_format": "png",
  "output_quality": 80,
  "prompt_upsampling": false
}


```

