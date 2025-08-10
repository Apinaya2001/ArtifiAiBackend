import cv2
from PIL import Image, ImageEnhance
import numpy as np
import os
from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan


def smooth_vangogh_artifacts(np_img):
    # 1. Median blur to reduce dot noise
    np_img = cv2.medianBlur(np_img, 3)

    # 2. Bilateral filter to smooth colors but preserve edges
    np_img = cv2.bilateralFilter(np_img, d=9, sigmaColor=75, sigmaSpace=75)

    return np_img


def enhance_contrast_and_color(pil_img):
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(1.2)

    enhancer = ImageEnhance.Color(pil_img)
    pil_img = enhancer.enhance(1.1)

    return pil_img


def run_postprocessing(input_path, output_path, use_superres=True):
    img = Image.open(input_path).convert("RGB")
    np_img = np.array(img)

    # Artifact smoothing
    np_img = smooth_vangogh_artifacts(np_img)

    # Convert back to PIL
    img = Image.fromarray(np_img)

    # Auto contrast + color enhancement
    img = enhance_contrast_and_color(img)

    # Optional: Super-resolution upscale
    if use_superres:
        try:
            sr_model_path = os.path.join("styletransfer", "model", "RealESRGAN_x4plus.pth")
            img = upscale_with_realesrgan(img, sr_model_path)
        except Exception as e:
            print(f"[VanGogh Warning] Super-resolution failed: {e}")

    # Save output
    img.save(output_path)
