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
    "model": "stable-diffusion-v1",
    "prompt": "A futuristic cityscape with flying cars.",
    "seed": 12345,
    "steps": 50,
    "guidance": 7.5,
    "aspect_ratio": "16:9",
    "safety_tolerance": 3,
    "interval": 1.75
}
```

### Embedding Metadata

The following code snippet shows how metadata is embedded into a PNG image using Python's PIL library:

```python
import io
from PIL import Image, PngImagePlugin

def embed_metadata_in_image(image_data, metadata):
    """Embed metadata into a PNG image stored in memory (image_data)"""
    try:
        # Open the image from the byte data
        image = Image.open(io.BytesIO(image_data))

        # Check if the image is in PNG format
        if image.format != 'PNG':
            raise ValueError('The image format is not PNG.')

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

# Example usage
metadata = json.dumps({
    "model": "stable-diffusion-v1",
    "prompt": "A futuristic cityscape with flying cars.",
    "seed": 12345,
    "steps": 50,
    "guidance": 7.5,
    "aspect_ratio": "16:9",
    "safety_tolerance": 3,
    "interval": 1.75
})

# Assuming img_data is the byte content of the generated image
img_with_metadata = embed_metadata_in_image(img_data, metadata)
