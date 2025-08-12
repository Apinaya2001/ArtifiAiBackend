import cv2
import numpy as np
from PIL import Image,ImageEnhance, ImageFilter
import torch
from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan


# def run_postprocessing(input_path, output_path, use_superres=False):
#     # Load image
#     image = cv2.imread(input_path)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#     # Light denoising
#     denoised = cv2.fastNlMeansDenoisingColored(image, None, 5, 5, 7, 21)

#     # Slight vibrance boost (convert to HSV)
#     hsv = cv2.cvtColor(denoised, cv2.COLOR_RGB2HSV).astype(np.float32)
#     hsv[..., 1] *= 1.15  # Increase saturation
#     hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
#     boosted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

#     # Sharpening
#     kernel = np.array([[0, -1, 0],
#                        [-1, 5.2, -1],
#                        [0, -1, 0]])
#     sharpened = cv2.filter2D(boosted, -1, kernel)

#     # Save final image
#     final = Image.fromarray(sharpened)
#     final.save(output_path)

#     # Optional super-resolution
#     if use_superres:
#      upscale_with_realesrgan(image)  # No model_path needed now

def upscale_with_realesrgan(img, scale=2):
    """
    Accepts a PIL.Image and returns a PIL.Image (upscaled).
    Implement with your ESRGAN wrapper; this stub keeps signatures consistent.
    """
    # TODO: replace with your actual ESRGAN integration
    return img  # no-op fallback

def run_postprocessing(img_in: str, img_out: str, use_superres: bool = True):
    """
    Required signature (called by inference.run_inference_with_postprocessing):
        - img_in:  absolute path to RAW stylized image
        - img_out: absolute path where the final enhanced image must be saved
        - use_superres: whether to run ESRGAN
    """
    img = Image.open(img_in).convert("RGB")

    # gentle, style-appropriate tweaks (tune to taste)
    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = img.filter(ImageFilter.MedianFilter(size=3))

    if use_superres:
        try:
            img = upscale_with_realesrgan(img, scale=2)   # <-- pass a single PIL image
        except TypeError:
            # If your existing function expects keyword args only, try this:
            img = upscale_with_realesrgan(img=img, scale=2)

    # must save to the provided output path
    img.save(img_out, quality=92, subsampling=0)