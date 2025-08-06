import cv2
import numpy as np
from PIL import Image
import torch
from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan

def run_postprocessing(input_path, output_path, use_superres=False):
    # Load image
    image = cv2.imread(input_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Light denoising
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 5, 5, 7, 21)

    # Slight vibrance boost (convert to HSV)
    hsv = cv2.cvtColor(denoised, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] *= 1.15  # Increase saturation
    hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
    boosted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    # Sharpening
    kernel = np.array([[0, -1, 0],
                       [-1, 5.2, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(boosted, -1, kernel)

    # Save final image
    final = Image.fromarray(sharpened)
    final.save(output_path)

    # Optional super-resolution
    if use_superres:
     upscale_with_realesrgan(image)  # No model_path needed now
