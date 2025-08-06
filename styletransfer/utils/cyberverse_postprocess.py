# styletransfer/utils/cyberverse_postprocess.py

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import torch

try:
    from realesrgan import RealESRGANer
    realesrgan_available = True
except ImportError:
    realesrgan_available = False

def enhance_colors(img_pil, contrast=1.2, vibrance=1.3):
    img = ImageEnhance.Contrast(img_pil).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(vibrance)
    return img

def smooth_faces_and_reduce_noise(cv2_img):
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    result = cv2_img.copy()
    for (x, y, w, h) in faces:
        face = result[y:y+h, x:x+w]
        blurred = cv2.bilateralFilter(face, 15, 75, 75)
        result[y:y+h, x:x+w] = blurred

    result = cv2.fastNlMeansDenoisingColored(result, None, 5, 5, 7, 21)
    return result

def upscale_with_realesrgan(cv2_img):
    if not realesrgan_available:
        raise ImportError("Real-ESRGAN not installed. Install it: https://github.com/xinntao/Real-ESRGAN")

    from basicsr.archs.rrdbnet_arch import RRDBNet
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
    upsampler = RealESRGANer(
        scale=4,
        model_path=None,
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False
    )
    output, _ = upsampler.enhance(cv2_img, outscale=4)
    return output

def run_postprocessing(input_path, output_path, use_superres=True):
    img_pil = Image.open(input_path).convert("RGB")
    img_pil = enhance_colors(img_pil)

    cv2_img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    cv2_img = smooth_faces_and_reduce_noise(cv2_img)

    if use_superres and realesrgan_available:
        try:
            cv2_img = upscale_with_realesrgan(cv2_img)
        except Exception as e:
            print(f"[Real-ESRGAN warning] Super-resolution failed: {e}")

    result_pil = Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
    result_pil.save(output_path)
