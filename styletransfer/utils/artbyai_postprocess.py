# import cv2
# import numpy as np
# from PIL import Image
# import torch
# from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan

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
# styletransfer/utils/artbyai_postprocess.py
import cv2
import numpy as np
from PIL import Image

# Try to import ESRGAN helper (function or class)
try:
    from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan as _esr_func
    _ESR_KIND = "func"
except Exception:
    _esr_func = None
    _ESR_KIND = None

try:
    from styletransfer.utils.real_esrgan_upscale import RealESRGANUpscaler as _ESR_CLASS
    _ESR_KIND = "class"
except Exception:
    _ESR_CLASS = None

# Lazy instance if class-based helper exists
_ESR_INSTANCE = _ESR_CLASS() if _ESR_KIND == "class" else None


def _rgb_pil_to_jpg(path, rgb_array):
    Image.fromarray(rgb_array).save(path, format="JPEG", quality=95)


def _maybe_superres(rgb_img, scale=2):
    """Call ESRGAN helper regardless of whether it was exposed as a function or a class method."""
    try:
        if _ESR_KIND == "func" and callable(_esr_func):
            # function signature: (image, scale=2, ...)
            return _esr_func(rgb_img, scale=scale)
        if _ESR_KIND == "class" and _ESR_INSTANCE is not None:
            # method signature: self.upscale_with_realesrgan(image, scale=2, ...)
            return _ESR_INSTANCE.upscale_with_realesrgan(rgb_img, scale=scale)
    except TypeError as e:
        # This is the error you saw: "... takes 1 positional argument but 2 were given"
        print(f"[Real-ESRGAN warning] Signature mismatch: {e}")
    except Exception as e:
        print(f"[Real-ESRGAN warning] Super-resolution failed: {e}")
    return rgb_img


def run_postprocessing(input_path, output_path, use_superres=False):
    # Load BGR -> RGB
    bgr = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    # 1) Light denoising
    denoised = cv2.fastNlMeansDenoisingColored(rgb, None, 5, 5, 7, 21)

    # 2) Vibrance boost (HSV)
    hsv = cv2.cvtColor(denoised, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] *= 1.15  # saturation
    hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
    boosted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    # 3) Gentle sharpen
    kernel = np.array([[0, -1, 0],
                       [-1, 5.2, -1],
                       [0, -1, 0]], dtype=np.float32)
    sharpened = cv2.filter2D(boosted, -1, kernel)

    # 4) Optional super-resolution (on the sharpened result)
    final_rgb = _maybe_superres(sharpened, scale=2) if use_superres else sharpened

    # 5) Save once (final image)
    _rgb_pil_to_jpg(output_path, final_rgb)
